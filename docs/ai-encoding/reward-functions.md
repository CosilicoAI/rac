# Reward Functions

The reward function is the core of AI-assisted encoding. It provides the signal that guides agents toward correct implementations.

## Two-Level Reward Structure

### Level 1: Structural Reward (Code Alignment)

Does the generated code follow the target DSL grammar and patterns?

```python
def structural_reward(generated_code: str) -> float:
    """
    Reward for syntactic and structural correctness.
    Fast to compute, provides shaping signal.
    """
    score = 0.0

    # Parses without errors (0.3)
    if parses_successfully(generated_code):
        score += 0.3

    # Uses correct DSL primitives (0.2)
    if uses_valid_primitives(generated_code):
        score += 0.2

    # Has required metadata (citations, periods) (0.2)
    if has_required_metadata(generated_code):
        score += 0.2

    # Follows naming conventions (0.1)
    if follows_naming_conventions(generated_code):
        score += 0.1

    # References declared dependencies (0.2)
    if references_valid_dependencies(generated_code):
        score += 0.2

    return score
```

**Components:**

| Check | Weight | What It Validates |
|-------|--------|-------------------|
| Parses | 0.3 | Valid DSL syntax |
| Primitives | 0.2 | Uses `variable()`, `parameter()`, etc. correctly |
| Metadata | 0.2 | Has `reference`, `entity`, `period`, `dtype` |
| Naming | 0.1 | Follows snake_case, no reserved words |
| Dependencies | 0.2 | All referenced variables exist |

### Level 2: Semantic Reward (Calculation Alignment)

Does the generated code produce correct outputs across test scenarios?

```python
def semantic_reward(
    generated_code: str,
    test_cases: list[TestCase],
    oracles: list[Oracle]
) -> float:
    """
    Reward for calculation correctness against oracles.
    This is the ground truth signal.
    """
    if not compiles(generated_code):
        return 0.0

    compiled_fn = compile_rule(generated_code)

    results = []
    for test in test_cases:
        expected = consensus_oracle_output(test.inputs, oracles)
        actual = compiled_fn(test.inputs)

        # Exact match for booleans/enums
        if test.output_type in ['boolean', 'enum']:
            results.append(1.0 if actual == expected else 0.0)

        # Tolerance-based for numerics
        elif test.output_type == 'numeric':
            if expected == 0:
                results.append(1.0 if abs(actual) < 0.01 else 0.0)
            else:
                relative_error = abs(actual - expected) / abs(expected)
                results.append(max(0.0, 1.0 - relative_error * 10))

    return sum(results) / len(results)
```

**Tolerance Handling:**

| Output Type | Matching | Rationale |
|-------------|----------|-----------|
| Boolean | Exact | True/False must be exact |
| Enum | Exact | Category must be exact |
| Money | 1% relative or $1 absolute | Rounding differences acceptable |
| Rate | 0.1% absolute | Small rate differences acceptable |
| Count | Exact | Integer counts must match |

### Combined Reward

```python
def reward(
    generated_code: str,
    test_cases: list[TestCase],
    oracles: list[Oracle],
    alpha: float = 0.3  # Weight for structural vs semantic
) -> float:
    """
    Combined reward balancing structure and correctness.

    Early training: higher alpha (more structural shaping)
    Late training: lower alpha (focus on correctness)
    """
    r_struct = structural_reward(generated_code)
    r_semantic = semantic_reward(generated_code, test_cases, oracles)

    return alpha * r_struct + (1 - alpha) * r_semantic
```

**Alpha Scheduling:**

| Training Stage | Alpha | Emphasis |
|----------------|-------|----------|
| Initial | 0.5 | Learn DSL structure |
| Middle | 0.3 | Balance structure and correctness |
| Late | 0.1 | Focus on calculation accuracy |
| Final | 0.0 | Pure correctness (structure assumed) |

## Failure Diagnosis

When tests fail, structured diagnosis helps the agent fix issues:

```python
def diagnose_failures(
    code: str,
    test_cases: list[TestCase]
) -> list[FailureDiagnosis]:
    """
    Analyze why specific test cases fail.
    Returns structured feedback for the LLM.
    """
    compiled = compile_rule(code)
    failures = []

    for test in test_cases:
        expected = oracle_output(test)
        actual = compiled(test.inputs)

        if not close_enough(expected, actual):
            failures.append(FailureDiagnosis(
                inputs=test.inputs,
                expected=expected,
                actual=actual,
                error_type=classify_error(expected, actual),
                likely_cause=hypothesize_cause(test, expected, actual)
            ))

    return failures
```

**Error Classification:**

| Error Type | Pattern | Likely Cause |
|------------|---------|--------------|
| `sign_error` | Expected positive, got negative | Missing `abs()` or wrong subtraction order |
| `off_by_factor` | Actual = N × Expected | Missing/extra multiplication |
| `threshold_miss` | Wrong near boundaries | Threshold value incorrect |
| `phase_out_error` | Wrong in high-income range | Phase-out formula wrong |
| `eligibility_error` | Should be 0, got value | Missing eligibility check |
| `rounding_error` | Close but not exact | Wrong rounding function |

## Revision Prompt

Failures feed back to the agent:

```python
def build_revision_prompt(
    current_code: str,
    failures: list[FailureDiagnosis],
    statute_text: str
) -> str:
    return f"""
You are encoding {rule_name} from statute into Cosilico DSL.

## Statute
{statute_text}

## Current Implementation
```cosilico
{current_code}
```

## Test Failures
{format_failures(failures)}

## Instructions
Analyze the failures and revise the implementation. Common issues:
- Threshold values not matching statute
- Phase-out calculations incorrect
- Missing eligibility conditions
- Wrong filing status handling

Return ONLY the corrected Cosilico DSL code.
"""
```

**Failure Formatting:**

```
Test: Single filer, $25,000 income
  Input: {filing_status: single, earned_income: 25000, children: 0}
  Expected EITC: $250
  Actual EITC: $0

  Error Type: eligibility_error
  Hypothesis: Phase-out threshold may be incorrect. Single filers with
              no children phase out between $15,270 and $17,640 (2024).
              At $25,000, credit should be fully phased out but
              implementation returns $0 suggesting eligibility failure.
```

## Partial Credit

Rather than binary pass/fail, partial credit encourages progress:

```python
def partial_credit(expected: float, actual: float) -> float:
    """
    Reward partial correctness to shape learning.
    """
    if expected == 0:
        return 1.0 if actual == 0 else max(0, 1 - abs(actual) / 100)

    relative_error = abs(actual - expected) / abs(expected)

    if relative_error < 0.001:  # <0.1% error
        return 1.0
    elif relative_error < 0.01:  # <1% error
        return 0.95
    elif relative_error < 0.05:  # <5% error
        return 0.8
    elif relative_error < 0.10:  # <10% error
        return 0.6
    elif relative_error < 0.25:  # <25% error
        return 0.3
    else:
        return 0.0
```

This means:
- Getting within 10% of the answer is better than being way off
- Agent learns to get close first, then refine

## Weighted Test Cases

Not all tests are equal:

```python
def weighted_semantic_reward(
    generated_code: str,
    test_cases: list[TestCase],
    oracles: list[Oracle]
) -> float:
    """
    Weight test cases by importance.
    """
    compiled_fn = compile_rule(generated_code)

    weighted_results = []
    for test in test_cases:
        expected = consensus_oracle_output(test.inputs, oracles)
        actual = compiled_fn(test.inputs)
        score = partial_credit(expected, actual)

        # Weight by test importance
        weight = test.weight or 1.0
        if test.source == 'irs_official':
            weight *= 2.0  # IRS examples are authoritative
        if test.is_boundary:
            weight *= 1.5  # Boundary cases are diagnostic
        if test.oracle_consensus == 'full':
            weight *= 1.2  # High-confidence oracle agreement

        weighted_results.append(score * weight)

    return sum(weighted_results) / sum(t.weight for t in test_cases)
```

## Metrics

Track reward components over training:

```python
@dataclass
class RewardMetrics:
    iteration: int

    # Structural
    parses: bool
    primitives_correct: bool
    metadata_complete: bool
    naming_correct: bool
    dependencies_valid: bool
    structural_score: float

    # Semantic
    tests_passed: int
    tests_total: int
    pass_rate: float
    mean_partial_credit: float
    semantic_score: float

    # Combined
    alpha: float
    combined_reward: float

    # Diagnosis
    failure_types: dict[str, int]  # Count by error type
    worst_test: str  # Most failed test case
```

Visualize these to understand what's working:
- If structural score is low, agent needs more DSL examples
- If semantic score plateaus, test cases may not be diagnostic enough
- If specific error types dominate, add targeted training data
