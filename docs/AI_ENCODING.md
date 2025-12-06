# AI-Assisted Rules Encoding: Technical Architecture

## Overview

This document describes the reinforcement learning framework for training AI agents to encode statutory rules as executable code. PolicyEngine and other oracles serve as the reward function, enabling automated verification of generated rules.

## The Core Insight

Traditional rules-as-code requires manual translation: lawyers and engineers read statutes, write code. This doesn't scale.

We flip the paradigm: **use existing implementations as verification oracles to train AI agents that learn to encode rules directly from legislation.**

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Statute Text   │────▶│   AI Agent       │────▶│  Generated Code │
│  (26 USC § 32)  │     │  (Policy Model)  │     │  (Cosilico DSL) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
                        ┌──────────────────┐     ┌─────────────────┐
                        │  Reward Signal   │◀────│  Oracle Stack   │
                        │  (0.0 - 1.0)     │     │  (PE, TAXSIM)   │
                        └──────────────────┘     └─────────────────┘
```

## Reward Function Design

### Two-Level Reward Structure

The reward function operates at two levels:

#### Level 1: Code Alignment (Structural Reward)

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

#### Level 2: Calculation Alignment (Semantic Reward)

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

    # Run against all test cases
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

#### Combined Reward

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

## Oracle Stack

Multiple independent implementations provide robust ground truth:

| Oracle | Coverage | Role |
|--------|----------|------|
| **PolicyEngine-US** | Federal + 50 states, benefits | Primary oracle, comprehensive |
| **PolicyEngine-UK** | UK taxes + benefits | Cross-jurisdiction validation |
| **TAXSIM (NBER)** | Federal + state income tax | Academic gold standard |
| **IRS Published Examples** | Official scenarios | Authoritative edge cases |
| **State DOR Calculators** | State-specific | State-level validation |

### Consensus Mechanism

When oracles disagree:

```python
def consensus_oracle_output(
    inputs: dict,
    oracles: list[Oracle],
    tolerance: float = 0.01
) -> tuple[float, float]:
    """
    Returns (consensus_value, confidence).

    High confidence: all oracles agree within tolerance
    Medium confidence: majority agree
    Low confidence: significant disagreement (flag for human review)
    """
    outputs = [oracle.calculate(inputs) for oracle in oracles]

    # Check for consensus
    clusters = cluster_by_tolerance(outputs, tolerance)

    if len(clusters) == 1:
        return (mean(outputs), 1.0)  # Full consensus

    largest_cluster = max(clusters, key=len)
    if len(largest_cluster) > len(outputs) / 2:
        return (mean(largest_cluster), 0.7)  # Majority consensus

    # No consensus - flag for review
    log_disagreement(inputs, outputs, oracles)
    return (median(outputs), 0.3)  # Low confidence
```

Oracle disagreements are valuable signal - they surface:
- Edge cases in statute interpretation
- Bugs in existing implementations
- Ambiguities requiring legal judgment

## Test Case Generation

### Scenario Sampling Strategies

```python
class TestCaseGenerator:
    def __init__(self, oracles: list[Oracle], rule_metadata: RuleMetadata):
        self.oracles = oracles
        self.metadata = rule_metadata

    def generate(self, n: int, strategy: str = 'mixed') -> list[TestCase]:
        if strategy == 'uniform':
            return self._uniform_sample(n)
        elif strategy == 'edge':
            return self._edge_case_sample(n)
        elif strategy == 'boundary':
            return self._boundary_sample(n)
        elif strategy == 'mixed':
            return (
                self._uniform_sample(n // 3) +
                self._edge_case_sample(n // 3) +
                self._boundary_sample(n // 3)
            )

    def _boundary_sample(self, n: int) -> list[TestCase]:
        """
        Sample around known thresholds and phase-outs.

        For EITC: income at 0, phase-in start, max credit,
        phase-out start, phase-out end, above eligibility.
        """
        boundaries = self.metadata.get_boundaries()
        cases = []

        for boundary in boundaries:
            # Just below, at, just above each boundary
            for delta in [-1, 0, 1]:
                inputs = self._base_inputs()
                inputs[boundary.variable] = boundary.value + delta
                cases.append(TestCase(inputs=inputs, boundary=boundary))

        return cases[:n]

    def _edge_case_sample(self, n: int) -> list[TestCase]:
        """
        Known edge cases from oracle test suites.
        """
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

### Curriculum Design

Start simple, progressively increase complexity:

```python
CURRICULUM = [
    # Stage 1: Simple, isolated rules
    {
        'rules': ['standard_deduction', 'personal_exemption'],
        'test_complexity': 'basic',
        'n_tests': 100,
        'max_iterations': 50,
    },

    # Stage 2: Rules with phase-outs
    {
        'rules': ['child_tax_credit', 'retirement_savings_credit'],
        'test_complexity': 'boundary',
        'n_tests': 500,
        'max_iterations': 100,
    },

    # Stage 3: Complex interactions
    {
        'rules': ['eitc', 'amt'],
        'test_complexity': 'mixed',
        'n_tests': 2000,
        'max_iterations': 200,
    },

    # Stage 4: Full integration
    {
        'rules': ['total_tax_liability'],
        'test_complexity': 'adversarial',
        'n_tests': 10000,
        'max_iterations': 500,
    },
]
```

## Agent Architecture

### Iterative Refinement Loop

This is NOT one-shot generation. The agent iterates:

```python
class RuleEncodingAgent:
    def __init__(
        self,
        llm: LanguageModel,
        oracles: list[Oracle],
        max_iterations: int = 20
    ):
        self.llm = llm
        self.oracles = oracles
        self.max_iterations = max_iterations

    def encode(
        self,
        statute_text: str,
        rule_name: str,
        existing_rules: dict[str, Rule]
    ) -> EncodingResult:
        """
        Iteratively encode a statute section into executable code.
        """
        test_cases = self.generate_test_cases(rule_name)

        # Initial generation
        context = self.build_context(statute_text, existing_rules)
        generated = self.llm.generate(context)

        history = []

        for iteration in range(self.max_iterations):
            # Evaluate
            r = reward(generated, test_cases, self.oracles)
            history.append({'code': generated, 'reward': r, 'iteration': iteration})

            # Success?
            if r >= 0.99:
                return EncodingResult(
                    code=generated,
                    success=True,
                    iterations=iteration,
                    history=history
                )

            # Diagnose failures
            failures = self.diagnose_failures(generated, test_cases)

            # Generate revision
            revision_prompt = self.build_revision_prompt(
                generated, failures, statute_text
            )
            generated = self.llm.generate(revision_prompt)

        # Max iterations reached
        return EncodingResult(
            code=generated,
            success=False,
            iterations=self.max_iterations,
            history=history,
            needs_review=True
        )

    def diagnose_failures(
        self,
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
            expected = self.oracle_output(test)
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

### Revision Prompt Structure

```python
def build_revision_prompt(
    self,
    current_code: str,
    failures: list[FailureDiagnosis],
    statute_text: str
) -> str:
    return f"""
You are encoding {self.rule_name} from statute into Cosilico DSL.

## Statute
{statute_text}

## Current Implementation
```cosilico
{current_code}
```

## Test Failures
{self.format_failures(failures)}

## Instructions
Analyze the failures and revise the implementation. Common issues:
- Threshold values not matching statute
- Phase-out calculations incorrect
- Missing eligibility conditions
- Wrong filing status handling

Return ONLY the corrected Cosilico DSL code.
"""
```

## Optimization Targets

We optimize the agent workflow, not model weights:

| Component | What to Optimize | Metrics |
|-----------|------------------|---------|
| **Context window** | What statute context helps most | Iterations to convergence |
| **Error formatting** | How to present failures to LLM | Fix rate per iteration |
| **Test selection** | Which test cases are most diagnostic | Failure detection rate |
| **Revision prompts** | Instructions that lead to fixes | Reward improvement per iteration |
| **Curriculum order** | Which rules to learn first | Transfer to new rules |

## Scaling Strategy

### Within US Tax Code

```
Phase 1: Simple provisions (standard deduction, brackets)
    ↓
Phase 2: Credits with phase-outs (CTC, EITC, education)
    ↓
Phase 3: Complex calculations (AMT, NIIT, self-employment)
    ↓
Phase 4: Full integration (Form 1040 line-by-line)
```

### Cross-Jurisdiction Transfer

Once trained on US federal:

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

### New Legislation (No Oracle)

For brand-new legislation with no existing implementation:

```python
def encode_new_legislation(bill_text: str) -> EncodingResult:
    """
    When no oracle exists, use:
    1. Similar existing rules as templates
    2. Explicit examples from legislative text
    3. Human-in-the-loop validation
    """
    # Find similar encoded rules
    similar = find_similar_rules(bill_text, rule_database)

    # Extract any examples from bill text
    examples = extract_examples(bill_text)

    # Generate with lower confidence threshold
    result = agent.encode(
        statute_text=bill_text,
        template_rules=similar,
        explicit_examples=examples,
        confidence_threshold=0.8  # Lower than normal
    )

    # Flag for human review
    result.needs_review = True
    result.review_reason = "No oracle available for validation"

    return result
```

## Evaluation Metrics

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

### System-Level Metrics

```python
@dataclass
class SystemMetrics:
    # Coverage
    rules_encoded: int
    rules_attempted: int
    success_rate: float

    # Accuracy
    mean_test_pass_rate: float
    rules_above_99_percent: int

    # Efficiency
    mean_iterations_per_rule: float
    mean_tokens_per_rule: int

    # Transfer
    state_rules_encoded: int
    transfer_efficiency: float  # iterations saved vs from-scratch
```

## Research Questions

1. **Context efficiency**: How much statute text does the agent need? Full section? Just relevant paragraphs?

2. **Test case diversity**: What's the minimum test set that catches 99% of bugs?

3. **Error feedback**: What failure format leads to fastest fixes? Stack traces? Natural language? Examples?

4. **Curriculum transfer**: How much does learning simple rules help with complex ones?

5. **Cross-jurisdiction transfer**: Can a US-trained agent encode UK rules faster?

6. **Oracle disagreement**: When oracles disagree, which should we trust? Can we learn a meta-policy?

7. **Adversarial robustness**: Can we generate adversarial test cases that break encoded rules?

## Implementation Roadmap

### Phase 1: Verification Harness (Current)
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
