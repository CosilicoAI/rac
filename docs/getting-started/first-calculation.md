# Your First Calculation

This guide walks through the calculation model in detail.

## Entities

Cosilico models society through entities:

- **Person** - An individual with age, income, etc.
- **TaxUnit** - Filing unit for tax purposes (can span multiple people)
- **Household** - Physical dwelling unit
- **SPMUnit** - Supplemental Poverty Measure unit (for benefits)

## Defining a Household

```python
household = {
    "people": {
        "parent": {
            "age": 35,
            "employment_income": 45000
        },
        "child": {
            "age": 8
        }
    },
    "tax_units": {
        "tax_unit": {
            "members": ["parent", "child"],
            "filing_status": "head_of_household"
        }
    },
    "households": {
        "household": {
            "members": ["parent", "child"],
            "state_name": "TX"
        }
    }
}
```

## Running a Simulation

```python
from cosilico import Simulation

sim = Simulation(jurisdictions=["us"], year=2024)
result = sim.calculate(household)
```

## Accessing Results

```python
# Scalar results
print(result.us.income_tax)
print(result.us.eitc)

# Per-person results
for person_id, person_result in result.us.people.items():
    print(f"{person_id}: {person_result.employment_income}")
```

## Tracing Calculations

See how a value was calculated:

```python
trace = sim.trace(household, "us.eitc")
print(trace)
```

Output shows the dependency chain and intermediate values.
