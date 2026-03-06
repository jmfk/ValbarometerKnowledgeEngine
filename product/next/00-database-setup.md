# Step 0: Database Schema, Migrations & Storage

Referens: [MVP1.md](../MVP1.md) (Datamodell, Storage)

## Mål
Etablera fullständigt databasschema, seed data och objektlagring innan ingestion börjar.

## PostgreSQL Extensions

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

## Schema

### entities

| field      | type                                          | constraint  |
| ---------- | --------------------------------------------- | ----------- |
| id         | uuid                                          | PK, default |
| type       | enum('party', 'politician', 'organization')   | NOT NULL    |
| name       | text                                          | NOT NULL    |
| aliases    | jsonb                                         | DEFAULT '[]' |
| created_at | timestamptz                                   | DEFAULT now |

### documents

| field         | type                                                                                                          | constraint  |
| ------------- | ------------------------------------------------------------------------------------------------------------- | ----------- |
| id            | uuid                                                                                                          | PK, default |
| source_id     | uuid                                                                                                          | FK entities |
| title         | text                                                                                                          | NOT NULL    |
| body          | text                                                                                                          |             |
| document_type | enum('motion', 'proposition', 'party_program', 'congress_decision', 'speech', 'press_release', 'policy_paper') | NOT NULL    |
| published_at  | timestamptz                                                                                                   |             |
| metadata      | jsonb                                                                                                         | DEFAULT '{}' |
| raw_storage_key | text                                                                                                        |             |
| created_at    | timestamptz                                                                                                   | DEFAULT now |

`raw_storage_key` pekar på originaldokumentet i S3.

### document_chunks

| field       | type        | constraint   |
| ----------- | ----------- | ------------ |
| id          | uuid        | PK, default  |
| document_id | uuid        | FK documents |
| chunk_text  | text        | NOT NULL     |
| embedding   | vector(3072)| NULL         |
| chunk_index | int         | NOT NULL     |
| tsv         | tsvector    | GENERATED    |

`tsv` genereras från `chunk_text` för BM25/full-text search.
`embedding` dimensioner matchar `text-embedding-3-large` (3072).

Index:
```sql
CREATE INDEX idx_chunks_embedding ON document_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_chunks_tsv ON document_chunks USING gin (tsv);
CREATE INDEX idx_chunks_document ON document_chunks (document_id);
```

### topics

| field        | type | constraint |
| ------------ | ---- | ---------- |
| id           | uuid | PK, default|
| name         | text | NOT NULL, UNIQUE |
| parent_topic | uuid | FK topics, NULL |

### claims

| field             | type                                          | constraint   |
| ----------------- | --------------------------------------------- | ------------ |
| id                | uuid                                          | PK, default  |
| subject_entity_id | uuid                                          | FK entities  |
| topic_id          | uuid                                          | FK topics    |
| claim_text        | text                                          | NOT NULL     |
| stance            | enum('support', 'oppose', 'unclear', 'mixed') | NOT NULL     |
| confidence        | float                                         |              |
| valid_from        | date                                          |              |
| valid_to          | date                                          |              |
| review_status     | enum('pending', 'approved', 'rejected')       | DEFAULT 'pending' |
| created_at        | timestamptz                                   | DEFAULT now  |

`valid_from` / `valid_to` möjliggör policy drift detection.
`review_status` stödjer admin review workflow.

### claim_evidence

| field    | type  | constraint    |
| -------- | ----- | ------------- |
| id       | uuid  | PK, default   |
| claim_id | uuid  | FK claims     |
| chunk_id | uuid  | FK document_chunks |
| quote    | text  | NOT NULL      |
| score    | float |               |

### votes

| field           | type | constraint |
| --------------- | ---- | ---------- |
| id              | uuid | PK, default|
| riksdag_vote_id | text | UNIQUE     |
| title           | text | NOT NULL   |
| date            | date | NOT NULL   |
| topic_id        | uuid | FK topics, NULL |

### vote_positions

| field     | type                              | constraint  |
| --------- | --------------------------------- | ----------- |
| id        | uuid                              | PK, default |
| vote_id   | uuid                              | FK votes    |
| entity_id | uuid                              | FK entities |
| position  | enum('yes', 'no', 'abstain', 'absent') | NOT NULL |

Composite unique constraint: `(vote_id, entity_id)`.

## Migrationsordning

1. Extensions (`pgvector`, `pg_trgm`, `pgcrypto`)
2. Enum types
3. `entities`
4. `documents` (FK → entities)
5. `document_chunks` (FK → documents) + index
6. `topics`
7. `claims` (FK → entities, topics)
8. `claim_evidence` (FK → claims, document_chunks)
9. `votes` (FK → topics)
10. `vote_positions` (FK → votes, entities)

## Seed data: Riksdagspartier

```json
[
  { "type": "party", "name": "Socialdemokraterna", "aliases": ["S", "Socialdemokraterna", "socialdemokraterna"] },
  { "type": "party", "name": "Moderaterna", "aliases": ["M", "Moderaterna", "moderaterna", "Nya Moderaterna"] },
  { "type": "party", "name": "Sverigedemokraterna", "aliases": ["SD", "Sverigedemokraterna", "sverigedemokraterna"] },
  { "type": "party", "name": "Centerpartiet", "aliases": ["C", "Centerpartiet", "centerpartiet"] },
  { "type": "party", "name": "Vänsterpartiet", "aliases": ["V", "Vänsterpartiet", "vänsterpartiet"] },
  { "type": "party", "name": "Kristdemokraterna", "aliases": ["KD", "Kristdemokraterna", "kristdemokraterna"] },
  { "type": "party", "name": "Liberalerna", "aliases": ["L", "Liberalerna", "liberalerna", "Folkpartiet"] },
  { "type": "party", "name": "Miljöpartiet", "aliases": ["MP", "Miljöpartiet", "miljöpartiet", "Miljöpartiet de gröna"] }
]
```

## Seed data: Topics

```json
[
  { "name": "migration" },
  { "name": "energy" },
  { "name": "defense" },
  { "name": "taxation" },
  { "name": "education" },
  { "name": "climate" },
  { "name": "healthcare" },
  { "name": "crime" },
  { "name": "economy" },
  { "name": "labor" },
  { "name": "housing" },
  { "name": "foreign_policy" }
]
```

Taxonomin är hierarkisk (`parent_topic`). Sub-topics läggs till efter initial claim extraction avslöjar vilka som behövs.

## Objektlagring (S3/R2)

Bucket: `valbarometer-raw`

Nyckelstruktur:
```
riksdagen/motioner/{year}/{doc_id}.xml
riksdagen/propositioner/{year}/{doc_id}.xml
riksdagen/anforanden/{year}/{doc_id}.xml
riksdagen/voteringar/{year}/{vote_id}.json
parties/{party_slug}/programs/{filename}.pdf
parties/{party_slug}/congress/{filename}.pdf
parties/{party_slug}/press/{filename}.html
```

Alla ingestion workers sätter `raw_storage_key` i `documents`-tabellen vid lagring.
