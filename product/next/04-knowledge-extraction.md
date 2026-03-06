# Step 4: Knowledge Extraction - Claims & Evidence

Referens: [MVP1.md](../MVP1.md) (Kärnfunktion 1 & 4)

## Mål
Extrahera strukturerade påståenden (claims) och koppla dem till textbevis (evidence).

## Funktionella krav
1. **Claim Extraction**: Identifiera (Subject, Topic, Stance) från textchunks.
2. **Evidence Mapping**: Spara exakta citat och referenser till `document_chunks`.
3. **Confidence Scoring**: Låta LLM bedöma säkerheten i extraktionen.

## Tekniska steg
- Designa prompt för strukturerad extraktion (JSON-output).
- Implementera worker som processar chunks och sparar i `claims` och `claim_evidence`.
- Hantera `valid_from` och `valid_to` baserat på dokumentets publiceringsdatum.
