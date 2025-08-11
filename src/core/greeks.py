"""
Option Greeks calculations using Black-Scholes formulas.
Uses core modules, no SciPy dependency.
"""

import math
from typing import Literal, Dict, Any
from .normals import normal_pdf, normal_cdf
from .bs import d1, d2

OptionType = Literal["call", "put"]


def delta(S: float, K: float, T: float, r: float, sigma: float, option_type: OptionType) -> float:
    """
    Calculate option delta.
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate (annualized)
        sigma: Volatility (annualized)
        option_type: "call" or "put"
        
    Returns:
        Delta (rate of change of option price with respect to stock price)
        
    Golden check (call): S=100, K=100, r=0.05, sigma=0.2, T=1 → ≈0.63683
    Golden check (put):  S=100, K=100, r=0.05, sigma=0.2, T=1 → ≈-0.36317
    """
    if T <= 0:
        if option_type == "call":
            return 1.0 if S > K else (0.5 if S == K else 0.0)
        else:
            return -1.0 if S < K else (-0.5 if S == K else 0.0)
    
    if sigma <= 0:
        if option_type == "call":
            return 1.0 if S > K * math.exp(-r * T) else 0.0
        else:
            return -1.0 if S < K * math.exp(-r * T) else 0.0
    
    d1_val = d1(S, K, r, sigma, T)
    
    if option_type == "call":
        return normal_cdf(d1_val)
    else:
        return normal_cdf(d1_val) - 1.0


def gamma(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """
    Calculate option gamma (same for calls and puts).
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate (annualized)
        sigma: Volatility (annualized)
        
    Returns:
        Gamma (rate of change of delta with respect to stock price)
        
    Golden check: S=100, K=100, r=0.05, sigma=0.2, T=1 → ≈0.018762
    """
    if T <= 0 or sigma <= 0:
        return 0.0
    
    d1_val = d1(S, K, r, sigma, T)
    return normal_pdf(d1_val) / (S * sigma * math.sqrt(T))


def vega(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """
    Calculate option vega (same for calls and puts).
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate (annualized)
        sigma: Volatility (annualized)
        
    Returns:
        Vega (rate of change of option price with respect to volatility)
        Note: This is per 1.0 vol change. For 1% vol change, divide by 100.
        
    Golden check: S=100, K=100, r=0.05, sigma=0.2, T=1 → ≈37.5240
    """
    if T <= 0 or sigma <= 0:
        return 0.0
    
    d1_val = d1(S, K, r, sigma, T)
    return S * math.sqrt(T) * normal_pdf(d1_val)


def theta(S: float, K: float, T: float, r: float, sigma: float, option_type: OptionType) -> float:
    """
    Calculate option theta (annualized).
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate (annualized)
        sigma: Volatility (annualized)
        option_type: "call" or "put"
        
    Returns:
        Theta (rate of change of option price with respect to time, annualized)
        
    Golden check (call): S=100, K=100, r=0.05, sigma=0.2, T=1 → ≈-6.4140
    Golden check (put):  S=100, K=100, r=0.05, sigma=0.2, T=1 → ≈-1.6579
    """
    if T <= 0 or sigma <= 0:
        return 0.0
    
    d1_val = d1(S, K, r, sigma, T)
    d2_val = d2(d1_val, sigma, T)
    
    term1 = -S * normal_pdf(d1_val) * sigma / (2 * math.sqrt(T))
    
    if option_type == "call":
        term2 = -r * K * math.exp(-r * T) * normal_cdf(d2_val)
    else:
        term2 = r * K * math.exp(-r * T) * normal_cdf(-d2_val)
    
    return term1 + term2


def rho(S: float, K: float, T: float, r: float, sigma: float, option_type: OptionType) -> float:
    """
    Calculate option rho.
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate (annualized)
        sigma: Volatility (annualized)
        option_type: "call" or "put"
        
    Returns:
        Rho (rate of change of option price with respect to risk-free rate)
        
    Golden check (call): S=100, K=100, r=0.05, sigma=0.2, T=1 → ≈53.2325
    Golden check (put):  S=100, K=100, r=0.05, sigma=0.2, T=1 → ≈-41.8905
    """
    if T <= 0 or sigma <= 0:
        return 0.0
    
    d2_val = d2(d1(S, K, r, sigma, T), sigma, T)
    
    if option_type == "call":
        return K * T * math.exp(-r * T) * normal_cdf(d2_val)
    else:
        return -K * T * math.exp(-r * T) * normal_cdf(-d2_val)


def calculate_all_greeks(S: float, K: float, T: float, r: float, sigma: float, option_type: OptionType) -> Dict[str, float]:
    """
    Calculate all option Greeks.
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate (annualized)
        sigma: Volatility (annualized)
        option_type: "call" or "put"
        
    Returns:
        Dictionary containing all Greeks
    """
    return {
        "delta": delta(S, K, T, r, sigma, option_type),
        "gamma": gamma(S, K, T, r, sigma),
        "vega": vega(S, K, T, r, sigma),
        "theta": theta(S, K, T, r, sigma, option_type),
        "rho": rho(S, K, T, r, sigma, option_type)
    }
