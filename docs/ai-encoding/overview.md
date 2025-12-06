# AI-Assisted Rules Encoding

Traditional rules-as-code requires manual translation: lawyers and engineers read statutes, write code. This doesn't scale.

We flip the paradigm: **use existing implementations as verification oracles to train AI agents that learn to encode rules directly from legislation.**

## The Core Insight

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

This is **TDD at scale**:
1. Generate test cases from existing implementations (oracles)
2. AI agent generates code to pass those tests
3. Iterate until passing
4. The training data factory becomes the moat

## Why This Works

### Existing Implementations as Ground Truth

PolicyEngine, TAXSIM, and other tax calculators have already encoded tax law. They may have different architectures, but they agree on outputs for most inputs.

Instead of manually translating their code to Cosilico DSL, we use them as **verification oracles**:
- Generate thousands of test scenarios
- Run through oracles to get expected outputs
- Train agents to produce code that matches

### Not One-Shot Generation

This is NOT asking an LLM to generate code in one pass. The agent iterates:

1. Generate initial code
2. Run tests against oracles
3. Diagnose failures
4. Revise code
5. Repeat until passing

The reward signal guides improvement.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         ENCODER SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │   Statute   │  │  Test Case   │  │      Agent Loop       │  │
│  │   Parser    │  │  Generator   │  │                       │  │
│  │             │  │              │  │  ┌─────────────────┐  │  │
│  │  - Extract  │  │  - Boundary  │  │  │  LLM (Claude/   │  │  │
│  │    clauses  │  │  - Edge      │  │  │  GPT/Gemini)    │  │  │
│  │  - Build    │  │  - Uniform   │  │  └────────┬────────┘  │  │
│  │    context  │  │  - Random    │  │           │           │  │
│  │             │  │              │  │           ▼           │  │
│  └──────┬──────┘  └──────┬───────┘  │  ┌─────────────────┐  │  │
│         │                │          │  │  Code Generator │  │  │
│         │                │          │  └────────┬────────┘  │  │
│         ▼                ▼          │           │           │  │
│  ┌──────────────────────────────┐  │           ▼           │  │
│  │       Context Builder        │  │  ┌─────────────────┐  │  │
│  │                              │──┼─▶│  DSL Compiler   │  │  │
│  │  - Statute text              │  │  └────────┬────────┘  │  │
│  │  - Similar encoded rules     │  │           │           │  │
│  │  - Parameter schemas         │  │           ▼           │  │
│  │  - Failure diagnoses         │  │  ┌─────────────────┐  │  │
│  └──────────────────────────────┘  │  │  Test Runner    │  │  │
│                                    │  └────────┬────────┘  │  │
│                                    │           │           │  │
│                                    └───────────┼───────────┘  │
│                                                │              │
├────────────────────────────────────────────────┼──────────────┤
│                     ORACLE STACK               │              │
│  ┌──────────────────────────────────────────┐  │              │
│  │                                          │  │              │
│  │  ┌────────────┐  ┌────────────┐         │  │              │
│  │  │PolicyEngine│  │  TAXSIM    │         │◀─┘              │
│  │  │    -US     │  │  (NBER)    │   ...   │                 │
│  │  └────────────┘  └────────────┘         │                 │
│  │                                          │                 │
│  │            ┌─────────────────┐           │                 │
│  │            │    Consensus    │           │                 │
│  │            │    Mechanism    │           │                 │
│  │            └────────┬────────┘           │                 │
│  │                     │                    │                 │
│  └─────────────────────┼────────────────────┘                 │
│                        │                                      │
│                        ▼                                      │
│                ┌───────────────┐                              │
│                │ Reward Signal │──────────────────────────────┤
│                │  (0.0 - 1.0)  │                              │
│                └───────────────┘                              │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Key Components

### Oracle Stack

Multiple independent implementations provide robust ground truth:

| Oracle | Coverage | Role |
|--------|----------|------|
| **PolicyEngine-US** | Federal + 50 states, benefits | Primary oracle, comprehensive |
| **PolicyEngine-UK** | UK taxes + benefits | Cross-jurisdiction validation |
| **TAXSIM (NBER)** | Federal + state income tax | Academic gold standard |
| **IRS Published Examples** | Official scenarios | Authoritative edge cases |
| **State DOR Calculators** | State-specific | State-level validation |

When oracles disagree, the consensus mechanism flags for human review. Disagreements surface bugs in existing implementations or ambiguities in statute.

### Test Case Generator

Generates diverse scenarios to exercise the code:

- **Boundary** - Values at thresholds and phase-outs
- **Edge** - Zero income, maximum values, unusual filing statuses
- **Uniform** - Random samples across input space
- **Adversarial** - Designed to break common mistakes

### Reward Function

Two-level reward:

1. **Structural (0-1)** - Does code follow DSL grammar? Use correct primitives? Have citations?
2. **Semantic (0-1)** - Do calculations match oracles across test cases?

Combined reward shapes learning from syntax compliance to calculation correctness.

### Agent Loop

The iterative refinement process:

```python
for iteration in range(max_iterations):
    # Evaluate current code
    reward = evaluate(generated_code, test_cases, oracles)

    if reward >= 0.99:
        return success

    # Diagnose failures
    failures = diagnose(generated_code, test_cases)

    # Generate revision
    generated_code = llm.revise(
        current_code=generated_code,
        failures=failures,
        statute_text=statute
    )
```

## What We Optimize

We optimize the agent **workflow**, not model weights:

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

Once trained on US federal, transfer learning accelerates state encoding:
- Many state rules reference federal calculations
- State agent starts from federal patterns
- Curriculum: simple coupling states → complex states

### New Legislation (No Oracle)

For brand-new laws with no existing implementation:
1. Find similar encoded rules as templates
2. Extract examples from bill text
3. Generate with lower confidence threshold
4. Flag for human review

## Learn More

- {doc}`reward-functions` - Two-level reward system design
- {doc}`oracle-stack` - Oracle consensus and disagreement handling
- {doc}`curriculum` - Progressive complexity training
