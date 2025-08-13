"""
Black-Scholes option pricing formulas.
Uses normals module, no SciPy dependency.
"""

import math
from typing import Literal
from .normals import normal_cdf, safe_log, safe_sqrt

OptionType = Literal["call", "put"]


def d1(S: float, K: float, r: float, sigma: float, T: float) -> float:
    """
    Calculate d1 parameter for Black-Scholes formula.
    
    Args:
        S: Current stock price
        K: Strike price
        r: Risk-free rate (annualized)
        sigma: Volatility (annualized)
        T: Time to expiration (years)
        
    Returns:
        d1 = (ln(S/K) + (r + σ²/2)T) / (σ√T)
    """
    if T <= 0:
        return float('inf') if S >= K else float('-inf')
    
    if sigma <= 0:
        raise ValueError("Volatility must be positive for d1 calculation")
    
    try:
        log_term = safe_log(S / K)
        sigma_sqrt_T = sigma * safe_sqrt(T)
        numerator = log_term + (r + 0.5 * sigma * sigma) * T
        return numerator / sigma_sqrt_T
    except (ValueError, ZeroDivisionError) as e:
        raise ValueError(f"Error in d1 calculation: {e}")


def d2(d1_value: float, sigma: float, T: float) -> float:
    """
    Calculate d2 parameter for Black-Scholes formula.
    
    Args:
        d1_value: d1 parameter
        sigma: Volatility (annualized)
        T: Time to expiration (years)
        
    Returns:
        d2 = d1 - σ√T
    """
    if T <= 0:
        return float('inf') if d1_value > 0 else float('-inf')
    
    if sigma <= 0:
        raise ValueError("Volatility must be positive for d2 calculation")
    
    try:
        return d1_value - sigma * safe_sqrt(T)
    except ValueError as e:
        raise ValueError(f"Error in d2 calculation: {e}")


def _validate_inputs(S: float, K: float, r: float, sigma: float, T: float) -> None:
    """Validate input parameters."""
    if S <= 0:
        raise ValueError("Stock price must be positive")
    if K <= 0:
        raise ValueError("Strike price must be positive")
    if sigma < 0:
        raise ValueError("Volatility must be non-negative")
    if T < 0:
        raise ValueError("Time to expiration must be non-negative")
    
    # Additional bounds checking
    if S > 10000:
        raise ValueError("Stock price too high (max: 10,000)")
    if K > 10000:
        raise ValueError("Strike price too high (max: 10,000)")
    if r < -0.5 or r > 2:
        raise ValueError("Risk-free rate out of bounds (-50% to 200%)")
    if T > 50:
        raise ValueError("Time to expiry too long (max: 50 years)")
    if sigma > 5:
        raise ValueError("Volatility too high (max: 500%)")


def price_call(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """
    Price a European call option using Black-Scholes.
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate (annualized)
        sigma: Volatility (annualized)
        
    Returns:
        Call option price
        
    Golden check: S=100, K=100, r=0.05, sigma=0.2, T=1 → ≈10.4506
    """
    _validate_inputs(S, K, r, sigma, T)
    
    if T == 0:
        return max(0, S - K)
    
    if sigma == 0:
        return max(0, S - K * math.exp(-r * T))
    
    try:
        d1_val = d1(S, K, r, sigma, T)
        d2_val = d2(d1_val, sigma, T)
        
        return S * normal_cdf(d1_val) - K * math.exp(-r * T) * normal_cdf(d2_val)
    except (ValueError, OverflowError) as e:
        raise ValueError(f"Error in call price calculation: {e}")


def price_put(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """
    Price a European put option using Black-Scholes.
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate (annualized)
        sigma: Volatility (annualized)
        
    Returns:
        Put option price
        
    Golden check: S=100, K=100, r=0.05, sigma=0.2, T=1 → ≈5.5735
    """
    _validate_inputs(S, K, r, sigma, T)
    
    if T == 0:
        return max(0, K - S)
    
    if sigma == 0:
        return max(0, K * math.exp(-r * T) - S)
    
    try:
        d1_val = d1(S, K, r, sigma, T)
        d2_val = d2(d1_val, sigma, T)
        
        return K * math.exp(-r * T) * normal_cdf(-d2_val) - S * normal_cdf(-d1_val)
    except (ValueError, OverflowError) as e:
        raise ValueError(f"Error in put price calculation: {e}")


def black_scholes_price(S: float, K: float, T: float, r: float, sigma: float, option_type: OptionType) -> float:
    """
    Price a European option using Black-Scholes.
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate (annualized)
        sigma: Volatility (annualized)
        option_type: "call" or "put"
        
    Returns:
        Option price
    """
    if option_type == "call":
        return price_call(S, K, T, r, sigma)
    elif option_type == "put":
        return price_put(S, K, T, r, sigma)
    else:
        raise ValueError("option_type must be 'call' or 'put'")
