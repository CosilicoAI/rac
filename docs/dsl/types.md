# Data Types

## Available Types

| Type | Description | Example |
|------|-------------|---------|
| `Money` | Currency amount | `eitc`, `income_tax` |
| `Rate` | Decimal rate (0-1) | `marginal_rate` |
| `Percent` | Percentage (0-100) | Display-friendly |
| `Count` | Non-negative integer | `num_dependents` |
| `Int` | Signed integer | `age_difference` |
| `Bool` | Boolean | `is_eligible` |
| `Enum(T)` | Enumerated type | `filing_status` |
| `Date` | Calendar date | `birth_date` |

## Type Coercion

- `Int` → `Money`: Implicit
- `Rate` → `Percent`: Explicit (`rate.as_percent`)
- `Count` → `Int`: Implicit
- All others: Explicit conversion required

## Enums

```cosilico
enum filing_status {
  single
  married_filing_jointly
  married_filing_separately
  head_of_household
  qualifying_widow
}
```

## Units

Money types should specify units:

```cosilico
variable income_tax {
  dtype Money
  unit "USD"
  ...
}
```
