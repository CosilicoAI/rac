# Oracle Stack

The oracle stack provides ground truth for AI-assisted encoding. Multiple independent implementations create robust verification through consensus.

## Available Oracles

| Oracle | Coverage | Role |
|--------|----------|------|
| **PolicyEngine-US** | Federal + 50 states, benefits | Primary oracle, comprehensive |
| **PolicyEngine-UK** | UK taxes + benefits | Cross-jurisdiction validation |
| **TAXSIM (NBER)** | Federal + state income tax | Academic gold standard |
| **IRS Published Examples** | Official scenarios | Authoritative edge cases |
| **State DOR Calculators** | State-specific | State-level validation |

## Oracle Interface

Each oracle implements a common interface:

```python
class Oracle(Protocol):
    """Interface for verification oracles."""

    @property
    def name(self) -> str:
        """Oracle identifier."""
        ...

    @property
    def coverage(self) -> list[str]:
        """Which variables this oracle can calculate."""
        ...

    def calculate(
        self,
        inputs: dict,
        variable: str,
        year: int
    ) -> OracleResult:
        """
        Calculate a variable for given inputs.

        Returns OracleResult with value and confidence.
        """
        ...
```

**Oracle Result:**

```python
@dataclass
class OracleResult:
    value: float | bool | str
    confidence: float  # 0.0 to 1.0
    source: str  # Oracle name
    metadata: dict  # Oracle-specific info
```

## PolicyEngine Integration

PolicyEngine is the primary oracle:

```python
class PolicyEngineOracle(Oracle):
    def __init__(self, country: str = "us"):
        self.country = country
        if country == "us":
            from policyengine_us import Simulation
        elif country == "uk":
            from policyengine_uk import Simulation
        self.Simulation = Simulation

    def calculate(
        self,
        inputs: dict,
        variable: str,
        year: int
    ) -> OracleResult:
        # Build situation from inputs
        situation = self._build_situation(inputs, year)

        # Run simulation
        sim = self.Simulation(situation=situation)
        value = sim.calculate(variable, year)

        return OracleResult(
            value=float(value),
            confidence=1.0,  # PE is authoritative
            source="policyengine_us",
            metadata={"simulation_id": sim.id}
        )
```

## TAXSIM Integration

NBER's TAXSIM provides academic validation:

```python
class TAXSIMOracle(Oracle):
    """
    NBER TAXSIM - academic gold standard for income tax.
    http://taxsim.nber.org/
    """

    def calculate(
        self,
        inputs: dict,
        variable: str,
        year: int
    ) -> OracleResult:
        # Convert to TAXSIM format
        taxsim_input = self._to_taxsim_format(inputs, year)

        # Call TAXSIM API
        response = taxsim_api.calculate(taxsim_input)

        # Map TAXSIM output variable to requested variable
        value = self._map_variable(response, variable)

        return OracleResult(
            value=value,
            confidence=0.95,  # High but not authoritative
            source="taxsim",
            metadata={"taxsim_id": response.id}
        )
```

## Consensus Mechanism

When multiple oracles are available, we compute consensus:

```python
def consensus_oracle_output(
    inputs: dict,
    oracles: list[Oracle],
    variable: str,
    year: int,
    tolerance: float = 0.01
) -> tuple[float, float]:
    """
    Returns (consensus_value, confidence).

    High confidence: all oracles agree within tolerance
    Medium confidence: majority agree
    Low confidence: significant disagreement (flag for human review)
    """
    results = []
    for oracle in oracles:
        if variable in oracle.coverage:
            result = oracle.calculate(inputs, variable, year)
            results.append(result)

    if not results:
        raise NoOracleAvailable(f"No oracle covers {variable}")

    values = [r.value for r in results]

    # Check for consensus
    clusters = cluster_by_tolerance(values, tolerance)

    if len(clusters) == 1:
        # Full consensus
        return (mean(values), 1.0)

    largest_cluster = max(clusters, key=len)
    if len(largest_cluster) > len(values) / 2:
        # Majority consensus
        return (mean(largest_cluster), 0.7)

    # No consensus - flag for review
    log_disagreement(inputs, results, variable)
    return (median(values), 0.3)
```

**Consensus Levels:**

| Level | Condition | Confidence | Action |
|-------|-----------|------------|--------|
| Full | All oracles within tolerance | 1.0 | Use mean |
| Majority | >50% within tolerance | 0.7 | Use cluster mean |
| No consensus | Significant disagreement | 0.3 | Flag for review |

## Handling Disagreements

Oracle disagreements are valuable signal:

```python
def log_disagreement(
    inputs: dict,
    results: list[OracleResult],
    variable: str
):
    """
    Log oracle disagreements for analysis.

    Disagreements surface:
    - Edge cases in statute interpretation
    - Bugs in existing implementations
    - Ambiguities requiring legal judgment
    """
    disagreement = OracleDisagreement(
        variable=variable,
        inputs=inputs,
        results=[
            {"oracle": r.source, "value": r.value}
            for r in results
        ],
        timestamp=datetime.now(),
        status="pending_review"
    )

    # Store for human review
    disagreement_store.add(disagreement)

    # Alert if high-priority variable
    if variable in HIGH_PRIORITY_VARIABLES:
        alert_team(disagreement)
```

**Disagreement Analysis:**

| Cause | Detection | Resolution |
|-------|-----------|------------|
| Bug in oracle | One oracle consistently wrong | Report upstream, use other oracles |
| Rounding difference | Values within $1 | Increase tolerance |
| Year/version mismatch | Systematic offset | Align oracle versions |
| Genuine ambiguity | Persistent disagreement | Legal review needed |

## IRS Examples as Oracles

Published IRS examples are authoritative:

```python
class IRSExampleOracle(Oracle):
    """
    IRS-published examples from publications and worksheets.
    These are THE authoritative source.
    """

    def __init__(self):
        # Load curated IRS examples
        self.examples = load_irs_examples()

    @property
    def coverage(self) -> list[str]:
        return list(self.examples.keys())

    def calculate(
        self,
        inputs: dict,
        variable: str,
        year: int
    ) -> OracleResult | None:
        # Find matching example
        example = self._find_matching_example(inputs, variable, year)

        if example is None:
            return None  # No matching IRS example

        return OracleResult(
            value=example.expected_value,
            confidence=1.0,  # Authoritative
            source="irs_example",
            metadata={
                "publication": example.publication,
                "page": example.page,
                "example_name": example.name
            }
        )
```

IRS examples override other oracles:

```python
def oracle_priority(
    results: list[OracleResult]
) -> OracleResult:
    """
    When we have an IRS example that matches, use it.
    """
    for result in results:
        if result.source == "irs_example":
            return result

    # Otherwise use consensus
    return consensus(results)
```

## Oracle Coverage Matrix

Track which oracles cover which variables:

```python
ORACLE_COVERAGE = {
    # Federal income tax
    "income_tax": ["policyengine_us", "taxsim", "irs_examples"],
    "agi": ["policyengine_us", "taxsim", "irs_examples"],
    "taxable_income": ["policyengine_us", "taxsim", "irs_examples"],

    # Credits
    "eitc": ["policyengine_us", "taxsim", "irs_examples"],
    "ctc": ["policyengine_us", "taxsim", "irs_examples"],

    # Benefits (PE only)
    "snap": ["policyengine_us"],
    "medicaid": ["policyengine_us"],
    "tanf": ["policyengine_us"],

    # State taxes
    "ca_income_tax": ["policyengine_us", "taxsim"],
    "ny_income_tax": ["policyengine_us", "taxsim"],

    # UK
    "income_tax_uk": ["policyengine_uk"],
    "universal_credit": ["policyengine_uk"],
}
```

## Adding New Oracles

To add a new oracle:

1. Implement the `Oracle` protocol
2. Register coverage
3. Calibrate confidence levels
4. Add to consensus mechanism

```python
class NewOracle(Oracle):
    @property
    def name(self) -> str:
        return "new_oracle"

    @property
    def coverage(self) -> list[str]:
        return ["variable_a", "variable_b"]

    def calculate(self, inputs, variable, year) -> OracleResult:
        # Implementation
        ...

# Register
oracle_registry.register(NewOracle())
```

## Metrics

Track oracle performance:

```python
@dataclass
class OracleMetrics:
    oracle_name: str

    # Coverage
    variables_covered: int
    test_cases_answered: int

    # Agreement
    full_consensus_rate: float  # How often in full agreement
    majority_rate: float  # How often in majority
    disagreement_rate: float  # How often outlier

    # Performance
    mean_response_time: float
    error_rate: float

    # Quality
    confirmed_bugs_found: int  # Bugs in THIS oracle found via disagreement
    confirmed_bugs_reported: int  # Bugs in OTHER oracles we helped find
```
