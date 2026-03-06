# Step 4: Knowledge Extraction - Claims & Evidence

Referens: [MVP1.md](../MVP1.md) (Kärnfunktion 1 & 4)

## Mål
Extrahera strukturerade påståenden (claims) och koppla dem till textbevis (evidence).

## Funktionella krav
1. **Claim Extraction**: Identifiera (Subject, Topic, Stance) från textchunks.
2. **Evidence Mapping**: Spara exakta citat och referenser till `document_chunks`.
3. **Confidence Scoring**: Låta LLM bedöma säkerheten i extraktionen.
4. **Politician Issue Ownership**: Beräkna `politician_issue_score` per politiker och topic. Baseras på antal motioner, anföranden, citat och dokumentfrekvens kopplat till en sakfråga. Exponeras via API.
5. **Topic Taxonomy Management**: Seeda initiala topics från `00-database-setup.md`. Utöka taxonomin med sub-topics (`parent_topic`) baserat på mönster som framträder under claim extraction. Stöd för manuell justering via admin.

## Tekniska steg
- Designa prompt för strukturerad extraktion (JSON-output).
- Implementera worker som processar chunks och sparar i `claims` och `claim_evidence`.
- Hantera `valid_from` och `valid_to` baserat på dokumentets publiceringsdatum.
- Bygga aggregeringslogik för `politician_issue_score`: räkna dokument per politiker per topic, vikta efter dokumenttyp (motion > anförande > citat).
- Implementera topic taxonomy review-flöde: nya topics som upptäcks under extraction föreslås till admin för godkännande.
