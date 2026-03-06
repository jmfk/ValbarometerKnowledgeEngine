# Step 2: Ingestion - Party Documents

Referens: [MVP1.md](../MVP1.md) (Phase 2)

## Mål
Samla in officiella dokument från de 8 riksdagspartierna för att identifiera deras uttalade ståndpunkter.

## Funktionella krav
1. **Källor**: Partiprogram, stämmobeslut och policy-dokument.
2. **Pressmeddelanden**: Hämta pressmeddelanden via RSS-feeds och HTML-scraping från partiernas webbplatser. Spara med `document_type='press_release'`.
3. **Format**: Hantera PDF-extraktion och HTML-scraping.
4. **Mapping**: Koppla dokument till rätt `entity_id` (parti).

## Tekniska steg
- Skapa en lista på start-URL:er för varje partis dokumentarkiv.
- Kartlägg RSS-feeds för pressmeddelanden per parti.
- Implementera RSS-parser som hämtar och sparar nya pressmeddelanden inkrementellt.
- Implementera PDF-to-text pipeline (t.ex. `PyMuPDF` eller `unstructured`).
- Spara dokument i `documents`-tabellen med `document_type='party_program'`, `'press_release'` etc.
