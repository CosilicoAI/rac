"""Oracle implementations for validating generated code."""

from abc import ABC, abstractmethod
from typing import Any, Protocol


class Oracle(Protocol):
    """Protocol for oracle implementations."""

    def evaluate(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Given inputs, return computed values."""
        ...


class PolicyEngineOracle:
    """Oracle using PolicyEngine-US for validation."""

    def __init__(self, year: int = 2024):
        self.year = year
        self._simulation_class = None

    @property
    def Simulation(self):
        """Lazy import of PolicyEngine."""
        if self._simulation_class is None:
            from policyengine_us import Simulation

            self._simulation_class = Simulation
        return self._simulation_class

    def evaluate(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Evaluate inputs using PolicyEngine.

        Args:
            inputs: Dictionary with keys like:
                - earned_income: float
                - filing_status: str ("SINGLE", "JOINT", etc.)
                - n_children: int
                - age: int (optional)

        Returns:
            Dictionary with computed values like:
                - eitc: float
                - eitc_phase_in_rate: float
                - etc.
        """
        situation = self._build_situation(inputs)
        sim = self.Simulation(situation=situation)

        # Calculate relevant variables
        results = {}
        output_vars = ["eitc", "eitc_eligible", "earned_income"]

        for var in output_vars:
            try:
                value = sim.calculate(var, self.year)
                # Convert numpy to Python types
                if hasattr(value, "item"):
                    value = value.item()
                elif hasattr(value, "__iter__") and not isinstance(value, str):
                    value = float(value[0]) if len(value) > 0 else 0.0
                results[var] = value
            except Exception as e:
                results[var] = None
                results[f"{var}_error"] = str(e)

        return results

    def _build_situation(self, inputs: dict[str, Any]) -> dict:
        """Convert simplified inputs to PolicyEngine situation format."""
        earned_income = inputs.get("earned_income", 0)
        filing_status = inputs.get("filing_status", "SINGLE")
        n_children = inputs.get("n_children", 0)
        age = inputs.get("age", 30)

        # Build people
        people = {
            "adult": {
                "age": {self.year: age},
                "employment_income": {self.year: earned_income},
            }
        }

        # Add children
        children_ids = []
        for i in range(n_children):
            child_id = f"child_{i}"
            children_ids.append(child_id)
            people[child_id] = {
                "age": {self.year: 5},  # Young child
                "is_tax_unit_dependent": {self.year: True},
            }

        # Tax unit members
        tax_unit_members = ["adult"] + children_ids

        situation = {
            "people": people,
            "tax_units": {
                "tax_unit": {
                    "members": tax_unit_members,
                    "filing_status": {self.year: filing_status},
                }
            },
            "families": {"family": {"members": tax_unit_members}},
            "spm_units": {"spm_unit": {"members": tax_unit_members}},
            "households": {
                "household": {
                    "members": tax_unit_members,
                    "state_code": {self.year: "CA"},
                }
            },
        }

        return situation


class MockOracle:
    """Mock oracle for testing without PolicyEngine."""

    def __init__(self, responses: dict[str, dict[str, Any]] | None = None):
        self.responses = responses or {}

    def evaluate(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Return mock responses based on inputs."""
        # Create a key from inputs
        key = str(sorted(inputs.items()))
        if key in self.responses:
            return self.responses[key]

        # Simple EITC approximation for testing
        earned_income = inputs.get("earned_income", 0)
        n_children = inputs.get("n_children", 0)

        # Very rough EITC phase-in approximation
        if n_children == 0:
            rate = 0.0765
            max_income = 7840
        elif n_children == 1:
            rate = 0.34
            max_income = 11750
        elif n_children == 2:
            rate = 0.40
            max_income = 16510
        else:
            rate = 0.45
            max_income = 16510

        phase_in = min(earned_income, max_income) * rate

        return {"eitc": phase_in, "eitc_eligible": earned_income > 0, "earned_income": earned_income}
