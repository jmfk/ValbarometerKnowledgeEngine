# Step 3: Processing Pipeline - Chunking & Embeddings

Referens: [MVP1.md](../MVP1.md) (Systemarkitektur)

## Mål
Transformera råtext till sökbara vektorer för att möjliggöra evidensbaserad sökning.

## MVP-scope

### Funktionella krav
1. **Chunking**: Section-based chunking som respekterar rubriknivåer. Fallback till ~500 tokens för ostrukturerad text.
2. **Embeddings**: Generera vektorer med `text-embedding-3-small` (1536 dim).
3. **Indexering**: Spara i `document_chunks` med `pgvector`.
4. **Topic classification**: Klassificera varje chunk mot topic-taxonomin (Gemini 2.5 Flash). Spara via `chunk_topics` junction-tabell.

### Kostnadskontroll

1. **Embedding-cache**: Beräkna hash av `chunk_text` -- kör inte embedding om hash redan finns i `document_chunks`.
2. **Batch-embedding**: OpenAI embeddings-API stödjer batch (max 2048 inputs). Skicka chunks i batchar om 100.
3. **Topic classification batching**: Skicka 10-20 chunks per Gemini-anrop.
4. **Skip-logik**: Chunks under 50 tokens eller ren metadata skippas.

### Tekniska steg
- Implementera `ChunkingService` med section-based splitter.
- Integrera med OpenAI API för embeddings (`text-embedding-3-small`) med batch-support.
- Skapa HNSW-index i Postgres för snabb likhetssökning.
- Implementera topic classification-steg (Gemini 2.5 Flash) som matchar mot `topics`-tabellen.
- Implementera skip-logik och embedding-cache.

### Observabilitet

- **Logging**: `structlog` -- logga varje steg (chunking, embedding, topic classification) med document_id, chunk_count, duration.
- **Metrics**:
  - `pipeline_chunks_created_total{document_type}`
  - `pipeline_embeddings_generated_total`
  - `pipeline_topics_classified_total{topic}`
  - `pipeline_llm_tokens_used_total{model, step}`
  - `pipeline_errors_total{step, error_type}`
- **Alerting**: Embedding-API-fel eller topic classification timeout → logga error + retry.

## Deferred (post-MVP)

- **Deduplication**: Cosine similarity-baserad dedup av chunks/claims.
- **BM25 / Full-text search**: `tsvector` + GIN-index med svensk text search config.
- Hybrid retrieval (BM25 + vector merge).
