"""Deterministic fixed-effect heterogeneity calculation, independently checked with Wolfram.

No external service/API calls. Input arrays MUST be effect sizes and standard
errors obtained from authentic comparable studies before scientific use.
A pooled value is descriptive only, not proof of consensus or causal effect.
"""
from math import isfinite, sqrt

def inverse_variance_heterogeneity(effects: list[float], standard_errors: list[float]) -> dict:
    if len(effects) != len(standard_errors) or len(effects) < 2:
        raise ValueError("Need at least two matching effects and standard errors")
    if any(not isfinite(float(v)) for v in effects):
        raise ValueError("Effects must be finite")
    if any(not isfinite(float(se)) or float(se) <= 0 for se in standard_errors):
        raise ValueError("Standard errors must be finite positive numbers")
    weights = [1.0 / (float(se) ** 2) for se in standard_errors]
    pooled = sum(w * v for w, v in zip(weights, effects)) / sum(weights)
    q = sum(w * (float(v) - pooled) ** 2 for w, v in zip(weights, effects))
    dof = len(effects) - 1
    i2 = max(0.0, (q - dof) / q) if q > 0 else 0.0
    stderr = sqrt(1.0 / sum(weights))
    return {
        "pooled_effect": pooled,
        "standard_error": stderr,
        "ci95": [pooled - 1.96 * stderr, pooled + 1.96 * stderr],
        "Q": q,
        "degrees_of_freedom": dof,
        "I2": i2,
        "warning": "Do not pool incomparable outcomes or interpret this result as independent scientific validation.",
    }
