# Step 5: API & Comparison Engine

Referens: [MVP1.md](../MVP1.md) (API & Comparisons)

## Mål
Exponera kunskapsbasen via ett API för att möjliggöra jämförelser och analys.

## MVP-scope (Phase 3)

### Funktionella krav
1. **Search**: Metadata-filter + vector search efter claims.
2. **Evidence Cards**: Returnera kompletta objekt med påstående, citat och källa.

### MVP Endpoints

```
GET  /entities                          Lista alla entiteter (partier, politiker)
GET  /entities/{id}                     Detaljer för en entitet

GET  /topics                            Lista alla topics (med hierarki)

GET  /claims?entity={}&topic={}         Sök claims, filtrera på entitet och/eller topic
GET  /claims/{id}                       En claim med all evidens

GET  /votes                             Lista voteringar, filtrera på topic/datum
GET  /votes/{id}                        Detaljer för en votering med positioner per parti
```

### MVP Tekniska steg
- Bygga FastAPI-endpoints enligt ovan.
- Implementera metadata-filter + vector search (pgvector).
- Skapa filter för ämnen (topics) och entiteter (partier/politiker).

---

## Deferred (post-MVP)

### Comparison Engine
```
GET  /compare?topic={}                  Jämför alla partier för ett ämne
GET  /politicians/{id}/issues           Politician issue ownership scores
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
