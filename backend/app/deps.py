"""
Dependencies for QuantPricer API.
"""

from fastapi import HTTPException
from typing import List
import numpy as np


def validate_option_type(option_type: str) -> str:
    """Validate option type."""
    if option_type not in ["call", "put"]:
        raise HTTPException(status_code=422, detail="option_type must be 'call' or 'put'")
    return option_type


def generate_S_range(K: float, num_points: int = 100) -> List[float]:
    """Generate a range of stock prices around the strike."""
    min_S = K * 0.5
    max_S = K * 1.5
    return list(np.linspace(min_S, max_S, num_points))


def generate_vol_range(num_points: int = 50) -> List[float]:
    """Generate a range of volatility values."""
    return list(np.linspace(0.01, 1.0, num_points))
