# Step 6: Golden Set – Validation av Claim Extraction

Referens: [MVP1.md](../MVP1.md) (Kärnfunktion 1 & 4)

## Mål
Validera att LLM-baserad claim extraction (Gemini 2.5 Flash) producerar korrekta, konsekventa resultat på svensk politisk text innan pipelinen automatiseras.

## Metod
1. Samla 50–100 textstycken från riktiga riksdagsdokument (motioner, propositioner).
2. Hand-annotera varje stycke med förväntad output: subject, topics, stance, evidence quote.
3. Kör LLM extraction på samma stycken.
4. Mät precision, recall och konsistens (samma input → samma output vid upprepad körning).

## Golden Set Format

Filen `tests/golden_set/claims.jsonl` ska innehålla ett JSON-objekt per rad:

```jsonl
{
  "id": "gs-001",
  "source_text": "Den svenska texten från dokumentet...",
  "source_document": { "type": "motion", "id": "2024/25:1234", "party": "M" },
  "expected_claims": [
    {
      "subject": "Moderaterna",
      "topics": ["energy"],
      "stance": "support",
      "claim_text": "Moderaterna stödjer utbyggnad av kärnkraft",
      "evidence_quote": "Vi vill möjliggöra bygget av nya kärnkraftsreaktorer..."
    }
  ]
}
```

## Exempelannoteringar

Nedan följer startpunkten för golden set. Dessa är baserade på kända, offentliga ståndpunkter och ska verifieras mot faktiska dokumentcitat.

### Energi

| id     | subject           | topics     | stance  | claim_text                                                  |
| ------ | ----------------- | ---------- | ------- | ----------------------------------------------------------- |
| gs-001 | Moderaterna       | energy     | support | Moderaterna stödjer utbyggnad av kärnkraft                  |
| gs-002 | Miljöpartiet      | energy     | oppose  | Miljöpartiet motsätter sig kärnkraft                        |
| gs-003 | Sverigedemokraterna| energy     | support | SD stödjer kärnkraftsutbyggnad                              |
| gs-004 | Socialdemokraterna | energy     | mixed   | S har skiftat position kring kärnkraft                      |

### Migration

| id     | subject            | topics    | stance  | claim_text                                                    |
| ------ | ------------------ | --------- | ------- | ------------------------------------------------------------- |
| gs-010 | Sverigedemokraterna | migration | oppose  | SD vill kraftigt minska invandringen                          |
| gs-011 | Moderaterna        | migration | oppose  | M vill begränsa invandringen                                  |
| gs-012 | Vänsterpartiet     | migration | support | V stödjer en generös flyktingpolitik                          |
| gs-013 | Centerpartiet      | migration | support | C förespråkar öppen och reglerad invandring                   |

### Försvar

| id     | subject           | topics   | stance  | claim_text                                                     |
| ------ | ----------------- | -------- | ------- | -------------------------------------------------------------- |
| gs-020 | Moderaterna       | defense  | support | M vill höja försvarsbudgeten till över 2% av BNP               |
| gs-021 | Socialdemokraterna | defense  | support | S stödjer ökat försvarsanslag                                  |
| gs-022 | Vänsterpartiet    | defense  | oppose  | V har historiskt motsatt sig NATO-medlemskap                   |

### Skatt

| id     | subject            | topics              | stance  | claim_text                                                |
| ------ | ------------------ | -------------------- | ------- | --------------------------------------------------------- |
| gs-030 | Moderaterna        | taxation, economy    | support | M vill sänka inkomstskatten                               |
| gs-031 | Vänsterpartiet     | taxation, economy    | oppose  | V motsätter sig skattesänkningar för höginkomsttagare      |
| gs-032 | Socialdemokraterna  | taxation, economy    | mixed   | S balanserar mellan skattehöjningar och tillväxt           |

### Kriminalitet

| id     | subject            | topics | stance  | claim_text                                                     |
| ------ | ------------------ | ------ | ------- | -------------------------------------------------------------- |
| gs-040 | Moderaterna        | crime  | support | M vill införa hårdare straff                                  |
| gs-041 | Sverigedemokraterna | crime  | support | SD vill skärpa straffen kraftigt                               |
| gs-042 | Vänsterpartiet     | crime  | oppose  | V prioriterar förebyggande åtgärder framför strängare straff   |

### Multi-topic (testar junction-tabellen)

| id     | subject       | topics                    | stance  | claim_text                                                 |
| ------ | ------------- | ------------------------- | ------- | ---------------------------------------------------------- |
| gs-050 | Miljöpartiet  | climate, taxation         | support | MP vill införa högre koldioxidskatt                        |
| gs-051 | Centerpartiet | energy, climate, economy  | support | C vill satsa på förnybar energi och grön omställning       |
| gs-052 | Moderaterna   | crime, migration          | support | M kopplar ihop ökad brottslighet med invandringspolitiken  |

## Acceptanskriterier

- **Precision**: ≥ 80% av extraherade claims matchar golden set.
- **Recall**: ≥ 70% av golden set claims hittas av LLM.
- **Konsistens**: ≥ 90% samma output vid 3 körningar på samma input.
- **Multi-topic**: LLM ska identifiera ≥ 2 topics korrekt på multi-topic-exemplen.

## Nästa steg

1. Hämta faktiska textstycken från Riksdagens motioner för varje gs-entry.
2. Fyll i `source_text` och `evidence_quote` med riktiga citat.
3. Kör extraction-prompten och mät mot acceptanskriterierna.
4. Iterera på prompten tills trösklar nås.
