# Formulas

Formulas define how variables are calculated using a pure expression language.

## Expressions

### Arithmetic
```cosilico
a + b       # Addition
a - b       # Subtraction
a * b       # Multiplication
a / b       # Division
-a          # Negation
abs(a)      # Absolute value
```

### Comparison
```cosilico
a == b      # Equal
a != b      # Not equal
a < b       # Less than
a <= b      # Less than or equal
a > b       # Greater than
a >= b      # Greater than or equal
```

### Logical
```cosilico
a and b     # Logical AND
a or b      # Logical OR
not a       # Logical NOT
```

### Conditional
```cosilico
if condition then value_if_true else value_if_false

match {
  case condition1 => value1
  case condition2 => value2
  else => default_value
}
```

### Built-in Functions
```cosilico
min(a, b, ...)      # Minimum
max(a, b, ...)      # Maximum
clamp(x, lo, hi)    # Constrain to range
floor(x)            # Round down
ceil(x)             # Round up
round(x, n)         # Round to n decimals
```

## Let Bindings

Local variables for readability:

```cosilico
formula {
  let agi = adjusted_gross_income
  let exemptions = num_exemptions * exemption_amount
  let taxable = max(0, agi - exemptions)
  return brackets.marginal_rate(taxable)
}
```

## No Loops

The DSL has no loops. Iteration is handled through:
- Entity aggregations (`person.sum(...)`)
- Period ranges (`sum_over(period - 5 to period)`)

This ensures all computations terminate.
