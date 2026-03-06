# Step 3: Processing Pipeline - Chunking & Embeddings

Referens: [MVP1.md](../MVP1.md) (Systemarkitektur)

## Mål
Transformera råtext till sökbara vektorer för att möjliggöra evidensbaserad sökning.

## Funktionella krav
1. **Chunking**: Dela upp dokument i segment om ca 500 tokens med överlapp.
2. **Embeddings**: Generera vektorer med `text-embedding-3-large`.
3. **Indexering**: Spara i `document_chunks` med `pgvector`.

## Tekniska steg
- Implementera `ChunkingService` med `langchain` eller `llama-index`.
- Integrera med OpenAI API för embeddings.
- Skapa HNSW-index i Postgres för snabb likhetssökning.
