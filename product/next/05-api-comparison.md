# Step 5: API & Comparison Engine

Referens: [MVP1.md](../MVP1.md) (API & Comparisons)

## Mål
Exponera kunskapsbasen via ett API för att möjliggöra jämförelser och analys.

## Konventioner

### Paginering

Alla list-endpoints stödjer offset-baserad paginering:

```
?page=1&per_page=20              # default: page=1, per_page=20, max per_page=100
?sort=published_at&order=desc    # sortering (fältspecifikt per endpoint)
```

### Response-envelope

Alla list-endpoints returnerar:

```json
{
  "data": [...],
  "meta": {
    "total": 1234,
    "page": 1,
    "per_page": 20,
    "total_pages": 62
  }
}
```

Single-resource endpoints returnerar objektet direkt (utan envelope).

### Slug-lookup

Endpoints som tar `{id}` accepterar både UUID och slug: `GET /entities/moderaterna` och `GET /entities/{uuid}` fungerar likvärdigt.

### Tidsfiltrering (claims)

Claims har `valid_from`/`valid_to` för policy drift detection. Konventioner:

- `valid_to IS NULL` = aktiv/nuvarande ståndpunkt
- `GET /claims` returnerar **default enbart aktuella** claims (`valid_to IS NULL`)
- `?as_of=2022-01-01` returnerar claims giltiga vid givet datum
- `?include_historical=true` returnerar alla claims oavsett giltighetstid

### Review-status-filtrering

Claims har `review_status` (`pending`, `approved`, `rejected`).

- Public API returnerar **default enbart `approved`** claims
- `?include_pending=true` inkluderar `pending` claims (för admin-kontext)
- `review_status` inkluderas alltid i response-objektet

---

## MVP-scope (Phase 3)

### Funktionella krav
1. **Search**: Metadata-filter + vector search efter claims.
2. **Evidence Cards**: Returnera kompletta objekt med påstående, citat och källa.

### MVP Endpoints

```
GET  /health                            Health check (DB-anslutning, senaste ingestion timestamp)

GET  /entities                          Lista alla entiteter (partier, politiker)
                                        ?type=party|politician
                                        ?page=1&per_page=20
GET  /entities/{id_or_slug}             Detaljer för en entitet

GET  /topics                            Lista alla topics (med hierarki)

GET  /claims                            Sök claims
                                        ?entity={id_or_slug}
                                        ?topic={id_or_slug}
                                        ?stance=support|oppose|unclear|mixed
                                        ?as_of=2024-01-01
                                        ?include_historical=true
                                        ?include_pending=true
                                        ?sort=confidence|created_at&order=desc
                                        ?page=1&per_page=20
GET  /claims/{id}                       En claim med all evidens

GET  /votes                             Lista voteringar
                                        ?topic={id_or_slug}
                                        ?date_from=2022-01-01&date_to=2024-12-31
                                        ?sort=date&order=desc
                                        ?page=1&per_page=20
GET  /votes/{id}                        Detaljer för en votering med positioner per parti

GET  /search?q={query}                  Unified search (claims, topics, entiteter)
                                        ?type=claim,topic,entity
                                        ?page=1&per_page=20
GET  /autocomplete?q={prefix}           Snabbsökning (trigram-baserad)
                                        ?type=entity,topic
                                        ?limit=10
```

### Evidence Card response-format

`GET /claims/{id}` returnerar denormaliserad evidens med dokumentkontext:

```json
{
  "id": "...",
  "subject": { "id": "...", "name": "Moderaterna", "slug": "moderaterna", "abbreviation": "M", "color": "#52BDEC" },
  "claim_text": "Moderaterna stödjer utbyggnad av kärnkraft",
  "stance": "support",
  "confidence": 0.91,
  "valid_from": "2023-01-15",
  "valid_to": null,
  "review_status": "approved",
  "topics": [
    { "id": "...", "slug": "energi", "display_name": "Energi" }
  ],
  "evidence": [
    {
      "quote": "Sverige behöver fler kärnkraftsreaktorer...",
      "score": 0.93,
      "document": {
        "id": "...",
        "title": "Partiprogram 2023",
        "document_type": "party_program",
        "published_at": "2023-01-15",
        "date_precision": "year",
        "source_url": "https://moderaterna.se/partiprogram"
      }
    }
  ]
}
```

### Observabilitet

- **Health endpoint**: `GET /health` returnerar DB-status, senaste ingestion-timestamp från `ingestion_state`, och antal claims/documents.
- **Request logging**: `structlog` middleware som loggar method, path, status_code, duration per request.
- **Metrics**:
  - `api_requests_total{method, path, status}`
  - `api_request_duration_seconds{method, path}`

### MVP Tekniska steg
- Bygga FastAPI-endpoints enligt ovan.
- Implementera metadata-filter + vector search (pgvector).
- Skapa filter för ämnen (topics) och entiteter (partier/politiker).
- Implementera slug-baserad lookup (UUID eller slug i samma parameter).
- Implementera paginering, sortering och response-envelope som gemensam utility.
- Filtrera claims: default `review_status='approved'` och `valid_to IS NULL`.
- Denormalisera evidence med dokumentkontext i claims-responses.
- Implementera `/search` (unified BM25 + trigram) och `/autocomplete` (pg_trgm).
- Konfigurera `structlog` middleware och health endpoint.

---

## Deferred (post-MVP)

### Comparison Engine

```
GET  /compare?topic={id_or_slug}        Jämför alla partier för ett ämne
                                        ?as_of=2024-01-01
GET  /politicians/{id_or_slug}/issues   Politician issue ownership scores
GET  /entities/{id_or_slug}/timeline    Policy drift per entitet
                                        ?topic={id_or_slug}
```

#### Compare response-kontrakt

`GET /compare?topic=energy` returnerar:

```json
{
  "topic": { "id": "...", "name": "energy", "slug": "energi", "display_name": "Energi" },
  "as_of": "2026-03-06",
  "parties": [
    {
      "entity": { "id": "...", "name": "Moderaterna", "slug": "moderaterna", "abbreviation": "M", "color": "#52BDEC" },
      "claims": [
        {
          "id": "...",
          "claim_text": "Stödjer utbyggnad av kärnkraft",
          "stance": "support",
          "confidence": 0.91,
          "valid_from": "2023-01-15",
          "evidence_count": 3
        }
      ],
      "voting_summary": {
        "total_votes": 12,
        "yes_pct": 0.83,
        "no_pct": 0.08,
        "abstain_pct": 0.08
      },
      "alignment_score": 0.87
    }
  ]
}
```

`alignment_score` mäter överensstämmelse mellan uttalad ståndpunkt (claims) och faktiskt röstningsbeteende.

#### Timeline response-kontrakt

`GET /entities/moderaterna/timeline?topic=energi` returnerar:

```json
{
  "entity": { "id": "...", "name": "Moderaterna", "slug": "moderaterna" },
  "topic": { "id": "...", "slug": "energi", "display_name": "Energi" },
  "timeline": [
    {
      "claim_text": "Kärnkraften bör avvecklas",
      "stance": "oppose",
      "valid_from": "2006-01-01",
      "valid_to": "2014-12-31",
      "evidence_count": 2
    },
    {
      "claim_text": "Stödjer utbyggnad av kärnkraft",
      "stance": "support",
      "valid_from": "2022-01-01",
      "valid_to": null,
      "evidence_count": 3
    }
  ]
}
```

### BM25 Hybrid Search & Reranking
- Hybrid retrieval: metadata-filter → BM25 + vector search → merge scores.
- Reranking med cross-encoder (t.ex. `bge-reranker-v2-m3`).

### Admin API
```
GET    /admin/claims?status=pending     Lista claims som väntar på granskning
PATCH  /admin/claims/{id}               Uppdatera review_status, stance, topic
POST   /admin/topics                    Skapa ny topic
PATCH  /admin/topics/{id}               Redigera topic (namn, parent)
POST   /admin/dedup/merge               Slå ihop duplicerade claims
```

### Deferred Tekniska steg
- Implementera logik för att aggregera `claims` och `vote_positions` i `/compare`.
- Bygga admin-endpoints med autentisering för claim review och topic management.
