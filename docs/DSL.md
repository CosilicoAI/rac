# Cosilico DSL Specification

## Executive Summary

Cosilico uses a purpose-built domain-specific language for encoding tax and benefit rules. This is a deliberate choice over Python decorators (OpenFisca/PolicyEngine approach) for five strategic reasons:

1. **Safety** - Untrusted code (AI-generated, user-submitted, third-party) cannot escape the sandbox
2. **Multi-target compilation** - Clean IR enables Python, JS, WASM, SQL, Spark backends
3. **Legal-first design** - Citations are syntax, not comments
4. **AI-native** - Constrained grammar is easier to generate correctly and validate
5. **Formal verification** - Amenable to proving properties (monotonicity, boundedness)

This document specifies the language syntax, semantics, and tooling requirements.

---

## 1. Design Principles

### 1.1 Safety Over Flexibility

```
PRINCIPLE: Any .cosilico file can be executed without risk.
```

Unlike Python, where `@variable` decorated functions can import os, make network calls, or modify global state, Cosilico DSL is:
- **Pure** - No side effects, no I/O
- **Terminating** - No unbounded recursion or loops
- **Bounded** - Memory and compute limits enforceable
- **Sandboxed** - No access to filesystem, network, or system calls

This enables:
- Running user-submitted reforms in production
- AI agents writing rules without human review for safety (only correctness)
- Third-party jurisdiction packages without security audits

### 1.2 Compilation Over Interpretation

```
PRINCIPLE: Rules are compiled, not interpreted.
```

The DSL compiles to an Intermediate Representation (IR) that is then code-generated to targets:

```
.cosilico files → Parser → IR → Optimizer → Code Generator → Target
                                                              ├── Python (NumPy)
                                                              ├── JavaScript (TypedArrays)
                                                              ├── WASM (native)
                                                              ├── SQL (CTEs)
                                                              └── Spark (PySpark)
```

Benefits:
- Same rules run everywhere
- Target-specific optimizations (vectorization for Python, loops for JS)
- Catch errors at compile time, not runtime

### 1.3 Citations as Syntax

```
PRINCIPLE: Every rule traces to law.
```

Legal citations are not documentation strings or comments—they are part of the language grammar:

```cosilico
# Citation is required, compiler enforces
variable eitc_phase_in_rate {
  reference "26 USC § 32(b)(1)(A)"
  # ...
}

# Formula components can have inline citations
formula {
  let base_amount = parameter(gov.irs.eitc.max_amount)  # 26 USC § 32(b)(2)
}
```

This enables:
- Automated compliance checking ("which rules implement § 32?")
- Impact analysis ("what breaks if § 32(b) changes?")
- Audit trails ("why did this household get $3,200?")

### 1.4 AI-Native Grammar

```
PRINCIPLE: Optimize for AI generation and review.
```

The syntax is designed for:
- **Unambiguous parsing** - No context-dependent grammar
- **Structural consistency** - Same patterns everywhere
- **Explicit over implicit** - No magic, no defaults that hide behavior
- **Diff-friendly** - Changes are localized, reviewable

```cosilico
# Good: explicit, structural, unambiguous
variable income_tax {
  entity TaxUnit
  period Year
  dtype Money
  reference "26 USC § 1"

  formula {
    let agi = variable(adjusted_gross_income)
    let brackets = parameter(gov.irs.income.brackets)
    return brackets.marginal_rate(agi)
  }
}

# Bad (what we're avoiding): implicit, magical
@variable
def income_tax(tax_unit, period):
    return tax_unit("agi", period).apply(brackets)  # Where does brackets come from?
```

---

## 2. Language Specification

### 2.1 File Structure

Files use `.cosilico` extension and follow this structure:

```cosilico
# rules/us/federal/irs/credits/eitc.cosilico

# File metadata
module us.federal.irs.credits.eitc
version "2024.1"
jurisdiction us

# Imports
import us.federal.irs.income (adjusted_gross_income, earned_income)
import us.federal.irs.filing (filing_status)

# Variable definitions
variable eitc { ... }
variable eitc_phase_in { ... }
variable eitc_phase_out { ... }

# Tests (inline, for documentation and validation)
test "Single filer, $15k income" {
  given {
    person alice { age: 30, employment_income: 15000 }
    tax_unit { members: [alice], filing_status: single }
  }
  expect {
    eitc: 1502  # From IRS EITC tables
  }
}
```

### 2.2 Variable Definitions

```cosilico
variable <name> {
  # Required metadata
  entity <EntityType>           # Person, TaxUnit, Household, etc.
  period <PeriodType>           # Year, Month, Day, Eternity
  dtype <DataType>              # Money, Rate, Count, Bool, Enum
  reference "<citation>"        # Legal citation (required)

  # Optional metadata
  label "<human readable>"
  description "<longer description>"
  unit "<unit>"                 # "USD", "GBP", "%", "people"

  # Formula (optional - inputs have no formula)
  formula {
    <expression>
  }

  # Conditional applicability (optional)
  defined_for {
    <boolean expression>
  }

  # Default value (optional, defaults to 0/false/null by dtype)
  default <value>
}
```

**Example:**

```cosilico
variable eitc {
  entity TaxUnit
  period Year
  dtype Money
  reference "26 USC § 32"
  label "Earned Income Tax Credit"
  description "Refundable credit for low-to-moderate income workers"
  unit "USD"

  formula {
    let phase_in = variable(eitc_phase_in)
    let phase_out = variable(eitc_phase_out)
    return max(0, phase_in - phase_out)
  }

  defined_for {
    variable(is_tax_filer) and variable(earned_income) > 0
  }

  default 0
}
```

### 2.3 Data Types

| Type | Description | Literal Syntax | Example |
|------|-------------|----------------|---------|
| `Money` | Currency amount (cents precision) | `1234.56` | `eitc`, `income_tax` |
| `Rate` | Decimal rate (0.0 to 1.0 typical) | `0.15` | `marginal_rate` |
| `Percent` | Percentage (0 to 100) | `15%` | Display-friendly rate |
| `Count` | Non-negative integer | `3` | `num_dependents` |
| `Int` | Signed integer | `-5` | `age_difference` |
| `Bool` | Boolean | `true`, `false` | `is_eligible` |
| `Enum(T)` | Enumerated type | `single`, `married` | `filing_status` |
| `Date` | Calendar date | `2024-01-01` | `birth_date` |
| `String` | Text (limited use) | `"California"` | `state_name` |

**Type Coercion Rules:**
- `Int` → `Money`: Implicit (dollars)
- `Rate` → `Percent`: Explicit (`rate.as_percent`)
- `Count` → `Int`: Implicit
- All others: Explicit conversion required

### 2.4 Expressions

#### Arithmetic
```cosilico
a + b       # Addition
a - b       # Subtraction
a * b       # Multiplication
a / b       # Division (Money / Money = Rate, Money / Rate = Money)
a % b       # Modulo
-a          # Negation
abs(a)      # Absolute value
```

#### Comparison
```cosilico
a == b      # Equal
a != b      # Not equal
a < b       # Less than
a <= b      # Less than or equal
a > b       # Greater than
a >= b      # Greater than or equal
```

#### Logical
```cosilico
a and b     # Logical AND
a or b      # Logical OR
not a       # Logical NOT
```

#### Conditional
```cosilico
if condition then value_if_true else value_if_false

# Multi-way conditional
match {
  case condition1 => value1
  case condition2 => value2
  else => default_value
}
```

#### Clamping and Rounding
```cosilico
min(a, b, ...)      # Minimum
max(a, b, ...)      # Maximum
clamp(x, lo, hi)    # Equivalent to max(lo, min(x, hi))
floor(x)            # Round down
ceil(x)             # Round up
round(x)            # Round to nearest
round(x, 2)         # Round to 2 decimal places
```

### 2.5 Variable References

```cosilico
# Same entity, same period
variable(earned_income)

# Same entity, different period
variable(earned_income, period - 1)        # Previous year
variable(earned_income, period.january)     # January of this year

# Different entity (aggregation)
person.sum(employment_income)               # Sum across all persons
person.max(age)                            # Maximum age
person.any(is_disabled)                    # True if any person is disabled
person.all(is_citizen)                     # True if all persons are citizens
person.count()                             # Number of persons
person.count(is_dependent)                 # Number of dependents

# Filtered aggregation
person.sum(employment_income, where: is_adult)
person.count(where: age < 17)

# Role-based access
person.first(where: role == head).age      # Age of head of household
spouse.employment_income                    # Spouse's income (if exists)
```

### 2.6 Parameter References

```cosilico
# Simple parameter
parameter(gov.irs.eitc.max_amount)

# Parameterized by filing status
parameter(gov.irs.income.brackets[filing_status])

# Bracket scale operations
let brackets = parameter(gov.irs.income.brackets)
brackets.marginal_rate(taxable_income)     # Tax via marginal rates
brackets.threshold_at(index: 2)            # Get 3rd bracket threshold
brackets.rate_at(income: 50000)            # Rate at $50k income
```

### 2.7 Let Bindings

Local variable bindings for readability:

```cosilico
formula {
  let agi = variable(adjusted_gross_income)
  let exemptions = variable(num_exemptions) * parameter(gov.irs.exemption_amount)
  let taxable = max(0, agi - exemptions)
  return parameter(gov.irs.brackets).marginal_rate(taxable)
}
```

### 2.8 Entity Operations

#### Aggregation (child → parent)
```cosilico
# From Person to TaxUnit
tax_unit.members.sum(employment_income)
tax_unit.members.max(age)
tax_unit.members.any(is_blind)
tax_unit.members.count()
tax_unit.members.count(where: age < 17)
```

#### Broadcast (parent → child)
```cosilico
# From TaxUnit to Person
tax_unit.filing_status    # Available on each person in the unit
household.state_name      # Available on each person in the household
```

### 2.9 Period Operations

```cosilico
# Period arithmetic
period - 1                    # Previous year
period + 1                    # Next year
period.month(1)               # January of period's year

# Period conversion
variable(monthly_income).sum_over(period)    # Sum 12 months to year
variable(annual_income) / 12                  # Divide year to month

# Cross-period references
variable(income_tax, period - 1)              # Last year's tax
variable(avg_income, period - 3 to period - 1)  # 3-year lookback average
```

---

## 3. Built-in Functions

### 3.1 Mathematical
```cosilico
abs(x)          # Absolute value
min(a, b, ...)  # Minimum of values
max(a, b, ...)  # Maximum of values
clamp(x, lo, hi) # Constrain to range
floor(x)        # Round down to integer
ceil(x)         # Round up to integer
round(x)        # Round to nearest integer
round(x, n)     # Round to n decimal places
sqrt(x)         # Square root (rarely needed)
```

### 3.2 Logical
```cosilico
if_else(cond, true_val, false_val)  # Ternary
coalesce(a, b, ...)                  # First non-null value
is_null(x)                           # Check for null/missing
```

### 3.3 Bracket Scales
```cosilico
scale.marginal_rate(amount)          # Calculate tax via marginal rates
scale.average_rate(amount)           # Calculate average tax rate
scale.threshold_at(index)            # Get threshold at index
scale.rate_at(amount)                # Get marginal rate for amount
scale.tax_at(amount)                 # Get cumulative tax up to amount
```

### 3.4 Date Functions
```cosilico
age_in_years(birth_date, as_of)     # Calculate age
days_between(date1, date2)           # Days between dates
year_of(date)                        # Extract year
month_of(date)                       # Extract month (1-12)
```

---

## 4. Control Flow

### 4.1 Conditional Expressions

```cosilico
# Simple if-else
if income > 50000 then high_rate else low_rate

# Match expression (exhaustive)
match filing_status {
  case single => 12950
  case married_filing_jointly => 25900
  case married_filing_separately => 12950
  case head_of_household => 19400
}

# Match with guards
match {
  case age >= 65 and is_blind => 3700
  case age >= 65 or is_blind => 1850
  else => 0
}
```

### 4.2 No Loops

The DSL intentionally has **no loops**. Iteration is handled through:
- Entity aggregations (`person.sum(...)`)
- Period ranges (`sum_over(period - 5 to period)`)
- Recursion is not supported (all dependencies must be DAG)

This ensures:
- All computations terminate
- Dependency graph is statically analyzable
- Vectorization is straightforward

---

## 5. Modules and Imports

### 5.1 Module Declaration

```cosilico
# Each file declares its module path
module us.federal.irs.credits.eitc

# Module path corresponds to file path:
# rules/us/federal/irs/credits/eitc.cosilico
```

### 5.2 Imports

```cosilico
# Import specific variables
import us.federal.irs.income (adjusted_gross_income, earned_income)

# Import all from module
import us.federal.irs.income (*)

# Import with alias
import us.ca.ftb.credits.ca_eitc as state_eitc

# Import parameters
import parameters us.federal.irs (*)
```

### 5.3 Visibility

```cosilico
# Public (default) - visible to other modules
variable eitc { ... }

# Private - only visible within module
private variable eitc_internal_calc { ... }

# Internal - visible within jurisdiction package
internal variable eitc_phase_in { ... }
```

---

## 6. Testing

### 6.1 Inline Tests

```cosilico
test "EITC for single filer with one child" {
  reference "IRS Publication 596, Example 3"

  given {
    person adult {
      age: 30
      employment_income: 20000
    }
    person child {
      age: 5
    }
    tax_unit {
      members: [adult, child]
      filing_status: single
    }
    household {
      members: [adult, child]
      state: "TX"
    }
  }

  expect {
    earned_income: 20000
    eitc: 3584
    eitc_phase_in: 3584
    eitc_phase_out: 0
  }
}
```

### 6.2 Property Tests

```cosilico
property "EITC is non-negative" {
  for_all tax_unit {
    assert variable(eitc) >= 0
  }
}

property "EITC phases out to zero" {
  for_all tax_unit where variable(earned_income) > 60000 {
    assert variable(eitc) == 0
  }
}

property "Tax is monotonic in income" {
  for_all tax_unit, income1 < income2 {
    given { employment_income: income1 } as scenario1
    given { employment_income: income2 } as scenario2
    assert scenario1.income_tax <= scenario2.income_tax
  }
}
```

---

## 7. Parameters

Parameters are defined in YAML (not the DSL) for easier editing:

```yaml
# parameters/us/federal/irs/credits/eitc.yaml

gov.irs.eitc:
  max_amount:
    description: Maximum EITC by number of children
    reference: "26 USC § 32(b)(2)"
    unit: USD
    values:
      2024-01-01:
        0_children: 632
        1_child: 4213
        2_children: 6960
        3_or_more_children: 7830
      2023-01-01:
        0_children: 600
        1_child: 3995
        2_children: 6604
        3_or_more_children: 7430

  phase_in_rate:
    description: Phase-in rate by number of children
    reference: "26 USC § 32(b)(1)(A)"
    unit: rate
    values:
      2024-01-01:
        0_children: 0.0765
        1_child: 0.34
        2_children: 0.40
        3_or_more_children: 0.45
```

DSL references parameters:
```cosilico
let max_credit = parameter(gov.irs.eitc.max_amount[num_qualifying_children])
let phase_in_rate = parameter(gov.irs.eitc.phase_in_rate[num_qualifying_children])
```

---

## 8. Error Handling

### 8.1 Compile-Time Errors

The compiler catches:
- **Type errors**: `Money + Bool` is invalid
- **Period mismatches**: Monthly variable used where annual expected
- **Entity mismatches**: Person variable used in TaxUnit formula without aggregation
- **Missing citations**: Variables without `reference` field
- **Undefined references**: `variable(nonexistent)`
- **Circular dependencies**: A depends on B depends on A

```
error[E0001]: Type mismatch in formula
  --> rules/us/federal/irs/income_tax.cosilico:15:12
   |
15 |     return agi + is_blind
   |            ^^^^^^^^^^^^^ cannot add Money and Bool
   |
   = note: expected Money, found Bool
   = hint: did you mean to use a conditional? `if is_blind then ... else ...`
```

### 8.2 Validation Warnings

```
warning[W0001]: Missing unit specification
  --> rules/us/federal/irs/credits/eitc.cosilico:8:3
   |
 8 |   dtype Money
   |   ^^^^^^^^^^ Money type should specify unit (USD, GBP, etc.)
   |
   = hint: add `unit "USD"` for clarity

warning[W0002]: Test case may be outdated
  --> rules/us/federal/irs/credits/eitc.cosilico:45:1
   |
45 | test "EITC example" {
   | ^^^^^^^^^^^^^^^^^^^ test uses 2023 parameters but current year is 2024
```

---

## 9. Tooling Requirements

### 9.1 Language Server Protocol (LSP)

Full LSP implementation providing:
- **Completion**: Variables, parameters, keywords
- **Hover**: Type info, documentation, citations
- **Go to definition**: Jump to variable/parameter definition
- **Find references**: Where is this variable used?
- **Diagnostics**: Real-time error checking
- **Formatting**: Consistent code style
- **Rename**: Safe refactoring

### 9.2 Syntax Highlighting

Tree-sitter grammar for:
- VS Code extension
- Neovim integration
- GitHub rendering
- Web-based editors

### 9.3 CLI Tools

```bash
# Compile and validate
cosilico check rules/

# Run tests
cosilico test rules/

# Generate code for target
cosilico compile --target python rules/ -o dist/
cosilico compile --target javascript rules/ -o dist/
cosilico compile --target sql rules/ -o dist/

# Calculate specific variable
cosilico calc eitc --input situation.yaml

# Show dependency graph
cosilico deps income_tax --format dot | dot -Tpng > deps.png

# Find all rules citing a statute
cosilico refs "26 USC § 32"

# Diff two versions
cosilico diff v2023.1 v2024.1 --variables eitc
```

### 9.4 Web Playground

Interactive browser-based environment:
- Edit DSL code
- See compiled output (Python, JS)
- Run calculations
- Visualize dependency graph
- Share via URL

---

## 10. Migration Path

### 10.1 From Python (PolicyEngine/OpenFisca)

Automated migration tool:

```bash
# Convert Python variable to DSL
cosilico migrate python policyengine_us/variables/irs/credits/eitc.py

# Output:
# rules/us/federal/irs/credits/eitc.cosilico
```

The migrator handles:
- Decorator extraction → DSL structure
- Type inference from numpy operations
- Citation extraction from docstrings
- Test case generation from existing tests

### 10.2 Gradual Adoption

Support mixed codebases during transition:

```python
# Python code can import compiled DSL
from cosilico.compiled.us import eitc_formula

# DSL can reference "foreign" Python variables (with restrictions)
foreign us.legacy.complex_calculation {
  path: "policyengine_us.variables.legacy.complex"
  # Marked as untrusted, won't compile to WASM/SQL
}
```

---

## 11. Example: Complete EITC Implementation

```cosilico
# rules/us/federal/irs/credits/eitc.cosilico

module us.federal.irs.credits.eitc
version "2024.1"
jurisdiction us

import us.federal.irs.income (earned_income, adjusted_gross_income)
import us.federal.irs.filing (filing_status, is_joint)
import us.federal.irs.dependents (num_qualifying_children_for_eitc)

# Main EITC variable
variable eitc {
  entity TaxUnit
  period Year
  dtype Money
  unit "USD"
  reference "26 USC § 32"
  label "Earned Income Tax Credit"
  description "Refundable credit for low-to-moderate income working individuals and families"

  formula {
    let phase_in = variable(eitc_phase_in)
    let phase_out = variable(eitc_phase_out)
    let max_credit = variable(eitc_max_amount)

    return max(0, min(phase_in, max_credit) - phase_out)
  }

  defined_for {
    variable(earned_income) > 0 and
    variable(adjusted_gross_income) < parameter(gov.irs.eitc.agi_limit[filing_status])
  }

  default 0
}

# Phase-in calculation
variable eitc_phase_in {
  entity TaxUnit
  period Year
  dtype Money
  unit "USD"
  reference "26 USC § 32(a)(1)"

  formula {
    let earned = variable(earned_income)
    let rate = parameter(gov.irs.eitc.phase_in_rate[num_children_category])
    return earned * rate
  }
}

# Phase-out calculation
variable eitc_phase_out {
  entity TaxUnit
  period Year
  dtype Money
  unit "USD"
  reference "26 USC § 32(a)(2)"

  formula {
    let income = max(variable(earned_income), variable(adjusted_gross_income))
    let threshold = parameter(gov.irs.eitc.phase_out_start[filing_status, num_children_category])
    let rate = parameter(gov.irs.eitc.phase_out_rate[num_children_category])

    return max(0, (income - threshold) * rate)
  }
}

# Maximum credit by family size
variable eitc_max_amount {
  entity TaxUnit
  period Year
  dtype Money
  unit "USD"
  reference "26 USC § 32(b)(2)"

  formula {
    return parameter(gov.irs.eitc.max_amount[num_children_category])
  }
}

# Category for parameter lookup
private variable num_children_category {
  entity TaxUnit
  period Year
  dtype Enum(eitc_child_category)
  reference "26 USC § 32(b)"

  formula {
    let n = variable(num_qualifying_children_for_eitc)
    match {
      case n == 0 => eitc_child_category.none
      case n == 1 => eitc_child_category.one
      case n == 2 => eitc_child_category.two
      else => eitc_child_category.three_or_more
    }
  }
}

enum eitc_child_category {
  none
  one
  two
  three_or_more
}

# Tests
test "Single filer, no children, $8000 income" {
  reference "IRS Publication 596, Worksheet A"

  given {
    person worker { age: 28, employment_income: 8000 }
    tax_unit { members: [worker], filing_status: single }
  }

  expect {
    earned_income: 8000
    eitc_phase_in: 612          # 8000 * 0.0765
    eitc_max_amount: 632
    eitc_phase_out: 0
    eitc: 612
  }
}

test "Married filing jointly, 2 children, $35000 income" {
  reference "IRS EITC Assistant example"

  given {
    person parent1 { age: 35, employment_income: 25000 }
    person parent2 { age: 33, employment_income: 10000 }
    person child1 { age: 8 }
    person child2 { age: 5 }
    tax_unit {
      members: [parent1, parent2, child1, child2]
      filing_status: married_filing_jointly
    }
  }

  expect {
    earned_income: 35000
    num_qualifying_children_for_eitc: 2
    eitc_max_amount: 6960
    eitc: 5764
  }
}

property "EITC is bounded by max amount" {
  for_all tax_unit {
    assert variable(eitc) <= variable(eitc_max_amount)
  }
}

property "EITC is non-negative" {
  for_all tax_unit {
    assert variable(eitc) >= 0
  }
}
```

---

## 12. Future Extensions

### 12.1 Literate Programming Mode

For law-adjacent documentation:

```cosilico-lit
# Earned Income Tax Credit

Per [26 USC § 32](https://uscode.house.gov/view.xhtml?req=26+USC+32):

> (a) Allowance of credit
> In the case of an eligible individual, there shall be allowed as a
> credit against the tax imposed by this subtitle for the taxable year
> an amount equal to the credit percentage of so much of the taxpayer's
> earned income for the taxable year as does not exceed the earned
> income amount.

This translates to:

```cosilico
variable eitc {
  formula {
    let credit_pct = parameter(gov.irs.eitc.phase_in_rate)
    let earned = variable(earned_income)
    let cap = parameter(gov.irs.eitc.earned_income_amount)
    return credit_pct * min(earned, cap)
  }
}
```

The phase-out is defined in subsection (a)(2)...
```

### 12.2 Formal Verification

Integration with proof assistants:

```cosilico
# Compiler can generate Lean/Coq theorems
@verify monotonic(income_tax, with_respect_to: taxable_income)
@verify bounded(eitc, lower: 0, upper: 10000)
@verify equivalent(eitc, eitc_alternative_formula)
```

### 12.3 Probabilistic Extensions

For uncertainty quantification:

```cosilico
variable childcare_cost {
  dtype Money ~ LogNormal(mu: 8.5, sigma: 0.7)  # Distribution, not point estimate
  # ...
}
```

---

## Appendix A: Grammar (EBNF)

```ebnf
file = module_decl version_decl? jurisdiction_decl? import* definition* ;

module_decl = "module" module_path ;
version_decl = "version" string ;
jurisdiction_decl = "jurisdiction" identifier ;

import = "import" module_path "(" import_list ")" ("as" identifier)? ;
import_list = "*" | identifier ("," identifier)* ;

definition = variable_def | enum_def | test_def | property_def ;

variable_def = visibility? "variable" identifier "{" variable_body "}" ;
visibility = "private" | "internal" ;

variable_body =
  "entity" entity_type
  "period" period_type
  "dtype" data_type
  "reference" string
  ("label" string)?
  ("description" string)?
  ("unit" string)?
  ("formula" "{" expression "}")?
  ("defined_for" "{" expression "}")?
  ("default" literal)?
;

expression =
  | "let" identifier "=" expression
  | "if" expression "then" expression "else" expression
  | "match" match_body
  | binary_expr
  | unary_expr
  | call_expr
  | member_expr
  | literal
  | identifier
  | "(" expression ")"
;

(* ... additional grammar rules ... *)
```

---

## Appendix B: Comparison with Alternatives

| Feature | Cosilico DSL | Python Decorators | Catala | DMN/FEEL |
|---------|--------------|-------------------|--------|----------|
| Safety | ✅ Sandboxed | ❌ Full Python | ✅ Safe | ✅ Safe |
| Multi-target | ✅ 5 targets | ❌ Python only | ⚠️ 2 targets | ⚠️ Java mainly |
| Vectorization | ✅ Native | ⚠️ Manual NumPy | ❌ Scalar | ❌ Scalar |
| Citations | ✅ Syntax | ⚠️ Comments | ✅ Literate | ❌ None |
| IDE Support | ✅ LSP | ✅ Python tools | ⚠️ Limited | ✅ Tooling |
| Learning Curve | Medium | Low | High | Medium |
| Formal Verification | ✅ Planned | ❌ No | ✅ Yes | ❌ No |
| Time-varying Params | ✅ Native | ⚠️ Manual | ❌ No | ❌ No |
| Entity Hierarchies | ✅ Native | ⚠️ Manual | ❌ No | ❌ No |

---

## Appendix C: Implementation Roadmap

### Phase 1: Core Language (Q1)
- [ ] Grammar specification (EBNF)
- [ ] Tree-sitter parser
- [ ] Type system implementation
- [ ] Python code generator
- [ ] Basic CLI (`check`, `compile`)

### Phase 2: Tooling (Q2)
- [ ] LSP server
- [ ] VS Code extension
- [ ] Test runner
- [ ] Migration tool from Python

### Phase 3: Additional Targets (Q3)
- [ ] JavaScript generator
- [ ] SQL generator
- [ ] WASM generator (via Rust)

### Phase 4: Advanced Features (Q4)
- [ ] Literate programming mode
- [ ] Formal verification integration
- [ ] Web playground
- [ ] Spark generator

---

*This specification is a living document. Updates will track implementation progress and community feedback.*
