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

### Tekniska steg
- Implementera `ChunkingService` med section-based splitter.
- Integrera med OpenAI API för embeddings (`text-embedding-3-small`).
- Skapa HNSW-index i Postgres för snabb likhetssökning.
- Implementera topic classification-steg (Gemini 2.5 Flash) som matchar mot `topics`-tabellen.

## Deferred (post-MVP)

- **Deduplication**: Cosine similarity-baserad dedup av chunks/claims.
- **BM25 / Full-text search**: `tsvector` + GIN-index med svensk text search config.
- Hybrid retrieval (BM25 + vector merge).
