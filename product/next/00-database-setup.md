# Step 0: Database Schema, Migrations & Storage

Referens: [MVP1.md](../MVP1.md) (Datamodell, Storage)

## Mål
Etablera fullständigt databasschema, seed data och objektlagring innan ingestion börjar.

## Migrationsverktyg

**Alembic** med SQLAlchemy som ORM. Alla schemaändringar görs via migrationsfiler, inte manuell SQL.

```
alembic/
├── env.py
├── versions/
│   ├── 001_extensions_and_enums.py
│   ├── 002_entities_and_affiliations.py
│   ├── 003_documents_and_document_entities.py
│   ├── 004_document_chunks.py
│   ├── 005_topics_and_chunk_topics.py
│   ├── 006_claims_and_evidence.py
│   ├── 007_votes_and_positions.py
│   └── 008_materialized_views.py
└── alembic.ini
```

## PostgreSQL Extensions

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

## Schema

### entities

| field        | type                                          | constraint      |
| ------------ | --------------------------------------------- | --------------- |
| id           | uuid                                          | PK, default     |
| type         | enum('party', 'politician', 'organization')   | NOT NULL        |
| name         | text                                          | NOT NULL        |
| slug         | text                                          | UNIQUE, NOT NULL|
| abbreviation | text                                          | NULL            |
| color        | text                                          | NULL            |
| aliases      | jsonb                                         | DEFAULT '[]'    |
| metadata     | jsonb                                         | DEFAULT '{}'    |
| created_at   | timestamptz                                   | DEFAULT now     |
| updated_at   | timestamptz                                   | DEFAULT now     |

`slug` är URL-vänlig identifierare (t.ex. `moderaterna`, `ulf-kristersson`). Stödjer lookup via API: `GET /entities/moderaterna`.
`abbreviation` är partiförkortning (t.ex. `S`, `M`, `SD`). NULL för politiker.
`color` är hex-färgkod för visuell representation (t.ex. `#E8112D`). Kritiskt för diagram och jämförelsevyer.
`metadata` för ytterligare attribut som `logo_url`, `photo_url` etc.

### ingestion_state

Checkpointing för inkrementell hämtning. En rad per dokumenttyp och källa.

| field            | type        | constraint        |
| ---------------- | ----------- | ----------------- |
| id               | uuid        | PK, default       |
| source           | text        | NOT NULL          |
| document_type    | text        | NOT NULL          |
| last_fetched_at  | timestamptz |                   |
| last_status      | text        | DEFAULT 'idle'    |
| updated_at       | timestamptz | DEFAULT now       |

Composite unique: `(source, document_type)`.

### politician_affiliations

Kopplar politiker till parti med tidsperiod och roll (hanterar partibyten och rollförändringar).

| field         | type | constraint            |
| ------------- | ---- | --------------------- |
| id            | uuid | PK, default           |
| politician_id | uuid | FK entities, NOT NULL |
| party_id      | uuid | FK entities, NOT NULL |
| role          | text | NULL                  |
| from_date     | date | NOT NULL              |
| to_date       | date | NULL (NULL = pågående)|

`role` anger funktion, t.ex. `'partiledare'`, `'ledamot'`, `'språkrör'`. NULL = vanlig medlem.

### documents

| field               | type                                                                                                          | constraint  |
| ------------------- | ------------------------------------------------------------------------------------------------------------- | ----------- |
| id                  | uuid                                                                                                          | PK, default |
| title               | text                                                                                                          | NOT NULL    |
| body                | text                                                                                                          |             |
| document_type       | enum('motion', 'proposition', 'party_program', 'congress_decision', 'speech', 'press_release', 'policy_paper') | NOT NULL    |
| source_external_id  | text                                                                                                          | UNIQUE      |
| source_url          | text                                                                                                          |             |
| published_at        | timestamptz                                                                                                   |             |
| date_precision      | enum('year', 'month', 'day', 'exact')                                                                         | DEFAULT 'day' |
| metadata            | jsonb                                                                                                         | DEFAULT '{}' |
| raw_storage_key     | text                                                                                                          |             |
| created_at          | timestamptz                                                                                                   | DEFAULT now |
| updated_at          | timestamptz                                                                                                   | DEFAULT now |

`raw_storage_key` pekar på originaldokumentet i S3.
`source_external_id` är dokumentets ID i källsystemet (t.ex. Riksdagens dok-ID). Används för upsert/idempotens.
`source_url` är den URL dokumentet hämtades från. Explicit kolumn istället för i metadata-jsonb.
`date_precision` anger hur exakt `published_at` är. Partiprogram har ofta bara årtal (`year`), riksdagshandlingar har exakt datum (`day`). Frontend använder detta för korrekt datumformatering (t.ex. "2023" vs "15 mars 2023").

`source_id` har tagits bort — ersatt av `document_entities` (many-to-many, se nedan).

Index:
```sql
CREATE UNIQUE INDEX idx_documents_external_id ON documents (source_external_id) WHERE source_external_id IS NOT NULL;
CREATE INDEX idx_documents_type ON documents (document_type);
CREATE INDEX idx_documents_published ON documents (published_at);
```

### document_entities

Many-to-many: kopplar dokument till entiteter med roll. En proposition kan ha regeringen som author, en motion kan ha flera ledamöter från olika partier som signatories.

| field       | type                                             | constraint             |
| ----------- | ------------------------------------------------ | ---------------------- |
| id          | uuid                                             | PK, default            |
| document_id | uuid                                             | FK documents, NOT NULL |
| entity_id   | uuid                                             | FK entities, NOT NULL  |
| role        | enum('author', 'signatory', 'committee', 'source') | NOT NULL             |

Composite unique: `(document_id, entity_id, role)`.

Index:
```sql
CREATE INDEX idx_document_entities_entity ON document_entities (entity_id);
CREATE INDEX idx_document_entities_document ON document_entities (document_id);
```

### document_chunks

| field       | type        | constraint   |
| ----------- | ----------- | ------------ |
| id          | uuid        | PK, default  |
| document_id | uuid        | FK documents |
| chunk_text  | text        | NOT NULL     |
| embedding   | vector(1536)| NULL         |
| chunk_index | int         | NOT NULL     |
| token_count | int         |              |
| tsv         | tsvector    | GENERATED    |

`tsv` genereras från `chunk_text` för BM25/full-text search.
`embedding` dimensioner matchar `text-embedding-3-small` (1536).

Index:
```sql
CREATE INDEX idx_chunks_embedding ON document_chunks
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 24, ef_construction = 128);
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

| field        | type | constraint         |
| ------------ | ---- | ------------------ |
| id           | uuid | PK, default        |
| name         | text | NOT NULL, UNIQUE   |
| slug         | text | UNIQUE, NOT NULL   |
| display_name | text | NOT NULL           |
| parent_topic | uuid | FK topics, NULL    |

`name` är intern identifierare (engelska, t.ex. `migration`).
`slug` är URL-vänlig identifierare (t.ex. `migration`, `foreign-policy`). Stödjer lookup via API: `GET /topics/migration`.
`display_name` är den svenska etiketten som visas i frontend (t.ex. `Migration`, `Energi`).

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
| extraction_model  | text                                          |              |
| extraction_prompt_version | text                                  |              |
| created_at        | timestamptz                                   | DEFAULT now  |
| updated_at        | timestamptz                                   | DEFAULT now  |

`valid_from` / `valid_to` möjliggör policy drift detection.
`review_status` stödjer admin review workflow.

### claim_topics

Many-to-many: en claim kan röra flera sakfrågor (t.ex. "klimatskatt" → climate + taxation).

| field    | type | constraint          |
| -------- | ---- | ------------------- |
| claim_id | uuid | FK claims, NOT NULL |
| topic_id | uuid | FK topics, NOT NULL |

Composite PK: `(claim_id, topic_id)`.

### claim_history

Audit trail för claim-ändringar (stance, review_status, topic). Skapas automatiskt vid varje uppdatering.

| field         | type        | constraint        |
| ------------- | ----------- | ----------------- |
| id            | uuid        | PK, default       |
| claim_id      | uuid        | FK claims         |
| changed_field | text        | NOT NULL          |
| old_value     | text        |                   |
| new_value     | text        |                   |
| changed_by    | text        |                   |
| changed_at    | timestamptz | DEFAULT now       |

Index:
```sql
CREATE INDEX idx_claim_history_claim ON claim_history (claim_id);
```

### claim_evidence

| field    | type  | constraint    |
| -------- | ----- | ------------- |
| id       | uuid  | PK, default   |
| claim_id | uuid  | FK claims     |
| chunk_id | uuid  | FK document_chunks |
| quote    | text  | NOT NULL      |
| score    | float |               |

### votes

| field           | type        | constraint           |
| --------------- | ----------- | -------------------- |
| id              | uuid        | PK, default          |
| riksdag_vote_id | text        | UNIQUE               |
| document_id     | uuid        | FK documents, NULL   |
| title           | text        | NOT NULL             |
| date            | date        | NOT NULL             |
| topic_id        | uuid        | FK topics, NULL      |
| updated_at      | timestamptz | DEFAULT now          |

`document_id` kopplar voteringen till den proposition eller motion som röstningen gäller.

### vote_positions

Alltid per ledamot (politician). Parti-aggregering beräknas via `politician_affiliations`.

| field         | type                                     | constraint  |
| ------------- | ---------------------------------------- | ----------- |
| id            | uuid                                     | PK, default |
| vote_id       | uuid                                     | FK votes    |
| politician_id | uuid                                     | FK entities (type='politician') |
| position      | enum('yes', 'no', 'abstain', 'absent')   | NOT NULL    |

Composite unique constraint: `(vote_id, politician_id)`.

### politician_issue_scores (materialized view)

Aggregerad poäng per politiker och sakfråga. Beräknas från antal motioner, anföranden och citat kopplade till en topic, viktat efter dokumenttyp.

| field       | type        | note                  |
| ----------- | ----------- | --------------------- |
| entity_id   | uuid        | FK entities (politician) |
| topic_id    | uuid        | FK topics             |
| score       | float       | Viktat poäng          |
| doc_count   | int         | Antal dokument        |
| computed_at | timestamptz | Senaste beräkning     |

```sql
CREATE MATERIALIZED VIEW politician_issue_scores AS
SELECT
  de.entity_id,
  ct.topic_id,
  COUNT(DISTINCT d.id) AS doc_count,
  SUM(CASE d.document_type
    WHEN 'motion' THEN 3
    WHEN 'speech' THEN 2
    ELSE 1
  END)::float AS score,
  now() AS computed_at
FROM document_entities de
JOIN documents d ON d.id = de.document_id
JOIN document_chunks dc ON dc.document_id = d.id
JOIN chunk_topics ct ON ct.chunk_id = dc.id
WHERE de.entity_id IN (SELECT id FROM entities WHERE type = 'politician')
GROUP BY de.entity_id, ct.topic_id;

CREATE UNIQUE INDEX idx_pis_entity_topic ON politician_issue_scores (entity_id, topic_id);
```

Refreshas periodiskt: `REFRESH MATERIALIZED VIEW CONCURRENTLY politician_issue_scores;`

## Migrationsordning

1. Extensions (`pgvector`, `pg_trgm`, `pgcrypto`)
2. Enum types
3. `entities`
4. `ingestion_state`
5. `politician_affiliations` (FK → entities)
6. `documents` + unique index
7. `document_entities` (FK → documents, entities)
8. `document_chunks` (FK → documents) + index
9. `topics`
10. `chunk_topics` (FK → document_chunks, topics)
11. `claims` (FK → entities)
12. `claim_topics` (FK → claims, topics)
13. `claim_history` (FK → claims)
14. `claim_evidence` (FK → claims, document_chunks)
15. `votes` (FK → topics, documents)
16. `vote_positions` (FK → votes, entities)
17. `politician_issue_scores` (materialized view)

## Seed data: Riksdagspartier

```json
[
  { "type": "party", "name": "Socialdemokraterna", "slug": "socialdemokraterna", "abbreviation": "S", "color": "#E8112D", "aliases": ["S", "Socialdemokraterna", "socialdemokraterna"] },
  { "type": "party", "name": "Moderaterna", "slug": "moderaterna", "abbreviation": "M", "color": "#52BDEC", "aliases": ["M", "Moderaterna", "moderaterna", "Nya Moderaterna"] },
  { "type": "party", "name": "Sverigedemokraterna", "slug": "sverigedemokraterna", "abbreviation": "SD", "color": "#DDDD00", "aliases": ["SD", "Sverigedemokraterna", "sverigedemokraterna"] },
  { "type": "party", "name": "Centerpartiet", "slug": "centerpartiet", "abbreviation": "C", "color": "#009933", "aliases": ["C", "Centerpartiet", "centerpartiet"] },
  { "type": "party", "name": "Vänsterpartiet", "slug": "vansterpartiet", "abbreviation": "V", "color": "#DA291C", "aliases": ["V", "Vänsterpartiet", "vänsterpartiet"] },
  { "type": "party", "name": "Kristdemokraterna", "slug": "kristdemokraterna", "abbreviation": "KD", "color": "#000077", "aliases": ["KD", "Kristdemokraterna", "kristdemokraterna"] },
  { "type": "party", "name": "Liberalerna", "slug": "liberalerna", "abbreviation": "L", "color": "#006AB3", "aliases": ["L", "Liberalerna", "liberalerna", "Folkpartiet"] },
  { "type": "party", "name": "Miljöpartiet", "slug": "miljopartiet", "abbreviation": "MP", "color": "#83CF39", "aliases": ["MP", "Miljöpartiet", "miljöpartiet", "Miljöpartiet de gröna"] }
]
```

## Seed data: Topics

```json
[
  { "name": "migration", "slug": "migration", "display_name": "Migration" },
  { "name": "energy", "slug": "energi", "display_name": "Energi" },
  { "name": "defense", "slug": "forsvar", "display_name": "Försvar" },
  { "name": "taxation", "slug": "skatter", "display_name": "Skatter" },
  { "name": "education", "slug": "utbildning", "display_name": "Utbildning" },
  { "name": "climate", "slug": "klimat", "display_name": "Klimat" },
  { "name": "healthcare", "slug": "sjukvard", "display_name": "Sjukvård" },
  { "name": "crime", "slug": "brottslighet", "display_name": "Brottslighet" },
  { "name": "economy", "slug": "ekonomi", "display_name": "Ekonomi" },
  { "name": "labor", "slug": "arbetsmarknad", "display_name": "Arbetsmarknad" },
  { "name": "housing", "slug": "bostad", "display_name": "Bostad" },
  { "name": "foreign_policy", "slug": "utrikespolitik", "display_name": "Utrikespolitik" }
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
