"""
Normal distribution functions for option pricing.
Uses math module only, no SciPy dependency.
"""

from math import exp, sqrt, pi, erf
from typing import Union

SQRT2PI = sqrt(2 * pi)
SQRT_2 = sqrt(2.0)


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
    return exp(-0.5 * x * x) / SQRT2PI


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
    return 0.5 * (1.0 + erf(x / SQRT_2))

