# Step 4: Knowledge Extraction - Claims & Evidence

Referens: [MVP1.md](../MVP1.md) (Kärnfunktion 1 & 4)

## Mål
Extrahera strukturerade påståenden (claims) och koppla dem till textbevis (evidence).

## MVP-scope

### Funktionella krav
1. **Claim Extraction**: Identifiera (Subject, Topics[], Stance) från textchunks med Gemini 2.5 Flash. Topics sparas via `claim_topics` junction-tabell.
2. **Evidence Mapping**: Spara exakta citat och referenser till `document_chunks` via `claim_evidence`.
3. **Confidence Scoring**: LLM sätter initial confidence. Notera: LLM-genererad confidence är **okalibrerad** — använd `review_status` som primär kvalitetsindikator. `confidence`-fältet används för att prioritera admin-review (lägst confidence granskas först), inte som sannolikhetsmått mot användare.
4. **Golden Set Validation**: Validera extraction-kvalitet mot golden set innan full körning. Se [06-golden-set-validation.md](06-golden-set-validation.md).

### Tvåstegs-extraction

Se [07-volume-estimate.md](07-volume-estimate.md) för fullständig kostnadsberäkning.

Naiv extraction (LLM på alla ~558 000 chunks) kostar ~$2 500. Tvåstegsmodellen reducerar till ~$317 (87% besparing).

**Steg 1 — Claim-relevansklassificering (billig modell)**

Modell: GPT-4o-mini (eller Gemini 2.0 Flash).

Prompt returnerar enbart `{"has_claim": true/false}` per chunk. Filtrerar bort:
- Procedurell text (hänvisningar till lagrum, ärendenummer)
- Innehållsförteckningar och metadata
- Rent deskriptiv text utan ståndpunkt

Estimat: ~20% av chunks passerar filtret (~112 000 av 558 000).

**Steg 2 — Strukturerad claim extraction (kapabel modell)**

Modell: Gemini 2.5 Flash (primärt) eller GPT-4o (fallback).

Körs enbart på chunks som passerade steg 1. Extraherar fullständig JSON:

```json
{
  "claims": [
    {
      "subject": "Moderaterna",
      "topics": ["energy", "climate"],
      "stance": "support",
      "claim_text": "Moderaterna vill bygga ut kärnkraften",
      "evidence_quote": "Sverige behöver fler kärnkraftsreaktorer...",
      "confidence": 0.91
    }
  ]
}
```

### Ytterligare kostnadskontroll

1. **Batching**: Skicka 5–10 chunks per LLM-anrop med tydlig JSON-array-prompt. Minskar overhead per chunk.
2. **Caching**: Spara `extraction_model` och `extraction_prompt_version` på varje claim. Kör inte om extraction på chunks som redan processats med samma modell+prompt.
3. **Skip-logik**: Chunks under 50 tokens eller med enbart metadata (datum, sidhuvud) skippas automatiskt innan steg 1.
4. **Batch API**: Använd OpenAI Batch API (50% rabatt, 24h latens) för initial bulk-laddning. Real-time API för dagliga inkrementella körningar.
5. **Dry-run**: Stöd för `--dry-run` som estimerar token-kostnad utan att anropa LLM.
6. **Token-budget**: Konfigurerbart max antal tokens per körning. Pipeline pausar vid budget-gräns.

### valid_from / valid_to heuristik

- `valid_from` = dokumentets `published_at`.
- `valid_to` = `NULL` (pågående).
- Vid ny claim med samma `(subject_entity_id, topic, stance)`: behåll båda (olika evidens).
- Vid ny claim med samma `(subject_entity_id, topic)` men annan `stance`: sätt `valid_to` på äldre claim till `published_at` för nya dokumentet. Flagga med `review_status = 'pending'`.

### Tekniska steg
- Designa prompt för strukturerad extraktion (JSON-output med multi-topic stöd).
- Implementera worker som processar chunks och sparar i `claims`, `claim_topics` och `claim_evidence`.
- Implementera skip-logik och batching-strategi.
- Hantera `valid_from` och `valid_to` enligt heuristik ovan.

### Observabilitet

- **Logging**: `structlog` -- logga varje extraction-batch med chunk_ids, claims_found, skipped_count, duration, token_usage.
- **Metrics**:
  - `extraction_claims_created_total{stance, review_status}`
  - `extraction_chunks_processed_total`
  - `extraction_chunks_skipped_total{reason}`
  - `extraction_llm_tokens_used_total{model}`
  - `extraction_confidence_histogram` (histogram av confidence-scores för kalibrering)
- **Alerting**: Hög andel `confidence < 0.5` → flagga för prompt-review.

## Deferred (post-MVP)

- **Politician Issue Ownership**: `politician_issue_score` per politiker och topic.
- **Topic Taxonomy Management**: Dynamisk utökning av taxonomin med sub-topics, admin-godkännande.
