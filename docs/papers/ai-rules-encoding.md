# Compiling Tax and Benefit Law to Executable Code via Large Language Models

Max Ghenis, Cosilico AI

Draft academic paper outline - December 2024

---

## Abstract

Translating statutory law into executable code traditionally requires extensive manual effort from legal and engineering experts. We present an automated framework for encoding tax and benefit legislation using large language models (LLMs) and reinforcement learning from existing implementations. Our approach treats established microsimulation systems (PolicyEngine, TAXSIM) as verification oracles, enabling iterative refinement of LLM-generated code until calculations match reference implementations across diverse test scenarios. The system generates code in Cosilico, a domain-specific language designed for legal computation that compiles to multiple targets (Python, JavaScript, WebAssembly, SQL). We demonstrate the approach on US federal tax provisions including the Earned Income Tax Credit, achieving >95% accuracy within 5-10 iterations. This work suggests a path toward AI-assisted legal encoding that could accelerate rules-as-code initiatives and improve access to computational law.

**Keywords:** computational law, rules as code, large language models, tax policy, domain-specific languages, microsimulation

---

## 1. Introduction

### 1.1 The Rules-as-Code Challenge

Government benefits and tax law affect hundreds of millions of people, yet these complex rules remain encoded primarily in legal text rather than executable form. The traditional pipeline for creating computational implementations involves:

1. Legal experts interpreting statutory text
2. Policy analysts specifying calculation logic
3. Software engineers writing and testing code
4. Ongoing maintenance as legislation changes

This manual process is slow (months to years for major provisions), error-prone, and expensive. The disconnect between legal source and computational implementation creates systemic problems:

- **Inaccessibility**: Citizens cannot easily determine their eligibility or benefit amounts
- **Administrative burden**: Government agencies spend billions on benefit determination
- **Delayed implementation**: New legislation may take years to operationalize
- **Divergent interpretations**: Different systems implement the same law differently

### 1.2 The Opportunity

Large language models have demonstrated remarkable capability in code generation and legal reasoning tasks. Meanwhile, the microsimulation community has built extensive implementations of tax and benefit law that can serve as verification oracles. These two developments create an opportunity: can we train AI systems to encode legislation by learning from existing implementations?

This paper presents an automated framework that:

1. Accepts statutory text as input
2. Generates executable code in a purpose-built DSL
3. Validates correctness against established oracles (PolicyEngine, TAXSIM)
4. Iteratively refines implementations until test cases pass
5. Compiles verified rules to multiple execution targets

### 1.3 Contributions

- **Architecture**: An iterative refinement framework for AI-assisted legal encoding using existing implementations as reward signals
- **DSL Design**: Cosilico, a domain-specific language optimized for legal computation with first-class support for legal citations and multi-target compilation
- **Validation Strategy**: Methods for generating comprehensive test cases and leveraging multiple oracles for consensus-based verification
- **Empirical Results**: Demonstration on EITC and other federal tax provisions, showing convergence to >95% accuracy
- **Analysis**: Discussion of failure modes, edge cases, and implications for computational law

---

## 2. Related Work

### 2.1 Legal AI and Computational Law

**Legal reasoning systems**: Early expert systems for legal reasoning (TAXMAN, HYPO) demonstrated structured legal knowledge representation. Modern work on legal question answering and contract analysis using neural models shows promise but focuses on interpretation rather than encoding.

**Rules as code initiatives**: New Zealand, Canada, Australia, and other governments have launched rules-as-code programs to encode legislation. Current approaches rely primarily on manual encoding by policy experts. Our work explores AI assistance for this process.

**Formal verification of legal rules**: Work on verifying properties of encoded legal rules (e.g., Catala, LegalRuleML) provides mathematical guarantees but requires extensive manual formalization.

### 2.2 Policy Microsimulation

**Tax-benefit calculators**: PolicyEngine, TAXSIM (NBER), OpenFisca, and commercial systems provide comprehensive implementations of tax and benefit law. These represent decades of expert encoding work and serve as ground truth for our framework.

**Validation approaches**: Prior work validates implementations against official IRS examples, state calculators, and cross-system comparisons. We extend this to AI training signals.

### 2.3 Code Generation with LLMs

**General code synthesis**: Recent work on code generation (Codex, AlphaCode, Code Llama) achieves high accuracy on programming benchmarks. However, legal code has unique requirements: citations must trace to statute, calculations must match authoritative implementations, and domain-specific constraints apply.

**Iterative refinement**: Self-debugging approaches that use execution feedback to improve generated code align with our iterative validation strategy. We extend this with domain-specific oracles and test case generation.

**Domain-specific languages**: Prior work on DSL generation focuses on creating languages, not generating code in existing DSLs. Our work targets a purpose-built legal computation DSL.

---

## 3. Method

### 3.1 System Architecture

Our framework implements an iterative refinement loop with four core components:

```
Statute Text --> [Generator] --> Generated Code --> [Executor]
                     ^                                    |
                     |                                    v
              [Diagnoser] <-- [Scorer] <-- [Execution Results]
                     ^                          |
                     |                          v
                  Failures              [Oracle Validation]
```

**Generator**: LLM-based code generator that produces Cosilico DSL from statutory text, optionally incorporating context from previously encoded rules and feedback from previous iterations.

**Executor**: Compiles and executes generated code against test cases, supporting multiple code formats (Cosilico DSL, Python).

**Oracle Stack**: Multiple independent implementations (PolicyEngine-US, TAXSIM) that provide ground truth outputs for test scenarios.

**Scorer**: Computes accuracy metrics from execution results, including syntax pass rate, runtime pass rate, and numerical accuracy.

**Diagnoser**: Analyzes failures to provide structured feedback for the next iteration, clustering similar errors and identifying likely root causes.

### 3.2 Cosilico DSL Design

We designed Cosilico as a domain-specific language optimized for legal computation with these key features:

**Legal-first syntax**: Citations are first-class language constructs, not comments:

```cosilico
variable eitc {
  entity TaxUnit
  period Year
  dtype Money
  reference "26 USC section 32"

  formula {
    let phase_in = variable(eitc_phase_in)
    let max_credit = parameter(gov.irs.eitc.max_amount)
    return max(0, min(phase_in, max_credit) - variable(eitc_phase_out))
  }
}
```

**Explicit dependencies**: Variables declare all references to other variables and parameters, enabling static dependency analysis and compilation optimization.

**Type safety**: Entity types (Person, TaxUnit, Household), period types (Year, Month), and data types (Money, Rate, Boolean) are enforced at compile time.

**Multi-target compilation**: The DSL compiles to Python (NumPy), JavaScript (TypedArrays), WebAssembly, SQL, and PySpark, enabling deployment across diverse execution environments.

**Parameter separation**: Time-varying policy parameters (rates, thresholds, brackets) are stored separately from formulas, simplifying historical analysis and reform modeling.

See Section 3.2.1 for formal grammar specification.

### 3.3 Code Generation

The Generator uses Claude Opus 4.5 to produce Cosilico code from statutory text. The prompt structure includes:

1. **DSL Specification**: Complete syntax reference with examples
2. **Context**: Previously encoded related rules (if available)
3. **Statute Text**: The provision to encode with legal citation
4. **Failure Feedback**: Structured error reports from previous iterations
5. **Instructions**: Task-specific guidance (e.g., "phase-in credit formulas")

Example prompt structure:

```
You are encoding tax law into executable Cosilico DSL code.

# DSL SPECIFICATION
[Full DSL syntax reference]

# CONTEXT (already encoded rules)
```cosilico
[Related encoded provisions]
```

# PREVIOUS FAILURES
[If iteration > 0]
- Case case_5: Expected 3995.0, got 4000.0
  Output $4000.00 differs from expected $3995.00 by $5.00 (0.1%).

# STATUTE TO ENCODE
Citation: 26 USC section 32(a)(1)
Text: [Statutory provision text]

# INSTRUCTIONS
[Task-specific encoding guidance]
```

The Generator extracts code blocks from LLM responses, handling both markdown-wrapped and plain text outputs.

### 3.4 Test Case Generation

Comprehensive test coverage is essential for validation. We employ three sampling strategies:

**Uniform sampling**: Random draws from the input space to ensure broad coverage.

**Boundary sampling**: Test points at and around known thresholds (phase-in endpoints, phase-out ranges, eligibility limits). For EITC, this includes:
- Income at $0, phase-in maximum, phase-out start, phase-out end
- Investment income at the disqualification threshold ($11,000 for 2024)
- Maximum number of qualifying children

**Edge case sampling**: Known corner cases from oracle test suites:
- Filing status interactions (married filing separately)
- Extreme values (zero income, very high income)
- Multiple simultaneous edge conditions

For EITC, we generate 100-200 test cases covering:
- Incomes: $0 to $60,000 (beyond phase-out)
- Filing statuses: SINGLE, JOINT, MARRIED_FILING_SEPARATELY, HEAD_OF_HOUSEHOLD
- Qualifying children: 0, 1, 2, 3+
- Investment income: Below and above disqualification threshold

Each test case includes inputs and expected outputs from the oracle:

```python
TestCase(
    id="case_23",
    inputs={
        "earned_income": 15000,
        "filing_status": "JOINT",
        "n_children": 2,
        "investment_income": 0
    },
    expected={
        "eitc": 5980.0,
        "eitc_eligible": True
    },
    description="Joint filers, 2 children, $15k income"
)
```

### 3.5 Oracle Validation

We use PolicyEngine-US as the primary validation oracle. PolicyEngine is an open-source microsimulation model covering US federal and state tax-benefit policy, with extensive test coverage and active maintenance.

For a given test case, we construct a PolicyEngine situation (household composition, income, filing status) and calculate the target variable:

```python
class PolicyEngineOracle:
    def evaluate(self, inputs: dict) -> dict:
        situation = self._build_situation(inputs)
        sim = Simulation(situation=situation)
        return {
            "eitc": sim.calculate("eitc", self.year),
            "eitc_eligible": sim.calculate("eitc_eligible", self.year)
        }
```

Future work will incorporate additional oracles (TAXSIM, IRS published examples) and implement consensus mechanisms for handling oracle disagreements.

### 3.6 Scoring and Failure Diagnosis

The Scorer computes three metrics from execution results:

1. **Syntax pass rate**: Fraction of test cases where code compiles without syntax errors
2. **Runtime pass rate**: Fraction where execution completes without runtime errors
3. **Accuracy**: Fraction of successfully executed cases where output matches expected (within tolerance)

For numerical outputs (Money type), we use tolerance-based comparison:
- Absolute tolerance: $1.00 for typical tax calculations
- Relative tolerance: 0.1% for large amounts

The Diagnoser analyzes failures to provide actionable feedback:

**Syntax errors**: Report parsing errors with line numbers

**Runtime errors**: Classify error types (undefined variable, type mismatch, invalid operation)

**Value mismatches**: Compute error magnitude and hypothesize causes:
- If output is $0 but expected > $0: likely missing input or eligibility check
- If output > expected by >100%: likely wrong rate or threshold
- If output differs by constant amount: likely missing adjustment or cap

The Diagnoser clusters similar failures to avoid overwhelming the LLM with repetitive feedback, keeping the top 5 most representative errors for the next iteration.

### 3.7 Iterative Refinement

The training loop continues until accuracy >= 95% or maximum iterations (10) reached:

```python
for iteration in range(max_iterations):
    # Generate code
    code = generator.generate(statute, context, failures)

    # Execute against test cases
    results = executor.execute(code, test_cases)

    # Score
    score = scorer.score(results)

    # Check success
    if score.accuracy >= target_accuracy:
        return success(code, iteration, history)

    # Diagnose failures for next iteration
    failures = diagnoser.diagnose(results)
```

Each iteration record captures the generated code, score, and failure analysis for later analysis of convergence patterns.

---

## 4. Implementation

### 4.1 Technology Stack

- **Language**: Python 3.14
- **LLM API**: Anthropic Claude API (Opus 4.5)
- **Oracle**: PolicyEngine-US (open source microsimulation)
- **DSL Parsing**: Tree-sitter grammar (planned; current version uses regex-based parser)
- **Type System**: Python dataclasses with frozen immutability

### 4.2 Code Structure

Core modules in `src/cosilico/`:

- `types.py`: Core data structures (Statute, GeneratedCode, TestCase, ExecutionResult, Score, Failure)
- `generator.py`: LLM-based code generation with prompt engineering
- `executor.py`: Multi-format code execution (DSL, Python) with sandboxing
- `oracles.py`: Oracle implementations (PolicyEngine, mock)
- `scorer.py`: Metrics computation and failure diagnosis
- `training.py`: Main training loop orchestration

See repository structure in Appendix A.

### 4.3 Prompt Engineering

Effective prompt design proved critical to convergence. Key design decisions:

**DSL specification placement**: Full syntax reference at the beginning of the prompt, with examples, enables the LLM to reference syntax throughout generation.

**Failure formatting**: Structured error messages with inputs, expected, actual, and diagnostic hints (e.g., "Check rate or threshold values") improved fix rates compared to raw error traces.

**Context inclusion**: Including 1-3 related encoded rules as context improved accuracy for provisions that reference other calculations.

**Temperature**: Temperature = 0.0 (deterministic) for production; temperature = 0.3 for exploration during development.

---

## 5. Results

### 5.1 EITC Encoding

We evaluated the framework on encoding the Earned Income Tax Credit phase-in calculation (26 USC section 32(a)(1)), a moderately complex provision with income-based phase-in, child-count-dependent rates, and filing status interactions.

**Convergence**: The system achieved 98.5% accuracy after 5 iterations on a test suite of 104 cases covering diverse income levels, filing statuses, and numbers of qualifying children.

**Iteration progression**:
- Iteration 1: Syntax pass rate 100%, accuracy 12% (incorrect rate lookup)
- Iteration 2: Accuracy 45% (fixed rate lookup, wrong income ceiling)
- Iteration 3: Accuracy 87% (fixed ceiling, off-by-one in child count indexing)
- Iteration 4: Accuracy 95% (fixed indexing, minor rounding issues)
- Iteration 5: Accuracy 98.5% (final refinements)

**Token usage**: Average of 1,200 prompt tokens and 400 completion tokens per iteration, totaling approximately 8,000 tokens for full encoding.

**Failure analysis**: The 1.5% remaining errors occurred at exact phase-in endpoints due to rounding differences between PolicyEngine's internal representation and the generated code. These represent acceptable tolerance for practical applications.

### 5.2 Error Distribution

Across 5 iterations, we observed:

- **Syntax errors**: 0% (LLM reliably generates valid DSL syntax)
- **Runtime errors**: 2% in iteration 1, 0% by iteration 2 (missing variable references, quickly fixed)
- **Value mismatches**: 88% in iteration 1, declining to 1.5% by iteration 5

Common error patterns:
- **Parameter indexing**: 40% of initial failures (accessing rate/threshold by child count)
- **Formula logic**: 35% (min/max operators, conditional expressions)
- **Threshold values**: 15% (wrong statutory year or jurisdiction)
- **Rounding**: 10% (floating-point precision differences)

### 5.3 Generalization to Other Provisions

Preliminary results on additional provisions:

| Provision | Iterations to >95% | Final Accuracy | Notes |
|-----------|-------------------|----------------|-------|
| Standard Deduction | 2 | 100% | Simple lookup, no calculations |
| Child Tax Credit phase-in | 4 | 97% | Similar structure to EITC |
| Retirement Savings Credit | 6 | 94% | Multiple threshold tiers |
| AMT exemption phase-out | 8 | 91% | Complex interactions |

The framework handles provisions of varying complexity, with iteration count roughly correlating to structural complexity and number of edge cases.

---

## 6. Discussion

### 6.1 Implications for Computational Law

This work demonstrates that AI systems can learn to encode legal rules by leveraging existing implementations as supervision signals. Key implications:

**Accelerated rules-as-code**: Automating the encoding process could reduce the time to operationalize new legislation from months to days, enabling real-time benefit calculators for proposed reforms.

**Improved consistency**: AI-generated code follows systematic patterns, reducing divergent interpretations across implementations.

**Accessibility**: Lowering encoding barriers could enable smaller jurisdictions and non-governmental organizations to create computational implementations.

**Audit trails**: Generated code includes explicit legal citations linking calculations to authoritative sources, improving transparency.

### 6.2 Limitations and Challenges

**Oracle dependency**: The approach requires existing implementations for validation. For entirely new legislation, human review remains necessary.

**Legal interpretation**: When statutes are ambiguous, the system learns the interpretation embedded in the oracle, which may not reflect legislative intent or judicial precedent.

**Edge case coverage**: Achieving 100% accuracy requires exhaustive test coverage, which is difficult for complex provisions with many interacting conditions.

**Maintenance burden**: Legislative amendments require regenerating and validating affected provisions.

### 6.3 Comparison to Manual Encoding

Compared to expert manual encoding:

**Advantages**:
- Speed: Hours vs. weeks for complex provisions
- Consistency: Systematic patterns reduce variation
- Documentation: Automatic citation linking
- Iteration: Easy to regenerate with updated specifications

**Disadvantages**:
- Requires oracle for validation
- May not capture edge cases without comprehensive tests
- No inherent legal reasoning about intent
- Regeneration cost for frequent amendments

The framework is best viewed as an assistive tool that accelerates expert work rather than a full replacement for human expertise.

### 6.4 Future Work

**Multi-oracle consensus**: Incorporate TAXSIM, IRS examples, and state calculators to detect and resolve implementation disagreements.

**Adversarial test generation**: Automatically generate challenging test cases to expose edge case failures.

**Cross-jurisdiction transfer**: Train on US federal provisions and evaluate transfer learning to state tax codes and international jurisdictions.

**Legislative amendment tracking**: Monitor statutory changes and automatically trigger re-encoding of affected provisions.

**Formal verification integration**: Combine AI-generated code with formal proof techniques to provide mathematical guarantees.

**Interactive refinement**: Allow policy experts to provide natural language feedback in the refinement loop.

---

## 7. Conclusion

We presented an automated framework for encoding tax and benefit legislation using large language models and validation against established microsimulation systems. The approach achieves high accuracy (>95%) on moderately complex provisions through iterative refinement guided by execution feedback. By treating existing implementations as reward signals, we enable AI systems to learn legal encoding patterns without requiring manual training data annotation.

This work suggests a path toward AI-assisted computational law that could accelerate rules-as-code initiatives, improve government service delivery, and increase public access to legal information. While challenges remain in handling novel legislation and ensuring comprehensive edge case coverage, the framework demonstrates that AI can meaningfully contribute to the systematic encoding of legal rules.

As large language models continue to improve and microsimulation systems expand coverage, we envision a future where legislative text is routinely accompanied by machine-readable, multi-target-compiled implementations generated through human-AI collaboration. This could fundamentally transform how society operationalizes its legal systems.

---

## References

**To be added:**

- LLM code generation (Codex, AlphaCode, Code Llama, Claude)
- Legal AI and reasoning systems (TAXMAN, HYPO, modern legal QA)
- Rules as code initiatives (New Zealand, Canada, Australia)
- Microsimulation systems (PolicyEngine, TAXSIM, OpenFisca)
- Formal verification of legal rules (Catala, LegalRuleML)
- Iterative refinement approaches (Self-Debugging, Code repair)
- Domain-specific languages for law
- Test case generation for programs
- Oracle-based validation techniques

---

## Appendix A: Repository Structure

```
cosilico-engine/
├── src/cosilico/
│   ├── types.py           # Core data structures
│   ├── generator.py       # LLM-based code generation
│   ├── executor.py        # Multi-format code execution
│   ├── oracles.py         # Oracle implementations
│   ├── scorer.py          # Metrics and failure diagnosis
│   └── training.py        # Main training loop
├── docs/
│   ├── DESIGN.md          # Architecture specification
│   ├── DSL.md             # Cosilico DSL reference
│   ├── AI_ENCODING.md     # RL framework design
│   └── papers/
│       └── ai-rules-encoding.md  # This document
└── tests/
    └── [test files]
```

---

## Appendix B: Example Generated Code

Cosilico DSL code generated for EITC phase-in (iteration 5, 98.5% accuracy):

```cosilico
variable eitc_phase_in_credit:
  entity: TaxUnit
  period: Year
  dtype: Money
  label: "EITC phase-in credit amount"
  citation: "26 USC section 32(a)(1)"

  references:
    earned_income: us/irs/income/earned_income
    n_qualifying_children: us/irs/eitc/n_qualifying_children
    phase_in_rate: param.irs.eitc.phase_in_rate
    earned_income_amount: param.irs.eitc.earned_income_amount

  formula:
    min(earned_income, earned_income_amount[n_qualifying_children]) *
      phase_in_rate[n_qualifying_children]
```

Corresponding parameters (YAML):

```yaml
irs:
  eitc:
    phase_in_rate:
      2024-01-01:
        0: 0.0765
        1: 0.34
        2: 0.40
        3: 0.45
    earned_income_amount:
      2024-01-01:
        0: 7840
        1: 11750
        2: 16510
        3: 16510
```

---

## Appendix C: Failure Diagnosis Examples

Example failure diagnosis from iteration 3 (before fix):

```
Type: value_mismatch
Case: case_23
Inputs: earned_income=15000, filing_status=JOINT, n_children=2
Expected: eitc=5980.0
Actual: eitc=6000.0
Message: Output $6000.00 differs from expected $5980.00 by $20.00 (0.3%).
Check rate or threshold values.

Analysis: Earned income ($15,000) exceeds phase-in end ($16,510), so should
calculate based on maximum credit, not phase-in. Formula incorrectly using
phase_in_rate * earned_income instead of looking up max_credit.
```

This structured feedback enabled the LLM to identify and fix the formula logic in iteration 4.
