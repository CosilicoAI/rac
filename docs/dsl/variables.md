# Variables

Variables are the atomic units of calculation in Cosilico. Each variable maps to exactly one statutory clause.

## Variable Structure

```cosilico
variable <name> {
  # Required metadata
  entity <EntityType>           # Person, TaxUnit, Household
  period <PeriodType>           # Year, Month, Day
  dtype <DataType>              # Money, Rate, Count, Bool
  reference "<citation>"        # Legal citation (required)

  # Optional metadata
  label "<human readable>"
  description "<longer description>"
  unit "<unit>"                 # "USD", "%", "people"

  # Formula (optional - inputs have no formula)
  formula {
    <expression>
  }

  # Default value
  default <value>
}
```

## Example

```cosilico
variable earned_income_credit {
  entity TaxUnit
  period Year
  dtype Money
  unit "USD"
  reference "26 USC § 32(a)(1)"
  label "Earned Income Tax Credit"

  formula {
    return max(0, initial_credit_amount - credit_reduction_amount)
  }

  default 0
}
```

## References Block

Variables declare dependencies through references:

```cosilico
references:
  agi: us/irc/.../§62/(a)/adjusted_gross_income
  prior_agi: us/irc/.../§62/(a)/adjusted_gross_income@year-1
  credit_percentage: us/irc/.../§32/(b)/(1)/credit_percentage
```

See {doc}`../architecture/references` for full details.
