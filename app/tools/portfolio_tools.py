"""
Portfolio utilities for risk and allocation demos.
"""

from typing import Dict, List
import numpy as np


def compute_portfolio_risk(returns: List[float], weights: List[float]) -> Dict[str, float]:
    """
    Compute naive portfolio metrics:
    - expected_return (weighted average of returns)
    - variance (assuming independent returns for simplicity in demo)
    - volatility (sqrt of variance)

    Args:
        returns (list of float): expected annual returns per asset (e.g., [0.10, 0.06])
        weights (list of float): allocation per asset (e.g., [0.6, 0.4]) should sum to 1

    Returns:
        dict with expected_return, variance, volatility
    """
    if len(returns) != len(weights):
        raise ValueError("returns and weights must have the same length.")
    w = np.array(weights, dtype=float)
    r = np.array(returns, dtype=float)
    if not np.isclose(np.sum(w), 1.0):
        raise ValueError("weights must sum to 1.")
    expected_return = float(np.dot(w, r))
    # Demo variance: sum of w^2 * var_i with var_i ~ (return * 0.5)**2 as a placeholder
    # In real use, you'd pass covariance matrix; this is only illustrative.
    var_i = (r * 0.5) ** 2
    variance = float(np.dot(w**2, var_i))
    volatility = float(np.sqrt(variance))
    return {
        "expected_return": expected_return,
        "variance": variance,
        "volatility": volatility,
    }


def suggest_allocation(risk_tolerance: str, horizon_years: int) -> Dict[str, float]:
    """
    Suggest a simple allocation (%):
    Returns:
        dict: allocation across equities, bonds, cash
    """
    rt = risk_tolerance.lower().strip()
    # very naive demo logic
    if rt in ["low", "conservative"]:
        return {"equities": 0.30, "bonds": 0.50, "cash": 0.20}
    elif rt in ["medium", "moderate"]:
        return {"equities": 0.50, "bonds": 0.35, "cash": 0.15}
    else:  # high or aggressive
        return {"equities": 0.70, "bonds": 0.20, "cash": 0.10}