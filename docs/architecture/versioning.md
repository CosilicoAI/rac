# Versioning

Cosilico implements **full bi-temporal versioning** across all inputs. This enables complete reproducibility of any historical simulation.

## The Reproducibility Problem

A simulation depends on many inputs that change over time:

| Input Type | Example | Changes when? |
|------------|---------|---------------|
| Statutory parameters | EITC rates | Congress passes law |
| Inflation-adjusted | Tax brackets | IRS publishes annually |
| Economic indices | CPI-U | BLS publishes monthly |
| Forecasts | Projected CPI | CBO updates quarterly |
| Microdata | CPS ASEC | Census releases annually |

To reproduce a simulation from June 2024, you need ALL inputs as they existed in June 2024.

## Bi-Temporal Model

Every value has two time dimensions:

- **Effective date**: When the value applies (e.g., "2025 tax year")
- **Knowledge date**: When we knew this value (e.g., "as of June 2024")

```
┌─────────────────────────────────────────────────────────┐
│                     Knowledge Date                       │
│              2024-02      2024-06      2024-11          │
├─────────────┬────────────┬────────────┬─────────────────┤
│ Effective   │            │            │                 │
│ Date        │            │            │                 │
├─────────────┼────────────┼────────────┼─────────────────┤
│ 2024        │ Projected  │ Projected  │ Published       │
│             │ $11,850    │ $11,920    │ $11,600         │
├─────────────┼────────────┼────────────┼─────────────────┤
│ 2025        │ Projected  │ Projected  │ Projected       │
│             │ $12,100    │ $12,175    │ $12,250         │
└─────────────┴────────────┴────────────┴─────────────────┘
```

## Simulation Manifests

Every simulation produces a manifest for complete reproducibility:

```yaml
simulation:
  id: "sim_2024_q2_eitc_expansion"
  created: 2024-06-15T14:30:00Z

temporal:
  effective_date: 2025-01-01      # Policy year being modeled
  knowledge_date: 2024-06-15      # All inputs as of this date

versions:
  engine:
    version: "1.2.3"
    commit: "a1b2c3d"

  rules:
    repo: cosilico/us-rules
    commit: "b2c3d4e"

  parameters:
    projection_vintage: 2024-06
    forecast_provider: cbo
    forecast_vintage: 2024-06

  microdata:
    dataset: cps_enhanced
    vintage: 2024-06
    manifest_checksum: sha256:abc123...
```

## CLI Usage

```bash
# Run with current knowledge (default)
cosilico sim reform.yaml --year 2025

# Pin to historical knowledge date
cosilico sim reform.yaml --year 2025 --knowledge-date 2024-06-15

# Specify forecast provider
cosilico sim reform.yaml --year 2025 --forecast-provider cbo --forecast-vintage 2024-06

# Full reproducibility from manifest
cosilico sim --manifest simulations/2024_q2/manifest.yaml

# Compare across vintages
cosilico diff reform.yaml \
  --knowledge-date 2024-02-15 \
  --vs-knowledge-date 2024-11-15
```

## Audit Trail

Every calculation includes full provenance:

```json
{
  "calculation": {
    "variable": "income_tax",
    "value": 8521.00,
    "effective_date": "2025-01-01",
    "knowledge_date": "2024-06-15"
  },

  "parameters_used": {
    "gov.irs.income.brackets.single": {
      "value": [11925, 48475, ...],
      "tier": "projected",
      "projection_vintage": "2024-06",
      "forecast_provider": "cbo"
    }
  }
}
```
