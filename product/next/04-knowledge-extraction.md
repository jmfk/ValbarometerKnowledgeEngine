# Step 4: Knowledge Extraction - Claims & Evidence

Referens: [MVP1.md](../MVP1.md) (Kärnfunktion 1 & 4)

## Mål
Extrahera strukturerade påståenden (claims) och koppla dem till textbevis (evidence).

## MVP-scope

### Funktionella krav
1. **Claim Extraction**: Identifiera (Subject, Topics[], Stance) från textchunks med Gemini 2.5 Flash. Topics sparas via `claim_topics` junction-tabell.
2. **Evidence Mapping**: Spara exakta citat och referenser till `document_chunks` via `claim_evidence`.
3. **Confidence Scoring**: Låta LLM bedöma säkerheten i extraktionen.
4. **Golden Set Validation**: Validera extraction-kvalitet mot golden set innan full körning. Se [06-golden-set-validation.md](06-golden-set-validation.md).

### Tekniska steg
- Designa prompt för strukturerad extraktion (JSON-output med multi-topic stöd).
- Implementera worker som processar chunks och sparar i `claims`, `claim_topics` och `claim_evidence`.
- Hantera `valid_from` och `valid_to` baserat på dokumentets publiceringsdatum.

## Deferred (post-MVP)

- **Politician Issue Ownership**: `politician_issue_score` per politiker och topic.
- **Topic Taxonomy Management**: Dynamisk utökning av taxonomin med sub-topics, admin-godkännande.
