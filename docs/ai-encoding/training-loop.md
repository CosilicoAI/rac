# Training Loop: Technical Specification

This document specifies the v1 training loop for the Cosilico AI rules engine.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Training Loop                                  │
│                                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ Statute  │───▶│ Code Gen │───▶│ Executor │───▶│ Scorer   │          │
│  │ Corpus   │    │ (LLM)    │    │          │    │          │          │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘          │
│       │              ▲                │               │                 │
│       │              │                ▼               ▼                 │
│       │         ┌────┴────┐     ┌──────────┐    ┌──────────┐          │
│       │         │ Failure │◀────│ Test     │    │ Metrics  │          │
│       │         │ Diagnoser│    │ Cases    │    │ Store    │          │
│       │         └─────────┘    └──────────┘    └──────────┘          │
│       │                              ▲                                  │
│       │                              │                                  │
│       │                        ┌──────────┐                            │
│       └───────────────────────▶│ Oracles  │                            │
│                                │ PE/TAXSIM│                            │
│                                └──────────┘                            │
└─────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Statute Corpus

Statutory text organized by citation path.

```python
@dataclass
class Statute:
    citation: str              # e.g., "26 USC § 32(a)(1)"
    text: str                  # Raw statutory text
    effective_date: date       # When this version took effect
    jurisdiction: str          # "us", "us-ca", etc.
    parent: Optional[str]      # Parent citation
    children: list[str]        # Child citations
```

**v1 scope**: Start with a single, well-defined provision. Candidate: EITC phase-in (`26 USC § 32(a)(1)`) - simple formula, clear oracle coverage.

### 2. Code Generator

The LLM-based component that produces Cosilico DSL from statute.

```python
class CodeGenerator:
    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.model = model
        self.dsl_spec = load_dsl_specification()
        self.examples = load_few_shot_examples()

    def generate(
        self,
        statute: Statute,
        context: list[str],          # Related already-encoded rules
        failures: list[Failure],      # Previous attempt failures
        temperature: float = 0.0
    ) -> GeneratedCode:
        prompt = self._build_prompt(statute, context, failures)
        response = self._call_llm(prompt, temperature)
        return self._parse_response(response)
```

**Prompt structure**:
```
SYSTEM: You are encoding tax law into executable code.

DSL SPECIFICATION:
{dsl_spec}

CONTEXT (already encoded rules):
{context}

PREVIOUS FAILURES (if any):
{failures}

STATUTE TO ENCODE:
Citation: {statute.citation}
Text: {statute.text}

Produce Cosilico DSL code for this provision. Include:
- Variable definition with proper entity and period
- Formula implementation
- Reference block for dependencies
- Citation in metadata

OUTPUT FORMAT:
```cosilico
[code here]
```
```

### 3. Executor

Runs generated code against test cases.

```python
class Executor:
    def execute(
        self,
        code: GeneratedCode,
        test_cases: list[TestCase]
    ) -> list[ExecutionResult]:
        # Parse and validate DSL
        parsed = parse_cosilico(code.source)
        if parsed.errors:
            return [ExecutionResult(error=e) for e in parsed.errors]

        # Compile to executable
        compiled = compile_to_python(parsed)

        # Run each test case
        results = []
        for case in test_cases:
            try:
                output = compiled.evaluate(case.inputs)
                results.append(ExecutionResult(
                    case_id=case.id,
                    output=output,
                    expected=case.expected,
                    match=self._compare(output, case.expected)
                ))
            except Exception as e:
                results.append(ExecutionResult(
                    case_id=case.id,
                    error=str(e)
                ))
        return results
```

### 4. Oracles

Interface to existing implementations.

```python
class Oracle(Protocol):
    def evaluate(self, inputs: dict) -> dict:
        """Given household inputs, return computed values."""
        ...

class PolicyEngineOracle:
    def __init__(self, country: str = "us"):
        from policyengine_us import Simulation
        self.Simulation = Simulation

    def evaluate(self, inputs: dict) -> dict:
        sim = self.Simulation(situation=inputs)
        return {
            var: sim.calculate(var, 2024)
            for var in self.output_variables
        }

class TaxsimOracle:
    def __init__(self):
        self.endpoint = "https://taxsim.nber.org/taxsim35/"

    def evaluate(self, inputs: dict) -> dict:
        # Convert to TAXSIM format and call API
        ...
```

**Oracle aggregation**: When oracles disagree, we need a strategy:

```python
class OracleConsensus:
    def __init__(self, oracles: list[Oracle], threshold: float = 0.99):
        self.oracles = oracles
        self.threshold = threshold

    def evaluate(self, inputs: dict) -> OracleResult:
        results = [o.evaluate(inputs) for o in self.oracles]

        # Check agreement
        if self._all_agree(results, tolerance=0.01):
            return OracleResult(value=results[0], confidence=1.0)

        # Disagreement - flag for human review
        return OracleResult(
            value=None,
            confidence=0.0,
            disagreement=results,
            needs_human_review=True
        )
```

### 5. Test Case Generator

Produces test households covering the input space.

```python
class TestCaseGenerator:
    def __init__(self, oracles: list[Oracle]):
        self.oracles = oracles

    def generate_for_provision(
        self,
        statute: Statute,
        n_cases: int = 1000
    ) -> list[TestCase]:
        # Identify relevant input variables from statute
        input_vars = self._extract_input_variables(statute)

        cases = []
        for _ in range(n_cases):
            inputs = self._sample_inputs(input_vars)
            expected = self._get_oracle_consensus(inputs)
            cases.append(TestCase(inputs=inputs, expected=expected))

        return cases

    def _sample_inputs(self, variables: list[str]) -> dict:
        """Sample from realistic distributions."""
        # Use CPS/SCF distributions for income, demographics
        # Include boundary values (0, thresholds, phase-out points)
        # Include adversarial cases
        ...
```

**Sampling strategies**:
1. **Uniform**: Even coverage of input space
2. **Importance**: Weight toward common scenarios (from CPS/ACS)
3. **Boundary**: Focus on thresholds, phase-in/out points
4. **Adversarial**: Edge cases designed to break naive implementations

### 6. Scorer

Computes metrics comparing generated code to oracles.

```python
class Scorer:
    def score(
        self,
        results: list[ExecutionResult]
    ) -> Score:
        # Syntax errors
        syntax_errors = [r for r in results if r.error and "parse" in r.error]

        # Runtime errors
        runtime_errors = [r for r in results if r.error and "parse" not in r.error]

        # Numerical accuracy
        correct = [r for r in results if r.match]
        incorrect = [r for r in results if not r.match and not r.error]

        return Score(
            syntax_pass_rate=1 - len(syntax_errors) / len(results),
            runtime_pass_rate=1 - len(runtime_errors) / len(results),
            accuracy=len(correct) / (len(correct) + len(incorrect)) if (correct or incorrect) else 0,
            mean_absolute_error=self._compute_mae(incorrect),
            max_error=self._compute_max_error(incorrect),
        )
```

### 7. Failure Diagnoser

Extracts structured failure information for the next iteration.

```python
class FailureDiagnoser:
    def diagnose(
        self,
        code: GeneratedCode,
        results: list[ExecutionResult]
    ) -> list[Failure]:
        failures = []

        for result in results:
            if result.error:
                failures.append(Failure(
                    type="error",
                    message=result.error,
                    case=result.case_id
                ))
            elif not result.match:
                failures.append(Failure(
                    type="value_mismatch",
                    expected=result.expected,
                    actual=result.output,
                    case=result.case_id,
                    analysis=self._analyze_mismatch(result)
                ))

        # Cluster similar failures
        return self._cluster_failures(failures)

    def _analyze_mismatch(self, result: ExecutionResult) -> str:
        """Produce human-readable analysis of why values differ."""
        # e.g., "Expected $3,000 but got $0. Input earned_income=$15,000
        # is above phase-in threshold, so credit should be positive."
        ...
```

## Training Loop

```python
class TrainingLoop:
    def __init__(
        self,
        generator: CodeGenerator,
        executor: Executor,
        oracles: list[Oracle],
        scorer: Scorer,
        diagnoser: FailureDiagnoser,
        max_iterations: int = 10,
        target_accuracy: float = 0.99
    ):
        self.generator = generator
        self.executor = executor
        self.oracles = oracles
        self.scorer = scorer
        self.diagnoser = diagnoser
        self.max_iterations = max_iterations
        self.target_accuracy = target_accuracy

    def train(
        self,
        statute: Statute,
        test_cases: list[TestCase],
        context: list[str] = []
    ) -> TrainingResult:
        failures = []
        history = []

        for i in range(self.max_iterations):
            # Generate code
            code = self.generator.generate(
                statute=statute,
                context=context,
                failures=failures
            )

            # Execute against test cases
            results = self.executor.execute(code, test_cases)

            # Score
            score = self.scorer.score(results)
            history.append(IterationRecord(
                iteration=i,
                code=code,
                score=score
            ))

            # Check success
            if score.accuracy >= self.target_accuracy:
                return TrainingResult(
                    success=True,
                    final_code=code,
                    iterations=i + 1,
                    history=history
                )

            # Diagnose for next iteration
            failures = self.diagnoser.diagnose(code, results)

        # Max iterations reached
        return TrainingResult(
            success=False,
            final_code=history[-1].code,
            iterations=self.max_iterations,
            history=history,
            remaining_failures=failures
        )
```

## Learning Modes

### Mode 1: Prompt Iteration (v1)

No model fine-tuning. Each iteration refines by providing failure context.

```python
# Simple iteration - failures become context
for i in range(max_iterations):
    code = generator.generate(statute, context, failures)
    results = executor.execute(code, test_cases)
    failures = diagnoser.diagnose(code, results)
```

**Pros**: Fast to implement, uses off-the-shelf models
**Cons**: No cross-provision learning, resets each statute

### Mode 2: Few-Shot Learning (v2)

Successfully encoded provisions become few-shot examples.

```python
class FewShotLearner:
    def __init__(self):
        self.examples = []

    def add_success(self, statute: Statute, code: GeneratedCode):
        self.examples.append((statute, code))

    def get_examples(self, statute: Statute, k: int = 3) -> list:
        # Return k most similar successful examples
        return self._find_similar(statute, k)
```

**Pros**: Improves with each success, generalizes patterns
**Cons**: Still no weight updates

### Mode 3: Fine-Tuning (v3)

Train model weights on successful encodings.

```python
class FineTuner:
    def create_training_data(
        self,
        successes: list[tuple[Statute, GeneratedCode]]
    ) -> Dataset:
        return Dataset([
            {
                "input": self._format_prompt(statute),
                "output": code.source
            }
            for statute, code in successes
        ])

    def fine_tune(self, base_model: str, dataset: Dataset) -> str:
        # Use Anthropic/OpenAI fine-tuning APIs
        ...
```

**Pros**: Learns patterns in weights, faster inference
**Cons**: Expensive, needs many examples, risk of overfitting

### Mode 4: RL with Code Execution (v4)

Full reinforcement learning with execution reward.

```python
class RLTrainer:
    def __init__(self, policy_model, value_model):
        self.policy = policy_model
        self.value = value_model

    def train_step(self, statute: Statute, test_cases: list[TestCase]):
        # Generate code (action)
        code = self.policy.generate(statute)

        # Execute and score (reward)
        results = self.executor.execute(code, test_cases)
        reward = self.scorer.score(results).accuracy

        # PPO update
        advantage = reward - self.value.predict(statute)
        self.policy.update(statute, code, advantage)
        self.value.update(statute, reward)
```

**Pros**: Optimizes directly for execution accuracy
**Cons**: Complex, needs careful reward shaping, expensive

## v1 Implementation Plan

Start with Mode 1 (Prompt Iteration) on a single provision.

### Step 1: Pick Target Provision

**Candidate: EITC Phase-In Credit (`26 USC § 32(a)(1)`)**

Statutory text:
> "In the case of an eligible individual, there shall be allowed as a credit... an amount equal to the credit percentage of so much of the taxpayer's earned income for the taxable year as does not exceed the earned income amount."

This is:
- Simple formula: `min(earned_income, earned_income_amount) * credit_percentage`
- Well-defined inputs: earned income, filing status, number of children
- Dense oracle coverage: Both PE and TAXSIM implement this
- Clear parameters: credit_percentage and earned_income_amount are in IRS tables

### Step 2: Set Up Oracles

```python
# PolicyEngine oracle
from policyengine_us import Simulation

def pe_eitc_phase_in(earned_income: float, filing_status: str, n_children: int) -> float:
    situation = {
        "people": {"person": {"employment_income": {2024: earned_income}}},
        "tax_units": {"tax_unit": {
            "members": ["person"],
            "filing_status": {2024: filing_status}
        }},
        # ... children if any
    }
    sim = Simulation(situation=situation)
    return float(sim.calculate("eitc", 2024))
```

### Step 3: Generate Test Cases

```python
test_cases = []

# Boundary values
for income in [0, 1000, 5000, 10000, 15000, 20000, 25000]:
    for status in ["SINGLE", "JOINT"]:
        for n_children in [0, 1, 2, 3]:
            expected = pe_eitc_phase_in(income, status, n_children)
            test_cases.append(TestCase(
                inputs={"earned_income": income, "filing_status": status, "n_children": n_children},
                expected={"eitc_phase_in": expected}
            ))
```

### Step 4: Run Training Loop

```python
statute = Statute(
    citation="26 USC § 32(a)(1)",
    text="""In the case of an eligible individual, there shall be allowed
    as a credit against the tax imposed by this subtitle for the taxable
    year an amount equal to the credit percentage of so much of the
    taxpayer's earned income for the taxable year as does not exceed
    the earned income amount.""",
    jurisdiction="us"
)

loop = TrainingLoop(
    generator=CodeGenerator(),
    executor=Executor(),
    oracles=[PolicyEngineOracle()],
    scorer=Scorer(),
    diagnoser=FailureDiagnoser()
)

result = loop.train(statute, test_cases)
print(f"Success: {result.success}, Iterations: {result.iterations}")
print(f"Final code:\n{result.final_code.source}")
```

### Step 5: Evaluate and Iterate

Track metrics across provisions:
- Iterations to convergence
- Final accuracy
- Common failure modes
- Human interventions needed

Use insights to improve prompts, add few-shot examples, expand to more provisions.

## Success Criteria

**v1 Success**: Generate code for EITC phase-in that matches PolicyEngine within $1 on 95% of test cases.

**v2 Success**: Encode full EITC (phase-in, phase-out, eligibility) with <5 human interventions.

**v3 Success**: Encode 10 IRC provisions, with later provisions requiring fewer iterations than earlier ones (demonstrating learning).

## Next Steps

1. Implement `CodeGenerator` with Claude API
2. Implement `PolicyEngineOracle` wrapper
3. Implement `TestCaseGenerator` for EITC
4. Run first training loop
5. Analyze failures, iterate on prompts
6. Document what works for v2 planning
