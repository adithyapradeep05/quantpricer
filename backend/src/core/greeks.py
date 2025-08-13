"""
Option Greeks calculations using Black-Scholes formulas.
Uses core modules, no SciPy dependency.
"""

import math
from typing import Literal, Dict, Any
from .normals import normal_pdf, normal_cdf, safe_sqrt
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
    
    try:
        d1_val = d1(S, K, r, sigma, T)
        
        if option_type == "call":
            return normal_cdf(d1_val)
        else:
            return normal_cdf(d1_val) - 1.0
    except (ValueError, OverflowError) as e:
        raise ValueError(f"Error in delta calculation: {e}")


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
    
    try:
        d1_val = d1(S, K, r, sigma, T)
        denominator = S * sigma * safe_sqrt(T)
        
        if denominator <= 0:
            return 0.0
            
        return normal_pdf(d1_val) / denominator
    except (ValueError, OverflowError, ZeroDivisionError) as e:
        raise ValueError(f"Error in gamma calculation: {e}")


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
    
    try:
        d1_val = d1(S, K, r, sigma, T)
        return S * safe_sqrt(T) * normal_pdf(d1_val)
    except (ValueError, OverflowError) as e:
        raise ValueError(f"Error in vega calculation: {e}")


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
        Theta (rate of change of option price with respect to time)
        Note: This is annualized. For daily theta, divide by 365.
        
    Golden check (call): S=100, K=100, r=0.05, sigma=0.2, T=1 → ≈-6.4140
    """
    if T <= 0:
        return 0.0
    
    if sigma <= 0:
        if option_type == "call":
            return -r * K * math.exp(-r * T) if S > K * math.exp(-r * T) else 0.0
        else:
            return r * K * math.exp(-r * T) if S < K * math.exp(-r * T) else 0.0
    
    try:
        d1_val = d1(S, K, r, sigma, T)
        d2_val = d2(d1_val, sigma, T)
        
        if option_type == "call":
            return -(S * normal_pdf(d1_val) * sigma) / (2 * safe_sqrt(T)) - r * K * math.exp(-r * T) * normal_cdf(d2_val)
        else:
            return -(S * normal_pdf(d1_val) * sigma) / (2 * safe_sqrt(T)) + r * K * math.exp(-r * T) * normal_cdf(-d2_val)
    except (ValueError, OverflowError, ZeroDivisionError) as e:
        raise ValueError(f"Error in theta calculation: {e}")


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
        Note: This is per 1.0 rate change. For 1% rate change, divide by 100.
        
    Golden check (call): S=100, K=100, r=0.05, sigma=0.2, T=1 → ≈53.2325
    Golden check (put):  S=100, K=100, r=0.05, sigma=0.2, T=1 → ≈-41.8905
    """
    if T <= 0:
        return 0.0
    
    if sigma <= 0:
        return 0.0
    
    try:
        d1_val = d1(S, K, r, sigma, T)
        d2_val = d2(d1_val, sigma, T)
        
        if option_type == "call":
            return K * T * math.exp(-r * T) * normal_cdf(d2_val)
        else:
            return -K * T * math.exp(-r * T) * normal_cdf(-d2_val)
    except (ValueError, OverflowError) as e:
        raise ValueError(f"Error in rho calculation: {e}")


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
    try:
        return {
            "delta": delta(S, K, T, r, sigma, option_type),
            "gamma": gamma(S, K, T, r, sigma),
            "vega": vega(S, K, T, r, sigma),
            "theta": theta(S, K, T, r, sigma, option_type),
            "rho": rho(S, K, T, r, sigma, option_type)
        }
    except Exception as e:
        raise ValueError(f"Error calculating Greeks: {e}")
