# Cosilico Documentation

Cosilico builds open-source infrastructure for modeling society in silico. We encode tax and benefit rules as executable code, organized by statute, enabling AI systems to understand and calculate government programs.

## What is Cosilico?

Cosilico is a rules engine that:

1. **Encodes law as code** - Tax credits, benefit programs, and regulatory requirements translated into executable formulas
2. **Organizes by statute** - Code structure mirrors legal structure, with paths like `us/irc/subtitle_a/.../§32/earned_income_credit`
3. **Compiles to multiple targets** - Same rules run in Python, JavaScript, SQL, and WebAssembly
4. **Versions everything** - Parameters, forecasts, and calculations are fully reproducible across time

## Key Concepts

### Statute-Organized Code

Unlike traditional codebases organized by calculation type, Cosilico organizes code by legal citation:

```
cosilico-us/
└── irc/
    └── subtitle_a/
        └── chapter_1/
            └── .../§32/           # EITC
                ├── (a)/(1)/       # Main credit formula
                ├── (a)/(2)/(A)/   # Phase-in calculation
                ├── (a)/(2)/(B)/   # Phase-out calculation
                └── (b)/(1)/       # Credit percentages (parameters)
```

The path IS the legal citation. `us/irc/.../§32/(a)/(1)/earned_income_credit` maps directly to "26 USC §32(a)(1)".

### References System

Variables declare dependencies through a named references block:

```python
references:
  federal_agi: us/irc/.../§62/(a)/adjusted_gross_income
  earned_income: us/irc/.../§32/(c)/(2)/(A)/earned_income
  credit_percentage: us/irc/.../§32/(b)/(1)/credit_percentage@2024-01-01

def initial_credit_amount() -> Money:
    return credit_percentage * min(earned_income, earned_income_amount)
```

### Multi-Jurisdiction Support

Each jurisdiction gets its own repository:

- `cosilico-us` - US federal
- `cosilico-us-ca` - California
- `cosilico-us-ny` - New York
- `cosilico-uk` - United Kingdom

The engine coordinates cross-jurisdiction calculations (e.g., federal AGI flowing to state returns).

## Getting Started

```bash
pip install cosilico cosilico-us cosilico-us-ca

from cosilico import Simulation

sim = Simulation(jurisdictions=["us", "us-ca"], year=2024)
result = sim.calculate(household)
```

## Learn More

- {doc}`getting-started/quickstart` - Calculate your first tax scenario
- {doc}`architecture/statute-organization` - How code maps to law
- {doc}`ai-encoding/overview` - How AI agents learn to encode rules
