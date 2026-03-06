# PRD – Valbarometer Knowledge Engine (MVP)

## Syfte

Bygga en evidensbaserad kunskapsbas som samlar och analyserar:

- svenska politiska partiers ståndpunkter
- hur partier faktiskt röstar i riksdagen
- vilka frågor politiker driver
- dokument och uttalanden från primärkällor

Målet är att skapa en **transparent datamotor** som senare kan driva:

- valkompass
- partijämförelser
- tidslinjer över politiska positioner
- analys av politiker och sakfrågor

Det viktiga ordet här är **transparent**. Varje slutsats måste kunna spåras tillbaka till ett citat eller dokument.

------

# MVP Scope

### Partier

Starta med riksdagspartierna:

- Socialdemokraterna
- Moderaterna
- Sverigedemokraterna
- Centerpartiet
- Vänsterpartiet
- Kristdemokraterna
- Liberalerna
- Miljöpartiet

------

### Dokumenttyper

MVP bör stödja:

1. **Partiprogram**
2. **Partistämmobeslut**
3. **Motioner**
4. **Propositioner**
5. **Voteringar**
6. **Riksdagsanföranden**
7. **Pressmeddelanden**

Media och journalistlager kan vänta till senare.

------

# Kärnfunktioner

### 1 – Stance extraction

Systemet ska kunna identifiera:

```
subject: parti eller politiker
topic: sakfråga
stance: stöd / emot / oklar / blandad
source: dokument
```

Exempel:

```
subject: Moderaterna
topic: kärnkraft
stance: support expansion
source: partiprogram 2023
evidence: citat
```

------

### 2 – Voting alignment

Visa hur partier faktiskt röstar.

Exempel:

```
topic: migration
vote: proposition X
party vote distribution
```

Sedan kan man visa:

```
official stance vs parliamentary behavior
```

------

### 3 – Politician issue ownership

Identifiera vilka politiker som driver vilka frågor.

Beräknas via:

- motioner
- anföranden
- citat
- dokumentfrekvens

Resultat:

```
politician_issue_score
```

------

### 4 – Evidence cards

All output ska kunna visas som:

```
CLAIM

Moderaterna stödjer utbyggnad av kärnkraft

EVIDENCE

Document: Partiprogram 2023
Quote: "Sverige behöver fler kärnkraftsreaktorer..."
Date: 2023
Confidence: 0.91
```

Detta är kritiskt. Utan evidens är analysen bara gissning.

------

# Systemarkitektur

## Översikt

```
Data sources
     ↓
Ingestion workers
     ↓
Document storage
     ↓
Text processing pipeline
     ↓
Knowledge extraction
     ↓
PostgreSQL knowledge base
     ↓
API
     ↓
Frontend / analysis tools
```

------

# Data ingestion layer

Python workers.

Källor:

### Riksdagen

API:

- motioner
- propositioner
- voteringar
- anföranden

### Partier

Crawler:

- partiprogram
- stämmodokument
- policy papers

### Press

RSS + scraping.

------

# Storage

### PostgreSQL

Primär databas.

Extensions:

```
pgvector
pg_trgm
```

### Objektlagring

S3-bucket för:

```
PDF
HTML snapshots
raw documents
```

------

# Datamodell

## Entities

```
entities
```

| field      | type                              |
| ---------- | --------------------------------- |
| id         | uuid                              |
| type       | party / politician / organization |
| name       | text                              |
| aliases    | jsonb                             |
| created_at | timestamp                         |

------

## Documents

```
documents
```

| field         | type      |
| ------------- | --------- |
| id            | uuid      |
| source_id     | uuid      |
| title         | text      |
| body          | text      |
| document_type | enum      |
| published_at  | timestamp |
| metadata      | jsonb     |

------

## Document chunks

```
document_chunks
```

| field       | type   |
| ----------- | ------ |
| id          | uuid   |
| document_id | uuid   |
| chunk_text  | text   |
| embedding   | vector |
| chunk_index | int    |

------

## Topics

```
topics
```

| field        | type |
| ------------ | ---- |
| id           | uuid |
| name         | text |
| parent_topic | uuid |

Exempel:

```
migration
energy
defense
taxation
education
climate
healthcare
crime
```

------

## Claims

```
claims
```

| field             | type      |
| ----------------- | --------- |
| id                | uuid      |
| subject_entity_id | uuid      |
| topic_id          | uuid      |
| stance            | enum      |
| confidence        | float     |
| created_at        | timestamp |

------

## Claim evidence

```
claim_evidence
```

| field    | type  |
| -------- | ----- |
| id       | uuid  |
| claim_id | uuid  |
| chunk_id | uuid  |
| quote    | text  |
| score    | float |

------

## Votes

```
votes
```

| field           | type |
| --------------- | ---- |
| id              | uuid |
| riksdag_vote_id | text |
| title           | text |
| date            | date |
| topic_id        | uuid |

------

## Vote positions

```
vote_positions
```

| field     | type               |
| --------- | ------------------ |
| vote_id   | uuid               |
| entity_id | uuid               |
| vote      | yes / no / abstain |

------

# NLP pipeline

Pipeline steg:

### 1 Document parsing

PDF → text.

### 2 Chunking

```
~500 tokens
```

### 3 Embeddings

Model:

```
bge-m3
or
text-embedding-3-large
```

### 4 Topic classification

LLM eller finetuned classifier.

### 5 Claim extraction

Structured extraction:

```
subject
topic
stance
evidence span
```

### 6 Deduplication

Multiple documents kan säga samma sak.

------

# Retrieval architecture

Hybrid search:

```
metadata filtering
+
BM25
+
vector search
```

Ranking pipeline:

```
retrieve
rerank
extract evidence
generate structured output
```

------

# API

FastAPI.

Endpoints:

### Entities

```
GET /entities
GET /entities/{id}
```

------

### Topics

```
GET /topics
```

------

### Claims

```
GET /claims?entity=moderaterna&topic=energy
```

------

### Votes

```
GET /votes
GET /votes/{id}
```

------

### Comparisons

```
GET /compare?topic=immigration
```

Returnerar:

```
party stance
voting behavior
evidence
```

------

# Admin tools

Intern panel behövs för:

- claim review
- manual correction
- topic tagging
- deduplication

AI extraction måste kunna granskas.

------

# MVP roadmap

## Phase 1

Riksdagsdata ingestion.

- motioner
- voteringar
- anföranden

------

## Phase 2

Partiprogram ingestion.

------

## Phase 3

Claim extraction pipeline.

------

## Phase 4

Topic taxonomy.

------

## Phase 5

Comparison API.

------

# Viktig designprincip

Politik förändras.

Så alla claims måste ha:

```
valid_from
valid_to
```

Annars går det inte att se när partier ändrar sig.

------

# Vad man absolut inte ska göra i MVP

Undvik:

- mediabias analyser
- journalist scoring
- social media ingestion
- graph database

Alla dessa kan byggas senare.

------

# Långsiktig vision

När kunskapsbasen är stabil kan man bygga:

### Valbarometer

Användaren svarar på frågor.

Systemet matchar:

```
user positions
vs
party positions
```

Men baserat på **verklig evidens**, inte bara partiernas egen beskrivning.

------

# Den verkligt intressanta framtida funktionen

En sak som skulle göra detta system **radikalt bättre än alla valkompasser i Sverige**:

```
policy drift detection
```

Exempel:

```
Parti X 2018 → stance A
Parti X 2022 → stance B
Parti X 2026 → stance C
```

Med evidens.

Det visar hur politiska idéer faktiskt förändras över tid.

