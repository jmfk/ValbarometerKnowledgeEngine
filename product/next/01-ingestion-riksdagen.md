# Step 1: Ingestion - Riksdagen API

Referens: [MVP1.md](../MVP1.md) (Phase 1)

## Mål
Hämta rådata från Riksdagens öppna data för att bygga grunden i kunskapsbasen.

## Funktionella krav
1. **Motioner**: Hämta alla motioner för innevarande och föregående mandatperiod.
2. **Propositioner**: Hämta propositioner via Riksdagens API. Spara med `document_type='proposition'`.
3. **Voteringar**: Hämta röstningsresultat per parti och individ.
4. **Anföranden**: Hämta protokollförda anföranden i kammaren.
5. **Metadata**: Spara käll-URL, datum och dokument-ID för spårbarhet.

## Idempotens & felhantering

### Unika nycklar
- `documents.source_external_id`: Sätts till Riksdagens dok-ID (t.ex. `H5021234`). UNIQUE constraint möjliggör upsert.
- `votes.riksdag_vote_id`: UNIQUE (redan i schemat).
- `vote_positions`: Composite unique `(vote_id, politician_id)` (redan i schemat).

### Upsert-semantik
Alla inserts använder `INSERT ... ON CONFLICT (source_external_id) DO UPDATE` för att säkert kunna köra om ingestion utan dubbletter.

### Inkrementell hämtning
- Spara `last_fetched_at` per dokumenttyp i en `ingestion_state`-tabell eller config.
- Vid varje körning: hämta enbart dokument med `published_at > last_fetched_at`.
- Initial import (backfill) körs en gång med `last_fetched_at = NULL`.

### Retry & rate limiting
- Exponential backoff med jitter (base 2s, max 60s, 3 retries).
- Per-request timeout: 30s.
- Batch-storlek: 100 dokument per API-anrop.
- Spara ingestion-status per batch: `started`, `completed`, `failed`.

## Observabilitet

- **Logging**: `structlog` med JSON-format. Logga varje batch: source, document_type, count, duration, errors.
- **Metrics**: Exponera counters via Prometheus-kompatibelt format:
  - `ingestion_documents_total{source, document_type, status}`
  - `ingestion_errors_total{source, error_type}`
  - `ingestion_duration_seconds{source, document_type}`
- **Health check**: Scraper som returnerar 0 dokument vid schemalagd körning → logga warning + alert.

## Tekniska steg
- Implementera `RiksdagenClient` i Python med retry-decorator och session-hantering.
- Skapa schema för `documents` och `votes` i PostgreSQL.
- Bygga en crawler som hanterar paginering och rate-limiting från Riksdagen.
- Lagra rådata i S3 (JSON-format primärt, XML som fallback) och metadata i Postgres.
- Skapa `document_entities`-kopplingar: motioner → ledamöter (role='author'/'signatory'), propositioner → entitet för regeringen/departement, anföranden → talaren.
- Koppla voteringar till propositioner/motioner via `votes.document_id`.
- Implementera `ingestion_state`-tabell för checkpointing.
- Konfigurera `structlog` med JSON-output och Prometheus counters.
