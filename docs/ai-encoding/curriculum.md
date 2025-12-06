# Curriculum Learning

The AI encoder learns progressively, starting with simple rules and building to complex ones. This curriculum design enables transfer learning and efficient training.

## Curriculum Design

### Stage 1: Simple, Isolated Rules

```python
{
    'rules': ['standard_deduction', 'personal_exemption'],
    'test_complexity': 'basic',
    'n_tests': 100,
    'max_iterations': 50,
}
```

**Characteristics:**
- Single formula
- No dependencies on other rules
- Clear statutory text
- Straightforward parameters

**Examples:**
- Standard deduction amounts
- Filing status determination
- Age-based thresholds

### Stage 2: Rules with Phase-Outs

```python
{
    'rules': ['child_tax_credit', 'retirement_savings_credit'],
    'test_complexity': 'boundary',
    'n_tests': 500,
    'max_iterations': 100,
}
```

**Characteristics:**
- Income phase-outs
- Multiple parameters
- Boundary conditions
- Filing status variations

**Examples:**
- Child Tax Credit (phase-out at high income)
- Retirement Savings Contributions Credit
- Education credits

### Stage 3: Complex Interactions

```python
{
    'rules': ['eitc', 'amt'],
    'test_complexity': 'mixed',
    'n_tests': 2000,
    'max_iterations': 200,
}
```

**Characteristics:**
- Multiple interdependent variables
- Complex eligibility rules
- Interactions with other credits
- Edge cases

**Examples:**
- EITC (earned income, qualifying children, investment income limits)
- Alternative Minimum Tax
- Self-employment tax

### Stage 4: Full Integration

```python
{
    'rules': ['total_tax_liability'],
    'test_complexity': 'adversarial',
    'n_tests': 10000,
    'max_iterations': 500,
}
```

**Characteristics:**
- Aggregates multiple calculations
- Full Form 1040 logic
- All interactions
- End-to-end validation

## Test Case Generation Strategies

### Boundary Sampling

Focus on thresholds and phase-out points:

```python
def boundary_sample(n: int, metadata: RuleMetadata) -> list[TestCase]:
    """
    Sample around known thresholds and phase-outs.

    For EITC: income at 0, phase-in start, max credit,
    phase-out start, phase-out end, above eligibility.
    """
    boundaries = metadata.get_boundaries()
    cases = []

    for boundary in boundaries:
        # Just below, at, just above each boundary
        for delta in [-1, 0, 1]:
            inputs = base_inputs()
            inputs[boundary.variable] = boundary.value + delta
            cases.append(TestCase(inputs=inputs, boundary=boundary))

    return cases[:n]
```

### Edge Case Sampling

Known edge cases from oracle test suites:

```python
def edge_case_sample(n: int) -> list[TestCase]:
    """Known edge cases from oracle test suites."""
    return [
        # Zero income
        TestCase(inputs={'earned_income': 0, 'children': 2}),
        # Maximum values
        TestCase(inputs={'earned_income': 1_000_000, 'children': 0}),
        # Boundary filing statuses
        TestCase(inputs={'filing_status': 'married_filing_separately'}),
        # Investment income limit
        TestCase(inputs={'investment_income': 10_999}),
        TestCase(inputs={'investment_income': 11_001}),
        # ... more edge cases
    ][:n]
```

### Uniform Sampling

Random samples across input space:

```python
def uniform_sample(n: int, input_ranges: dict) -> list[TestCase]:
    """Random samples across valid input space."""
    cases = []
    for _ in range(n):
        inputs = {}
        for var, range_def in input_ranges.items():
            if range_def.type == 'continuous':
                inputs[var] = random.uniform(range_def.min, range_def.max)
            elif range_def.type == 'categorical':
                inputs[var] = random.choice(range_def.values)
            elif range_def.type == 'integer':
                inputs[var] = random.randint(range_def.min, range_def.max)
        cases.append(TestCase(inputs=inputs))
    return cases
```

### Mixed Strategy

Combine all strategies:

```python
def mixed_sample(n: int) -> list[TestCase]:
    return (
        uniform_sample(n // 3) +
        edge_case_sample(n // 3) +
        boundary_sample(n // 3)
    )
```

## Transfer Learning

### Federal → State Transfer

After encoding federal rules, state encoding is faster:

```python
def transfer_to_state(state: str, federal_agent: RuleEncodingAgent):
    """
    Many state rules reference federal calculations.
    Transfer learning accelerates encoding.
    """
    # Load state statute
    state_statute = load_statute(f'state/{state}/income_tax')

    # Federal rules as context
    federal_rules = federal_agent.encoded_rules

    # State-specific oracle
    state_oracle = PolicyEngineUS(state=state)

    # Transfer: state agent starts from federal patterns
    state_agent = RuleEncodingAgent(
        llm=federal_agent.llm,
        oracles=[state_oracle],
        prior_rules=federal_rules  # Transfer knowledge
    )

    return state_agent.encode(state_statute)
```

**Transfer Benefits:**

| State Type | Transfer Efficiency | Reason |
|------------|---------------------|--------|
| Conformity states (most) | High | Start with federal AGI |
| Partial conformity | Medium | Some federal, some unique |
| Independent (e.g., CA AMT) | Low | Unique calculations |

### Cross-Jurisdiction Transfer

Can a US-trained agent encode UK rules faster?

```python
def cross_jurisdiction_transfer():
    """
    Research question: Does US training help UK encoding?

    Hypothesis: General patterns transfer
    - Phase-out structures
    - Income brackets
    - Benefit cliffs

    But specifics don't:
    - UK Universal Credit vs US SNAP
    - Different entity structures
    """
    # Train on US
    us_agent = train_us_agent()

    # Test on UK
    uk_agent_from_scratch = train_uk_agent()
    uk_agent_transferred = train_uk_agent(prior_knowledge=us_agent)

    # Compare iterations to convergence
    print(f"From scratch: {uk_agent_from_scratch.iterations}")
    print(f"Transferred: {uk_agent_transferred.iterations}")
```

## Metrics

### Per-Rule Metrics

```python
@dataclass
class RuleEncodingMetrics:
    rule_name: str

    # Convergence
    iterations_to_success: int
    final_reward: float

    # Test coverage
    test_cases_passed: int
    test_cases_total: int
    pass_rate: float

    # Oracle agreement
    oracle_consensus_rate: float
    oracles_consulted: list[str]

    # Efficiency
    llm_tokens_used: int
    wall_clock_seconds: float
```

### Curriculum Metrics

```python
@dataclass
class CurriculumMetrics:
    stage: int

    # Coverage
    rules_encoded: int
    rules_attempted: int
    success_rate: float

    # Efficiency
    mean_iterations_per_rule: float
    mean_tokens_per_rule: int

    # Transfer
    iterations_vs_no_transfer: float  # Ratio (lower is better)
```

## Research Questions

The curriculum design raises research questions:

1. **Context efficiency**: How much statute text does the agent need? Full section? Just relevant paragraphs?

2. **Test case diversity**: What's the minimum test set that catches 99% of bugs?

3. **Error feedback**: What failure format leads to fastest fixes? Stack traces? Natural language? Examples?

4. **Curriculum transfer**: How much does learning simple rules help with complex ones?

5. **Cross-jurisdiction transfer**: Can a US-trained agent encode UK rules faster?

6. **Oracle disagreement**: When oracles disagree, which should we trust? Can we learn a meta-policy?

7. **Adversarial robustness**: Can we generate adversarial test cases that break encoded rules?

## Implementation Roadmap

### Phase 1: Verification Harness

- [ ] Connect PolicyEngine as oracle
- [ ] Implement test case generator
- [ ] Build reward function
- [ ] Create evaluation pipeline

### Phase 2: Single-Rule Encoding

- [ ] Encode standard deduction with agent
- [ ] Measure iterations to convergence
- [ ] Tune revision prompts
- [ ] Benchmark against manual encoding time

### Phase 3: Curriculum Learning

- [ ] Implement curriculum scheduler
- [ ] Encode 10 simple rules
- [ ] Encode 10 complex rules
- [ ] Measure transfer effects

### Phase 4: State Expansion

- [ ] Encode California state tax (complex)
- [ ] Encode Texas (no income tax, simple)
- [ ] Encode New York (high complexity)
- [ ] Measure cross-state transfer

### Phase 5: Production System

- [ ] CI integration (new legislation triggers encoding)
- [ ] Human review workflow
- [ ] Monitoring and alerting
- [ ] Documentation generation
