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

### politician_affiliations

Kopplar politiker till parti med tidsperiod (hanterar partibyten).

| field         | type | constraint            |
| ------------- | ---- | --------------------- |
| id            | uuid | PK, default           |
| politician_id | uuid | FK entities, NOT NULL |
| party_id      | uuid | FK entities, NOT NULL |
| from_date     | date | NOT NULL              |
| to_date       | date | NULL (NULL = pågående)|

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
| embedding   | vector(1536)| NULL         |
| chunk_index | int         | NOT NULL     |
| tsv         | tsvector    | GENERATED    |

`tsv` genereras från `chunk_text` för BM25/full-text search.
`embedding` dimensioner matchar `text-embedding-3-small` (1536).

Index:
```sql
CREATE INDEX idx_chunks_embedding ON document_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_chunks_tsv ON document_chunks USING gin (tsv);
CREATE INDEX idx_chunks_document ON document_chunks (document_id);
```

### chunk_topics

Many-to-many: varje chunk kan klassificeras under flera topics.

| field    | type | constraint                     |
| -------- | ---- | ------------------------------ |
| chunk_id | uuid | FK document_chunks, NOT NULL   |
| topic_id | uuid | FK topics, NOT NULL            |

Composite PK: `(chunk_id, topic_id)`.

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
| claim_text        | text                                          | NOT NULL     |
| stance            | enum('support', 'oppose', 'unclear', 'mixed') | NOT NULL     |
| confidence        | float                                         |              |
| valid_from        | date                                          |              |
| valid_to          | date                                          |              |
| review_status     | enum('pending', 'approved', 'rejected')       | DEFAULT 'pending' |
| created_at        | timestamptz                                   | DEFAULT now  |

`valid_from` / `valid_to` möjliggör policy drift detection.
`review_status` stödjer admin review workflow.

### claim_topics

Many-to-many: en claim kan röra flera sakfrågor (t.ex. "klimatskatt" → climate + taxation).

| field    | type | constraint          |
| -------- | ---- | ------------------- |
| claim_id | uuid | FK claims, NOT NULL |
| topic_id | uuid | FK topics, NOT NULL |

Composite PK: `(claim_id, topic_id)`.

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

Alltid per ledamot (politician). Parti-aggregering beräknas via `politician_affiliations`.

| field         | type                                     | constraint  |
| ------------- | ---------------------------------------- | ----------- |
| id            | uuid                                     | PK, default |
| vote_id       | uuid                                     | FK votes    |
| politician_id | uuid                                     | FK entities (type='politician') |
| position      | enum('yes', 'no', 'abstain', 'absent')   | NOT NULL    |

Composite unique constraint: `(vote_id, politician_id)`.

## Migrationsordning

1. Extensions (`pgvector`, `pg_trgm`, `pgcrypto`)
2. Enum types
3. `entities`
4. `politician_affiliations` (FK → entities)
5. `documents` (FK → entities)
6. `document_chunks` (FK → documents) + index
7. `topics`
8. `chunk_topics` (FK → document_chunks, topics)
9. `claims` (FK → entities)
10. `claim_topics` (FK → claims, topics)
11. `claim_evidence` (FK → claims, document_chunks)
12. `votes` (FK → topics)
13. `vote_positions` (FK → votes, entities)

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
