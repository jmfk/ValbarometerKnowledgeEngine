# Volume Estimate & Cost Analysis

Referens: [MVP1.md](../MVP1.md), [SRD-architecture.md](../SRD-architecture.md)

## Scope

MVP: innevarande + föregående mandatperiod (~8 år, 2018–2026).

## Dokumentvolymer (estimat)

| Dokumenttyp | Per år (snitt) | Totalt (8 år) | Snitt tokens/dok | Totalt tokens |
|---|---|---|---|---|
| Motioner | ~3 000 | ~25 000 | ~4 000 | ~100M |
| Propositioner | ~200 | ~1 600 | ~20 000 | ~32M |
| Anföranden | ~15 000 | ~120 000 | ~1 000 | ~120M |
| Voteringar | ~1 200 | ~10 000 | metadata only | — |
| Partiprogram | 8 st | 8 st | ~30 000 | ~0.24M |
| Stämmobeslut/policy | ~30 | ~30 | ~10 000 | ~0.3M |
| Pressmeddelanden | ~500 | ~4 000 | ~800 | ~3.2M |
| **Totalt** | | **~160 600 dok** | | **~256M tokens** |

Källa motioner: riksdagen.se (2020: 3 645, 2023: 2 701, 2024: 3 178, 2025: 3 738).
Källa propositioner: SCB/riksdagen (~200/år i snitt).
Anföranden: estimat baserat på ~15 000 debattinlägg per riksmöte.

## Chunks (500 tokens, 50 token overlap)

| Dokumenttyp | Chunks totalt |
|---|---|
| Motioner | ~220 000 |
| Propositioner | ~70 000 |
| Anföranden | ~260 000 |
| Partiprogram | ~500 |
| Stämmobeslut/policy | ~650 |
| Pressmeddelanden | ~7 000 |
| **Totalt** | **~558 000** |

## Embedding-kostnader

Totalt tokens att embeddas: ~256M tokens.

| Modell | Pris/1M tokens | Total kostnad | Batch API (50% rabatt) |
|---|---|---|---|
| text-embedding-3-large (3072 dim) | $0.13 | ~$33 | ~$17 |
| text-embedding-3-small (1536 dim) | $0.02 | ~$5 | ~$2.50 |

Embedding-kostnaden är försumbar oavsett modellval.

## Extraction-kostnader (GPT-4o)

### Alt 1: Naiv — kör GPT-4o på alla chunks

| | Input tokens | Output tokens | Kostnad |
|---|---|---|---|
| Per chunk | ~1 000 (prompt + text) | ~200 | |
| 558 000 chunks | 558M | 112M | |
| **Kostnad (standard)** | 558M × $2.50/M = $1 395 | 112M × $10/M = $1 120 | **$2 515** |
| **Kostnad (batch API)** | $698 | $560 | **$1 258** |

### Alt 2: Tvåstegs-extraction (rekommenderat)

**Steg 1 — GPT-4o-mini klassificering**: Vilka chunks kan innehålla en politisk ståndpunkt?
Estimat: ~20% av chunks är relevanta (resten är procedurell text, hänvisningar, etc.)

| | Input tokens | Output tokens | Kostnad |
|---|---|---|---|
| 558 000 chunks | 335M (600 tok/chunk) | 28M (50 tok/chunk) | |
| **GPT-4o-mini** | 335M × $0.15/M = $50 | 28M × $0.60/M = $17 | **$67** |

**Steg 2 — GPT-4o extraction** på ~112 000 relevanta chunks:

| | Input tokens | Output tokens | Kostnad |
|---|---|---|---|
| 112 000 chunks | 112M | 22M | |
| **GPT-4o (batch)** | 112M × $1.25/M = $140 | 22M × $5/M = $110 | **$250** |

**Total tvåstegs-kostnad: ~$317** (87% besparing vs naiv approach).

## Lagringskostnader

| Resurs | Storlek (estimat) |
|---|---|
| Rådokument i S3 (XML/JSON/PDF) | ~5–10 GB |
| PostgreSQL text (chunks) | ~1–2 GB |
| Vektorer (3072 dim, float32) | ~6.4 GB (558k × 3072 × 4 bytes) |
| Vektorer (1536 dim, float32) | ~3.2 GB |
| HNSW-index overhead (~2×) | ~6–13 GB |
| **Total DB-storlek** | **~15–25 GB** |

## Rekommendation

1. Använd **tvåstegs-extraction** — besparingen ($2 500 → $317) motiverar den extra komplexiteten.
2. Starta med **text-embedding-3-small** (1536 dim) — kostnadsskillnaden för embeddings är liten, men lagring/index-prestanda förbättras avsevärt vid halverad dimension.
3. Använd **Batch API** för all initial bulk-bearbetning (embeddings + extraction).
4. Initial bulk-laddning beräknas ta ~24–48h via Batch API.
