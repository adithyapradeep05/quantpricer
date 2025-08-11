"""
Implied volatility calculation using bisection and Newton-Raphson methods.
Uses core modules, no SciPy dependency.
"""

import math
from typing import Literal, Optional
from .bs import price_call, price_put, d1
from .normals import normal_pdf

OptionType = Literal["call", "put"]


def _price_function(S: float, K: float, T: float, r: float, sigma: float, option_type: OptionType, target_price: float) -> float:
    """
    Price function for root finding: f(sigma) = BS_price(sigma) - target_price.
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate (annualized)
        sigma: Volatility (annualized)
        option_type: "call" or "put"
        target_price: Target option price
        
    Returns:
        Difference between calculated price and target price
    """
    if option_type == "call":
        calculated_price = price_call(S, K, T, r, sigma)
    else:
        calculated_price = price_put(S, K, T, r, sigma)
    
    return calculated_price - target_price


def _vega_function(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """
    Vega function for Newton-Raphson method.
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate (annualized)
        sigma: Volatility (annualized)
        
    Returns:
        Vega (derivative of price with respect to volatility)
    """
    if T <= 0 or sigma <= 0:
        return 0.0
    
    d1_val = d1(S, K, r, sigma, T)
    return S * math.sqrt(T) * normal_pdf(d1_val)


def _check_no_arbitrage_bounds(S: float, K: float, T: float, r: float, option_type: OptionType, target_price: float) -> None:
    """
    Check if target price is within no-arbitrage bounds.
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate (annualized)
        option_type: "call" or "put"
        target_price: Target option price
        
    Raises:
        ValueError: If price is outside no-arbitrage bounds
    """
    if T <= 0:
        if option_type == "call":
            intrinsic = max(0, S - K)
        else:
            intrinsic = max(0, K - S)
        
        if abs(target_price - intrinsic) > 1e-10:
            raise ValueError(f"Price {target_price} is outside no-arbitrage bounds for T=0")
        return
    
    if option_type == "call":
        upper_bound = S
        lower_bound = max(0, S - K * math.exp(-r * T))
    else:
        upper_bound = K * math.exp(-r * T)
        lower_bound = max(0, K * math.exp(-r * T) - S)
    
    if target_price > upper_bound + 1e-10:
        raise ValueError(f"Price {target_price} exceeds upper bound {upper_bound}")
    if target_price < lower_bound - 1e-10:
        raise ValueError(f"Price {target_price} below lower bound {lower_bound}")


def implied_vol_from_price(price: float, S: float, K: float, r: float, T: float, 
                          is_call: bool = True, tol: float = 1e-8, max_iter: int = 100) -> float:
    """
    Calculate implied volatility from option price using bisection with Newton-Raphson fallback.
    
    Args:
        price: Market price of the option
        S: Current stock price
        K: Strike price
        r: Risk-free rate (annualized)
        T: Time to expiration (years)
        is_call: True for call option, False for put option
        tol: Tolerance for convergence
        max_iter: Maximum number of iterations
        
    Returns:
        Implied volatility
        
    Raises:
        ValueError: If price is outside no-arbitrage bounds or no solution found
    """
    option_type = "call" if is_call else "put"
    
    _check_no_arbitrage_bounds(S, K, T, r, option_type, price)
    
    if T <= 0:
        return 0.0
    
    sigma_low = 1e-6
    sigma_high = 5.0
    
    f_low = _price_function(S, K, T, r, sigma_low, option_type, price)
    f_high = _price_function(S, K, T, r, sigma_high, option_type, price)
    
    if f_low * f_high > 0:
        sigma_low = 1e-8
        f_low = _price_function(S, K, T, r, sigma_low, option_type, price)
        
        if f_low * f_high > 0:
            sigma_high = 10.0
            f_high = _price_function(S, K, T, r, sigma_high, option_type, price)
            
            if f_low * f_high > 0:
                raise ValueError("Cannot find valid volatility bracket")
    
    for i in range(max_iter):
        sigma_mid = (sigma_low + sigma_high) / 2
        f_mid = _price_function(S, K, T, r, sigma_mid, option_type, price)
        
        if abs(f_mid) < tol:
            return sigma_mid
        
        if f_mid * f_low > 0:
            sigma_low = sigma_mid
            f_low = f_mid
        else:
            sigma_high = sigma_mid
            f_high = f_mid
    
    sigma_guess = (sigma_low + sigma_high) / 2
    
    for i in range(max_iter):
        f_val = _price_function(S, K, T, r, sigma_guess, option_type, price)
        
        if abs(f_val) < tol:
            return sigma_guess
        
        vega_val = _vega_function(S, K, T, r, sigma_guess)
        
        if abs(vega_val) < 1e-12:
            return (sigma_low + sigma_high) / 2
        
        sigma_new = sigma_guess - f_val / vega_val
        
        if sigma_new <= 0:
            sigma_new = sigma_guess / 2
        
        if abs(sigma_new - sigma_guess) < tol:
            return sigma_new
        
        sigma_guess = sigma_new
    
    raise ValueError(f"Failed to converge after {max_iter} iterations")
