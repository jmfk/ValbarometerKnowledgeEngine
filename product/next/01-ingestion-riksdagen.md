# Step 1: Ingestion - Riksdagen API

Referens: [MVP1.md](../MVP1.md) (Phase 1)

## Mål
Hämta rådata från Riksdagens öppna data för att bygga grunden i kunskapsbasen.

## Funktionella krav
1. **Motioner**: Hämta alla motioner för innevarande och föregående mandatperiod.
2. **Voteringar**: Hämta röstningsresultat per parti och individ.
3. **Anföranden**: Hämta protokollförda anföranden i kammaren.
4. **Metadata**: Spara käll-URL, datum och dokument-ID för spårbarhet.

## Tekniska steg
- Implementera `RiksdagenClient` i Python.
- Skapa schema för `documents` och `votes` i PostgreSQL.
- Bygga en crawler som hanterar paginering och rate-limiting från Riksdagen.
- Lagra rå-XML/HTML i S3 och metadata i Postgres.
