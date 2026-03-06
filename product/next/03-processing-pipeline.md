# Step 3: Processing Pipeline - Chunking & Embeddings

Referens: [MVP1.md](../MVP1.md) (Systemarkitektur)

## Mål
Transformera råtext till sökbara vektorer för att möjliggöra evidensbaserad sökning.

## MVP-scope

### Funktionella krav
1. **Chunking**: Section-based chunking som respekterar rubriknivåer. Fallback till ~500 tokens med 50 token overlap för ostrukturerad text. Spara `token_count` per chunk.
2. **Embeddings**: Generera vektorer med `text-embedding-3-small` (1536 dim).
3. **Indexering**: Spara i `document_chunks` med `pgvector`. HNSW-index med `m=24, ef_construction=128`.
4. **Topic classification**: Klassificera varje chunk mot topic-taxonomin (Gemini 2.5 Flash). Spara via `chunk_topics` junction-tabell.

### Embeddingmodell — val och motivering

**Valt: `text-embedding-3-small` (1536 dim)** framför `text-embedding-3-large` (3072 dim).

| Aspekt | small (1536) | large (3072) |
|--------|-------------|--------------|
| Pris/1M tokens | $0.02 | $0.13 |
| Total embedding-kostnad (256M tok) | ~$5 | ~$33 |
| Vektorlagring (558k chunks) | ~3.2 GB | ~6.4 GB |
| HNSW-index storlek (~2x) | ~6.4 GB | ~12.8 GB |
| MTEB retrieval benchmark | 62.3 | 64.6 |

Skillnaden i retrieval-kvalitet (2.3 poäng MTEB) motiverar inte fördubblad lagring och indexstorlek. Kostnaden är försumbar för båda — lagring och sökprestanda är de avgörande faktorerna.

Om retrieval-kvaliteten visar sig otillräcklig vid golden set-validering (se [06-golden-set-validation.md](06-golden-set-validation.md)), kan modellen bytas till `text-embedding-3-large` utan schemaändring (enbart `vector(1536)` → `vector(3072)` migration + re-embedding).

### HNSW-indexparametrar

```sql
CREATE INDEX idx_chunks_embedding ON document_chunks
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 24, ef_construction = 128);
```

- `m=24` (default 16): Fler grannar per nod → bättre recall vid ~558k vektorer.
- `ef_construction=128` (default 64): Mer arbete vid indexbygge → bättre grafkvalitet.
- Runtime: Sätt `SET hnsw.ef_search = 100` (default 40) vid sökningar för att balansera recall vs latens.

Dessa parametrar ger ~99% recall@10 vid denna datavolym. Kan sänkas om söklatens blir ett problem.

### Kostnadskontroll

1. **Embedding-cache**: Beräkna hash av `chunk_text` -- kör inte embedding om hash redan finns i `document_chunks`.
2. **Batch-embedding**: OpenAI embeddings-API stödjer batch (max 2048 inputs). Skicka chunks i batchar om 100.
3. **Topic classification batching**: Skicka 10-20 chunks per Gemini-anrop.
4. **Skip-logik**: Chunks under 50 tokens eller ren metadata skippas.

### Chunking-specifikation

| Dokumenttyp | Strategi | Anledning |
|-------------|----------|-----------|
| Motioner | Section-based (rubriknivå) | Har tydlig rubrikstruktur (Förslag, Motivering) |
| Propositioner | Section-based (rubriknivå) | Lång text med kapitelstruktur |
| Anföranden | Hela som en chunk om < 500 tok, annars paragraf-split | Korta texter, vanligtvis 200–1500 tokens |
| Partiprogram | Section-based (rubriknivå) | Kapitelindelade |
| Pressmeddelanden | Hela som en chunk om < 500 tok | Vanligtvis korta |

Överlapp: 50 tokens mellan chunks (undviker att meningar klipps mitt i).
Svensk tokenizer: Använd `tiktoken` med `cl100k_base` (OpenAI-kompatibel) för token-räkning.

### Tekniska steg
- Implementera `ChunkingService` med section-based splitter och dokumenttypsspecifik konfiguration.
- Integrera med OpenAI API för embeddings (`text-embedding-3-small`) med batch-support.
- Skapa HNSW-index i Postgres med `m=24, ef_construction=128`.
- Implementera topic classification-steg (Gemini 2.5 Flash) som matchar mot `topics`-tabellen.
- Implementera skip-logik och embedding-cache.
- Spara `token_count` per chunk för volymspårning och validering.

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
