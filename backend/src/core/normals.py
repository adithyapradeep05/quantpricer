"""
Normal distribution functions for option pricing.
Uses math module only, no SciPy dependency.
"""

from math import exp, sqrt, pi, erf, log
from typing import Union

SQRT2PI = sqrt(2 * pi)
SQRT_2 = sqrt(2.0)

# Constants for numerical stability
MAX_EXP = 700.0  # Maximum exponent to prevent overflow
MIN_EXP = -700.0  # Minimum exponent to prevent underflow


def normal_pdf(x: float) -> float:
    """
    Standard normal probability density function φ(x).
    
    Args:
        x: Input value
        
    Returns:
        φ(x) = exp(-x²/2) / √(2π)
        
    Note:
        φ(-x) = φ(x) due to symmetry
    """
    # Handle extreme values to prevent overflow/underflow
    if abs(x) > 37:  # exp(-37²/2) ≈ 1e-297, which is effectively zero
        return 0.0
    
    exponent = -0.5 * x * x
    if exponent < MIN_EXP:
        return 0.0
    if exponent > MAX_EXP:
        return 0.0
    
    return exp(exponent) / SQRT2PI


def normal_cdf(x: float) -> float:
    """
    Standard normal cumulative distribution function Φ(x).
    
    Args:
        x: Input value
        
    Returns:
        Φ(x) = 0.5 * (1 + erf(x/√2))
        
    Note:
        Φ(-x) = 1 - Φ(x) due to symmetry
    """
    # Handle extreme values for numerical stability
    if x > 8.0:  # Φ(8) ≈ 1 - 1e-15
        return 1.0
    if x < -8.0:  # Φ(-8) ≈ 1e-15
        return 0.0
    
    return 0.5 * (1.0 + erf(x / SQRT_2))


def safe_log(x: float) -> float:
    """
    Safe logarithm function that handles edge cases.
    
    Args:
        x: Input value
        
    Returns:
        log(x) if x > 0, otherwise raises ValueError
    """
    if x <= 0:
        raise ValueError("Cannot take logarithm of non-positive number")
    return log(x)


def safe_sqrt(x: float) -> float:
    """
    Safe square root function that handles edge cases.
    
    Args:
        x: Input value
        
    Returns:
        sqrt(x) if x >= 0, otherwise raises ValueError
    """
    if x < 0:
        raise ValueError("Cannot take square root of negative number")
    return sqrt(x)
