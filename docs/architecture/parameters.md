# Parameters

Parameters are time-varying policy values: rates, thresholds, brackets. They're stored separately from formulas and support multiple tiers (published, projected, statutory).

## Parameter Structure

```yaml
# us/irc/.../§32/(b)/(1)/parameters/credit_percentage.yaml

citation: 26 USC §32(b)(1)
description: EITC credit and phaseout percentages by number of children

values:
  2024-01-01:
    no_children:
      credit_rate: 0.0765
      phaseout_rate: 0.0765
    one_child:
      credit_rate: 0.34
      phaseout_rate: 0.1598
    two_children:
      credit_rate: 0.40
      phaseout_rate: 0.2106
    three_plus_children:
      credit_rate: 0.45
      phaseout_rate: 0.2106

source: IRS Rev. Proc. 2023-34
```

## Parameter Tiers

Parameters have a precedence hierarchy:

```
published > projected > statutory_calculation
```

### Published

Official government source values:

```yaml
published:
  2024-01-01:
    values: [11600, 47150, 100525, 191950, 243725, 609350]
    reference: "Rev. Proc. 2023-34"
```

### Projected

Our calculations using statute formula + forecasts:

```yaml
projected:
  2024-06:  # Vintage date
    method: statutory_inflation
    values:
      2025-01-01:
        values: [11925, 48475, 103350, 197300, 250525, 626350]
        inflation_index_used: chained_cpi
        forecast_provider: cbo
        forecast_vintage: 2024-06
```

### Statutory Calculation

On-the-fly from base year + inflation index:

```yaml
statute:
  - effective: 2018-01-01
    reference: "26 USC § 1(j)(2)"
    base_year: 2018
    base_values: [9525, 38700, 82500, 157500, 200000, 500000]
    inflation_index: chained_cpi
    rounding: -50
```

## Unknown Values

Explicitly mark unknown future values:

```yaml
published:
  2024-01-01:
    values: {...}
    reference: "Rev. Proc. 2023-34"

  2025-01-01: unknown  # IRS hasn't published yet

  2026-01-01:
    status: unknown
    reason: "TCJA sunset creates uncertainty"
    scenarios:
      tcja_extended: { values: [...] }
      tcja_sunset: { values: [...] }
```

## Time-Varying Indexation

The inflation index itself changes over time:

```yaml
indexation_rules:
  history:
    - effective: 1993-01-01
      expires: 2017-12-31
      index: cpi_u
      reference: "26 USC § 1(f)(3) (pre-TCJA)"

    - effective: 2018-01-01
      expires: 2025-12-31
      index: chained_cpi
      reference: "Tax Cuts and Jobs Act § 11002"

    - effective: 2026-01-01
      index: cpi_u  # Reverts unless Congress acts
```

TCJA switched from CPI-U to Chained CPI, resulting in ~0.25% slower bracket growth annually.

## Using Parameters in Code

Parameters are referenced like variables:

```python
references:
  credit_percentage: us/irc/.../§32/(b)/(1)/credit_percentage
  earned_income_amount: us/irc/.../§32/(b)/(2)/(A)/earned_income_amount

def initial_credit_amount() -> Money:
    return credit_percentage[qualifying_children] * min(
        earned_income,
        earned_income_amount[qualifying_children]
    )
```

The engine resolves the parameter value for the current period automatically.

## See Also

- {doc}`versioning` - Full bi-temporal versioning
- {doc}`references` - Vintage pinning syntax
