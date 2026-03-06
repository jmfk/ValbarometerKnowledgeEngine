# Step 0.5: Pipeline-orkestrering

Referens: [MVP1.md](../MVP1.md) (Systemarkitektur), [07-volume-estimate.md](07-volume-estimate.md)

## Mål

Etablera ett orkestreringsramverk som schemalägger, övervakar och hanterar fel i hela data-pipelinen.

## Val: Dagster

Dagster väljs framför Airflow och Prefect av följande skäl:

1. **Asset-baserat paradigm**: Dagster modellerar pipelinen som materialiserbara assets (documents, chunks, embeddings, claims) — matchar kunskapsbasens dataflöde bättre än task-baserat tänkande.
2. **Inbyggd data lineage**: Visar hur assets hänger ihop utan extra konfiguration.
3. **Lokalt utvecklingsläge**: `dagster dev` ger UI + scheduler lokalt utan Docker/Kubernetes.
4. **Python-native**: Ren Python-konfiguration, inget DSL.
5. **Sensor-stöd**: Inbyggda sensors för att trigga pipelines vid ny data (t.ex. nya motioner i Riksdagens API).

## Pipeline-struktur

```
dagster_project/
├── dagster_project/
│   ├── __init__.py
│   ├── assets/
│   │   ├── ingestion.py          # Riksdagen + parti-dokument
│   │   ├── processing.py         # Chunking + embeddings
│   │   ├── extraction.py         # Claim extraction (tvåstegs)
│   │   └── materialized_views.py # politician_issue_scores refresh
│   ├── resources/
│   │   ├── database.py           # PostgreSQL connection
│   │   ├── storage.py            # S3/R2 client
│   │   └── openai_client.py      # OpenAI API wrapper med rate limiting
│   ├── sensors/
│   │   └── riksdagen_sensor.py   # Pollar Riksdagens API för nya dokument
│   ├── schedules/
│   │   └── daily.py              # Daglig ingestion
│   └── partitions.py             # Partitionering per riksmöte/år
├── dagster.yaml
└── pyproject.toml
```

## Assets (DAG)

```
riksdagen_documents (partitioned by riksmöte)
  └─→ document_chunks
        ├─→ chunk_embeddings
        │     └─→ chunk_topics (classification)
        └─→ claim_extraction (tvåstegs)
              └─→ politician_issue_scores (materialized view refresh)

party_documents
  └─→ document_chunks (samma downstream)

votes_ingestion
  └─→ vote_positions
```

## Scheman

| Schema | Frekvens | Beskrivning |
|--------|----------|-------------|
| riksdagen_daily | Dagligen 06:00 | Hämta nya motioner, propositioner, anföranden, voteringar |
| party_weekly | Veckovis söndag | Scrapa partiwebbplatser för nya pressmeddelanden/dokument |
| recompute_views | Dagligen 08:00 | Refresha materialized views efter ingestion |

## Sensors

| Sensor | Trigger | Beskrivning |
|--------|---------|-------------|
| new_documents_sensor | Ny rad i `documents` | Triggar chunking + embedding för nya dokument |
| pending_chunks_sensor | Chunks utan embedding | Triggar embedding-jobb |
| pending_extraction_sensor | Chunks utan claims | Triggar claim extraction |

## Partitionering

Riksdagsdata partitioneras per riksmöte (t.ex. `2024/25`, `2023/24`). Möjliggör:
- Selektiv omprocessning av ett riksmöte
- Backfill av historisk data utan att påverka aktuella data
- Parallell bearbetning av olika riksmöten

## Retry- och felhantering

- **Max retries**: 3 per op, med exponential backoff (10s, 60s, 300s)
- **Alerting**: Dagster-events → webhook → Slack/email vid failure
- **Checkpointing**: Varje ingestion-jobb uppdaterar `ingestion_state`-tabellen. Vid omstart fortsätter från senaste checkpoint.
- **Dead letter**: Dokument som misslyckas 3 gånger markeras i `ingestion_state.last_status = 'failed'` för manuell granskning.

## Monitorering

Dagster UI ger:
- Asset-status (materialiserad/ej materialiserad)
- Run-historik med timing
- Failure-alerts
- Data lineage-visualisering

Komplettera med:
- **PostgreSQL-metrics**: Antal dokument/chunks/claims per dag (enkel SQL-query som Dagster-sensor)
- **Kostnadsspårning**: Logga OpenAI API-tokens per run i `metadata`
