# RAC

DSL parser and executor for encoding tax and benefit law.

## Install

```bash
pip install -e .
```

## Usage

```python
from datetime import date
from rac import parse, compile, execute

# Parse source
module = parse('''
    variable gov/tax/rate:
        from 2024-01-01: 0.25

    variable gov/tax/liability:
        entity: person
        from 2024-01-01: income * gov/tax/rate
''')

# Compile for a date
ir = compile([module], as_of=date(2024, 6, 1))

# Execute against data
result = execute(ir, {"person": [{"id": 1, "income": 50000}]})
print(result.values["gov/tax/rate"])  # 0.25
```

## DSL syntax

```
# Entity declaration
entity person:
    age: int
    income: float
    household: -> household

entity household:
    members: [person]

# Variable with temporal values
variable gov/irs/standard_deduction:
    from 2023-01-01 to 2023-12-31: 13850
    from 2024-01-01: 14600

# Entity-scoped variable
variable person/tax_liability:
    entity: person
    from 2024-01-01:
        if income > 50000: income * 0.22
        else: income * 0.12

# Amendment (override existing variable)
amend gov/irs/standard_deduction:
    from 2024-01-01: 15000
```

## Structure

```
src/rac/
├── ast.py       # AST node definitions
├── parser.py    # Lexer and recursive descent parser
├── compiler.py  # Temporal resolution, dependency analysis
├── executor.py  # Evaluate IR against data
└── schema.py    # Entity/field schema definitions
```

## Tests

```bash
pytest tests/ -v
```

## Related repos

- **rac-us** - US statute encodings
- **rac-uk** - UK statute encodings

## Licence

Apache 2.0
