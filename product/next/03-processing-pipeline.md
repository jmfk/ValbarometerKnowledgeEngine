# Step 3: Processing Pipeline - Chunking & Embeddings

Referens: [MVP1.md](../MVP1.md) (Systemarkitektur)

## Mål
Transformera råtext till sökbara vektorer för att möjliggöra evidensbaserad sökning.

## Funktionella krav
1. **Chunking**: Dela upp dokument i segment om ca 500 tokens med överlapp.
2. **Embeddings**: Generera vektorer med `text-embedding-3-large`.
3. **Indexering**: Spara i `document_chunks` med `pgvector`.
4. **Topic classification**: Klassificera varje chunk mot topic-taxonomin (LLM eller finetuned classifier). Spara `topic_id`-koppling.
5. **Deduplication**: Identifiera och markera semantiskt duplicerade chunks/claims. Använd embedding-likhet (cosine similarity > tröskel) för att flagga dubbletter.
6. **BM25 / Full-text search**: Generera `tsvector` per chunk för Postgres full-text search. Konfigureras med svensk text search config (`swedish`).

## Tekniska steg
- Implementera `ChunkingService` med `langchain` eller `llama-index`.
- Integrera med OpenAI API för embeddings.
- Skapa HNSW-index i Postgres för snabb likhetssökning.
- Implementera topic classification-steg som körs efter embedding, med LLM-prompt som matchar mot `topics`-tabellen.
- Bygga deduplication-logik som jämför nya chunks mot befintliga via cosine similarity.
- Konfigurera `tsvector`-kolumn (generated) på `document_chunks` och skapa GIN-index för BM25-sökning.
