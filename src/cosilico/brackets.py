"""Bracket calculation functions for tax and benefit computations.

Two core patterns:
- cut: Step function lookup (which bracket -> what value)
- marginal_agg: Marginal rate aggregation (sum of amount * rate per bracket)
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np


def cut(
    amount: Union[float, np.ndarray],
    schedule: Dict[str, Any],
    threshold_by: Optional[Any] = None,
    amount_by: Optional[Any] = None,
) -> Union[float, np.ndarray]:
    """Step function lookup - return value based on which bracket amount falls into.

    Args:
        amount: The value to look up (scalar or array)
        schedule: Dict with 'thresholds' and 'amounts' keys
        threshold_by: Key to index into thresholds (if thresholds vary by category)
        amount_by: Key to index into amounts (if amounts vary by category)

    Returns:
        The value from the bracket the amount falls into

    Example:
        schedule = {
            "thresholds": [10000, 20000],
            "amounts": [100, 50, 0],
        }
        cut(15000, schedule)  # Returns 50

        # With amount_by for household size:
        schedule = {
            "thresholds": [100, 130],
            "amounts": {1: [291, 200, 0], 2: [535, 400, 0]},
        }
        cut(115, schedule, amount_by=2)  # Returns 400
    """
    thresholds = schedule["thresholds"]
    amounts = schedule["amounts"]

    # Handle threshold_by
    if threshold_by is not None:
        if isinstance(threshold_by, np.ndarray):
            # Vectorized case - handle below
            pass
        else:
            thresholds = thresholds[threshold_by]

    # Handle amount_by
    if amount_by is not None:
        if isinstance(amount_by, np.ndarray):
            # Vectorized case - handle below
            pass
        else:
            amounts = amounts[amount_by]

    # Convert to numpy arrays for uniform handling
    amount = np.asarray(amount)
    thresholds = np.asarray(thresholds)
    amounts = np.asarray(amounts)

    # Handle vectorized keys
    if isinstance(threshold_by, np.ndarray) or isinstance(amount_by, np.ndarray):
        return _cut_vectorized_keys(amount, schedule, threshold_by, amount_by)

    # Use searchsorted to find bracket indices
    # searchsorted with side="right" means value AT threshold goes to next bracket
    # This matches typical tax/benefit behavior: income >= threshold puts you in that bracket
    indices = np.searchsorted(thresholds, amount, side="right")

    # Clip to valid range and get amounts
    indices = np.clip(indices, 0, len(amounts) - 1)
    result = amounts[indices]

    # Return scalar if input was scalar
    if result.ndim == 0:
        return float(result)
    return result


def _cut_vectorized_keys(
    amount: np.ndarray,
    schedule: Dict[str, Any],
    threshold_by: Optional[np.ndarray],
    amount_by: Optional[np.ndarray],
) -> np.ndarray:
    """Handle cut with vectorized keys."""
    n = len(amount)
    result = np.zeros(n)

    for i in range(n):
        t_key = threshold_by[i] if threshold_by is not None else None
        a_key = amount_by[i] if amount_by is not None else None

        thresholds = schedule["thresholds"]
        amounts = schedule["amounts"]

        if t_key is not None:
            thresholds = thresholds[t_key]
        if a_key is not None:
            amounts = amounts[a_key]

        thresholds = np.asarray(thresholds)
        amounts = np.asarray(amounts)

        idx = np.searchsorted(thresholds, amount[i], side="right")
        idx = np.clip(idx, 0, len(amounts) - 1)
        result[i] = amounts[idx]

    return result


def marginal_agg(
    amount: Union[float, np.ndarray],
    brackets: Dict[str, Any],
    threshold_by: Optional[Any] = None,
    rate_by: Optional[Any] = None,
) -> Union[float, np.ndarray]:
    """Marginal rate aggregation - sum of (amount in bracket * rate) for each bracket.

    Args:
        amount: The value to apply brackets to (scalar or array)
        brackets: Dict with 'thresholds' and 'rates' keys
        threshold_by: Key to index into thresholds (if thresholds vary by category)
        rate_by: Key to index into rates (if rates vary by category, rare)

    Returns:
        Sum of marginal amounts times rates

    Example:
        brackets = {
            "thresholds": [0, 10000, 40000],
            "rates": [0.10, 0.20, 0.30],
        }
        marginal_agg(15000, brackets)
        # = 10000 * 0.10 + 5000 * 0.20 = 2000

        # With threshold_by for filing status:
        brackets = {
            "thresholds": {"single": [0, 11600], "joint": [0, 23200]},
            "rates": [0.10, 0.12],
        }
        marginal_agg(20000, brackets, threshold_by="single")
    """
    thresholds = brackets["thresholds"]
    rates = brackets["rates"]

    # Handle threshold_by
    if threshold_by is not None:
        if isinstance(threshold_by, np.ndarray):
            return _marginal_agg_vectorized_keys(amount, brackets, threshold_by, rate_by)
        else:
            thresholds = thresholds[threshold_by]

    # Handle rate_by (rare)
    if rate_by is not None:
        if isinstance(rate_by, np.ndarray):
            return _marginal_agg_vectorized_keys(amount, brackets, threshold_by, rate_by)
        else:
            rates = rates[rate_by]

    # Convert to numpy arrays
    amount = np.asarray(amount)
    thresholds = np.asarray(thresholds)
    rates = np.asarray(rates)

    # Calculate marginal amounts and aggregate
    return _marginal_agg_core(amount, thresholds, rates)


def _marginal_agg_core(
    amount: np.ndarray,
    thresholds: np.ndarray,
    rates: np.ndarray,
) -> Union[float, np.ndarray]:
    """Core marginal aggregation calculation."""
    # Handle scalar case
    scalar_input = amount.ndim == 0
    if scalar_input:
        amount = np.atleast_1d(amount)

    n_brackets = len(rates)
    result = np.zeros_like(amount, dtype=float)

    for i in range(n_brackets):
        bracket_start = thresholds[i]
        bracket_end = thresholds[i + 1] if i + 1 < len(thresholds) else np.inf
        rate = rates[i]

        # Amount in this bracket
        amount_in_bracket = np.clip(amount - bracket_start, 0, bracket_end - bracket_start)
        # Only count if we're above the bracket start
        amount_in_bracket = np.where(amount > bracket_start, amount_in_bracket, 0)

        result += amount_in_bracket * rate

    if scalar_input:
        return float(result[0])
    return result


def _marginal_agg_vectorized_keys(
    amount: np.ndarray,
    brackets: Dict[str, Any],
    threshold_by: Optional[np.ndarray],
    rate_by: Optional[np.ndarray],
) -> np.ndarray:
    """Handle marginal_agg with vectorized keys."""
    amount = np.asarray(amount)
    n = len(amount)
    result = np.zeros(n)

    for i in range(n):
        t_key = threshold_by[i] if threshold_by is not None else None
        r_key = rate_by[i] if rate_by is not None else None

        thresholds = brackets["thresholds"]
        rates = brackets["rates"]

        if t_key is not None:
            thresholds = thresholds[t_key]
        if r_key is not None:
            rates = rates[r_key]

        thresholds = np.asarray(thresholds)
        rates = np.asarray(rates)

        val = _marginal_agg_core(np.array([amount[i]]), thresholds, rates)
        result[i] = val[0] if isinstance(val, np.ndarray) else val

    return result
