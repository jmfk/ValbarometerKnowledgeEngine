# Step 5: API & Comparison Engine

Referens: [MVP1.md](../MVP1.md) (API & Comparisons)

## Mål
Exponera kunskapsbasen via ett API för att möjliggöra jämförelser och analys.

## Funktionella krav
1. **Search**: Hybrid sökning (metadata filter + BM25 + vektor) efter claims.
2. **Compare**: Sammanställa ståndpunkter vs röstningsbeteende för ett ämne.
3. **Evidence Cards**: Returnera kompletta objekt med påstående, citat och källa.
4. **Reranking**: Retrieve → rerank (cross-encoder eller LLM-baserad) → extract evidence → returnera strukturerad output.
5. **Admin Tools**: Intern panel/endpoints för claim review, manuell korrigering, topic tagging och deduplication.

## Endpoints

### Public API

```
GET  /entities                          Lista alla entiteter (partier, politiker)
GET  /entities/{id}                     Detaljer för en entitet

GET  /topics                            Lista alla topics (med hierarki)

GET  /claims?entity={}&topic={}         Sök claims, filtrera på entitet och/eller topic
GET  /claims/{id}                       En claim med all evidens

GET  /votes                             Lista voteringar, filtrera på topic/datum
GET  /votes/{id}                        Detaljer för en votering med positioner per parti

GET  /compare?topic={}                  Jämför alla partier för ett ämne:
                                        → party stance, voting behavior, evidence

GET  /politicians/{id}/issues           Politician issue ownership scores
```

### Admin API

```
GET    /admin/claims?status=pending     Lista claims som väntar på granskning
PATCH  /admin/claims/{id}               Uppdatera review_status, stance, topic
POST   /admin/topics                    Skapa ny topic
PATCH  /admin/topics/{id}               Redigera topic (namn, parent)
POST   /admin/dedup/merge               Slå ihop duplicerade claims
```

## Tekniska steg
- Bygga FastAPI-endpoints enligt ovan.
- Implementera hybrid retrieval: metadata-filter → BM25 (Postgres full-text) + vector search (pgvector) → merge scores.
- Integrera reranking-steg med cross-encoder modell (t.ex. `bge-reranker-v2-m3`) efter initial retrieval.
- Implementera logik för att aggregera `claims` och `vote_positions` i `/compare`.
- Skapa filter för ämnen (topics) och entiteter (partier/politiker).
- Bygga admin-endpoints med autentisering för claim review och topic management.
