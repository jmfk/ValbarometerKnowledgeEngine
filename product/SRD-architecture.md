# SRD - System Requirements & Architecture

Referensdokument: [MVP1.md](../product/MVP1.md)

## 1. Övergripande Arkitektur
Systemet är uppbyggt som en datamotor för politisk analys med fokus på transparens och evidens.

### Komponenter
- **Orchestration**: Dagster för schemaläggning, beroenden, retry och monitorering.
- **Ingestion Layer**: Python-baserade workers för att hämta data från Riksdagens API och partiers webbplatser. Idempotent via `source_external_id` upsert.
- **Storage Layer**: PostgreSQL med `pgvector` för strukturerad data och embeddings. S3 för rådokument (JSON/PDF/HTML).
- **Processing Pipeline**: Tvåstegs-pipeline — billig klassificering (GPT-4o-mini) följt av strukturerad extraction (Gemini 2.5 Flash).
- **API Layer**: FastAPI för att servera entiteter, claims, voteringar och jämförelser.

## 2. Datamodell (High-Level)
- **Entities**: Partier, politiker och organisationer. Politiker kopplas till parti via `politician_affiliations` (med tidsperiod).
- **Documents & Document Entities**: Källdokument med many-to-many-koppling till entiteter (author, signatory, etc.).
- **Chunks**: Textsegment med vektorer (1536 dim) och `token_count`.
- **Topics**: Hierarkisk kategorisering av politiska sakfrågor.
- **Claims & Evidence**: Extraherade ståndpunkter med `valid_from/valid_to`, kopplade till textsegment. Multi-topic via `claim_topics`.
- **Votes**: Röstningsresultat per ledamot, kopplade till dokument via `votes.document_id`.

## 3. Teknisk Stack
- **Språk**: Python 3.11+
- **Databas**: PostgreSQL (Linode, Docker) + pgvector
- **Migrationer**: Alembic (SQLAlchemy)
- **AI/NLP**: OpenAI (text-embedding-3-small, 1536 dim), Gemini 2.5 Flash för extraktion/classification.
- **API**: FastAPI
- **Storage**: Lokal disk / S3-kompatibel (bestäms vid deploy)
- **Orchestrering**: Dagster
- **Observabilitet**: structlog + Prometheus metrics
