# Testing

Tests are written in YAML format, separate from rule definitions.

## Basic Test Format

```yaml
metadata:
  module: us.federal.irs.credits.eitc
  description: EITC test cases

tests:
  - name: Single filer, no children, $8000 income
    reference: IRS Publication 596
    period: 2024

    input:
      person:
        age: 28
        employment_income: 8000
      state: TX
      filing_status: single

    output:
      earned_income: 8000
      eitc: 612
```

## Property-Based Tests

```yaml
properties:
  - name: EITC is non-negative
    for_all:
      variables: [eitc]
      constraint: eitc >= 0

  - name: EITC bounded by max
    for_all:
      variables: [eitc, eitc_max_amount]
      constraint: eitc <= eitc_max_amount
```

## Running Tests

```bash
cosilico test tests/us/federal/
cosilico test --tag edge-case
cosilico test --properties
```
