"""Run a policy reform analysis.

Usage:
    python examples/run_reform.py examples/uk_tax_benefit.rac examples/reform.rac
"""

import sys
import time
from datetime import date

import numpy as np

from rac import Model


def load_microdata(n: int = 100_000) -> dict[str, np.ndarray]:
    """Generate synthetic UK population microdata."""
    np.random.seed(42)

    # Income distribution (log-normal, roughly UK-like)
    gross_income = np.random.lognormal(mean=10.3, sigma=0.8, size=n)
    gross_income = np.clip(gross_income, 0, 500_000)

    return {
        "person": np.column_stack([
            gross_income,
            np.full(n, 40.0),  # hours_worked
            np.ones(n),        # is_adult
            np.zeros(n),       # is_child
        ])
    }


def run_analysis(baseline_path: str, reform_path: str):
    """Run baseline vs reform comparison."""
    as_of = date(2024, 6, 1)

    # Load models
    print(f"Loading baseline: {baseline_path}")
    baseline = Model.from_file(baseline_path, as_of=as_of)

    print(f"Loading reform: {reform_path}")
    reform = Model.from_file(baseline_path, reform_path, as_of=as_of)

    # Show what changed
    print("\nScalar changes:")
    baseline_scalars = baseline.scalars
    reform_scalars = reform.scalars
    for k in baseline_scalars:
        if baseline_scalars[k] != reform_scalars.get(k):
            print(f"  {k}: {baseline_scalars[k]} -> {reform_scalars.get(k)}")

    # Load microdata (UK population scale)
    print("\nLoading microdata...")
    data = load_microdata(n=67_000_000)
    income = data["person"][:, 0]

    # Compare
    print("Running comparison...")
    start = time.perf_counter()
    comparison = baseline.compare(reform, data)
    elapsed = time.perf_counter() - start
    print(f"Done in {elapsed:.2f}s")

    # Get summary for net_income
    summary = comparison.summary("person", "person/net_income", income_col=income)

    # Print results
    print(f"\n{'='*60}")
    print("REFORM IMPACT ANALYSIS")
    print(f"{'='*60}")
    print(f"Population: {summary['n']:,}")
    print(f"\nAggregate impact:")
    print(f"  Total cost: £{summary['total_annual']/1e9:.2f}bn/year")
    print(f"  Avg gain:   £{summary['mean_monthly']:.0f}/month")
    print(f"  Winners:    {summary['winners']:,} ({summary['winners_pct']:.1f}%)")
    print(f"  Losers:     {summary['losers']:,} ({summary['losers_pct']:.1f}%)")

    if "by_decile" in summary:
        print(f"\nBy income decile:")
        print(f"{'Decile':>8} {'Avg Income':>12} {'Avg Gain':>10} {'% Winners':>10}")
        print("-" * 44)
        for d in summary["by_decile"]:
            print(f"{d['decile']:>8} £{d['avg_income']:>10,.0f} £{d['avg_gain']:>9,.0f} {d['pct_winners']:>9.0f}%")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python run_reform.py <baseline.rac> <reform.rac>")
        sys.exit(1)

    run_analysis(sys.argv[1], sys.argv[2])
