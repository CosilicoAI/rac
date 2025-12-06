# DSL Overview

Cosilico uses a purpose-built domain-specific language for encoding tax and benefit rules.

## Why a DSL?

1. **Safety** - Untrusted code cannot escape the sandbox
2. **Multi-target compilation** - Same rules run in Python, JS, SQL, WASM
3. **Legal-first design** - Citations are syntax, not comments
4. **AI-native** - Constrained grammar is easier to generate and validate
5. **Formal verification** - Amenable to proving properties

## File Structure

```cosilico
# Module declaration
module us.federal.irs.credits.eitc
version "2024.1"
jurisdiction us

# References (dependencies)
references:
  earned_income: us/irc/.../§32/(c)/(2)/(A)/earned_income
  credit_percentage: us/irc/.../§32/(b)/(1)/credit_percentage

# Variable definition
variable initial_credit_amount {
  entity TaxUnit
  period Year
  dtype Money
  unit "USD"
  reference "26 USC § 32(a)(2)(A)"

  formula {
    return credit_percentage * min(earned_income, earned_income_amount)
  }
}
```

## Key Concepts

- {doc}`variables` - The atomic units of calculation
- {doc}`formulas` - Expression language
- {doc}`types` - Data types and coercion
- {doc}`testing` - YAML test format
