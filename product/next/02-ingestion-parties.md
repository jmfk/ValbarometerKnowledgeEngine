# Step 2: Ingestion - Party Documents

Referens: [MVP1.md](../MVP1.md) (Phase 2)

## Mål
Samla in officiella dokument från de 8 riksdagspartierna för att identifiera deras uttalade ståndpunkter.

## Funktionella krav
1. **Källor**: Partiprogram, stämmobeslut och policy-dokument.
2. **Pressmeddelanden**: Hämta pressmeddelanden via RSS-feeds och HTML-scraping från partiernas webbplatser. Spara med `document_type='press_release'`.
3. **Format**: Hantera PDF-extraktion och HTML-scraping.
4. **Mapping**: Koppla dokument till rätt entitet (parti) via `document_entities` med `role='source'`.

## Idempotens & felhantering

### Unika nycklar
- `documents.source_external_id`: Genereras som `{party_slug}:{document_type}:{url_hash}` för scrape-baserade dokument.
- Alla inserts använder `INSERT ... ON CONFLICT (source_external_id) DO UPDATE`.

### Inkrementell hämtning
- RSS-feeds: Spara `last_fetched_at` i `ingestion_state` per parti. Hämta enbart nya entries.
- Scraping: Jämför URL-lista mot befintliga `source_url` i `documents`. Enbart nya URL:er processas.
- PDF-filer (partiprogram): Manuell trigger — partiprogram uppdateras sällan (~1 gång per mandatperiod).

### Data quality checks
- Extraherad text < 100 tecken → flagga som `quality_warning` i metadata.
- Encoding-validering: Verifiera UTF-8. Fallback till charset-detection (`chardet`).
- Tomma PDF-sidor (skannat dokument utan OCR) → logga warning, försök med `pytesseract` som fallback.

### Skörhet-mitigering
- Varje parti-scraper har en `selectors.json`-konfiguration med CSS-selectors. När selectors ger 0 resultat → alert.
- Testa scrapers veckovis via smoke test: hämta 1 sida per parti, validera att titel + brödtext extraheras.
- Versionera `selectors.json` i git — ändringar i selectors kräver review.

### Retry & rate limiting
- Exponential backoff (base 2s, max 60s, 3 retries).
- Respektera `robots.txt` och `Crawl-delay`.
- Max 1 request/2s per domän.

## Tekniska steg
- Skapa en lista på start-URL:er för varje partis dokumentarkiv.
- Kartlägg RSS-feeds för pressmeddelanden per parti.
- Implementera RSS-parser som hämtar och sparar nya pressmeddelanden inkrementellt.
- Implementera PDF-to-text pipeline (`PyMuPDF` primärt, `pytesseract` som OCR-fallback).
- Spara dokument i `documents`-tabellen med `document_type='party_program'`, `'press_release'` etc.
- Skapa `document_entities`-koppling med `role='source'` till rätt parti-entitet.
