"""
Black-Scholes option pricing formulas.
Uses normals module, no SciPy dependency.
"""

import math
from typing import Literal
from .normals import normal_cdf

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
    
    return (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))


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
    return d1_value - sigma * math.sqrt(T)


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
    
    d1_val = d1(S, K, r, sigma, T)
    d2_val = d2(d1_val, sigma, T)
    
    return S * normal_cdf(d1_val) - K * math.exp(-r * T) * normal_cdf(d2_val)


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
    
    d1_val = d1(S, K, r, sigma, T)
    d2_val = d2(d1_val, sigma, T)
    
    return K * math.exp(-r * T) * normal_cdf(-d2_val) - S * normal_cdf(-d1_val)


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

            