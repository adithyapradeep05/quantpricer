"""
Tests for Black-Scholes option pricing functions.
"""

import pytest
import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from core.bs import d1, d2, price_call, price_put, black_scholes_price


class TestD1D2:
    """Test d1 and d2 calculations."""
    
    def test_d1_golden_case(self):
        """Test d1 for golden case: S=100, K=100, r=0.05, σ=0.2, T=1."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        expected_d1 = 0.3500
        result = d1(S, K, r, sigma, T)
        assert abs(result - expected_d1) < 1e-4
    
    def test_d2_golden_case(self):
        """Test d2 for golden case: S=100, K=100, r=0.05, σ=0.2, T=1."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        d1_val = d1(S, K, r, sigma, T)
        expected_d2 = 0.1500
        result = d2(d1_val, sigma, T)
        assert abs(result - expected_d2) < 1e-4
    
    def test_d1_d2_relationship(self):
        """Test that d2 = d1 - σ√T."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        d1_val = d1(S, K, r, sigma, T)
        d2_val = d2(d1_val, sigma, T)
        expected_diff = sigma * math.sqrt(T)
        assert abs(d1_val - d2_val - expected_diff) < 1e-10
    
    def test_d1_edge_cases(self):
        """Test d1 for edge cases."""
        result = d1(100, 100, 0.05, 0.2, 0.0)
        assert result == float('inf')
        
        result = d1(110, 100, 0.05, 0.2, 0.0)
        assert result == float('inf')
        
        result = d1(90, 100, 0.05, 0.2, 0.0)
        assert result == float('-inf')


class TestBlackScholesPricing:
    """Test Black-Scholes option pricing."""
    
    def test_call_golden_case(self):
        """Test call price for golden case: S=100, K=100, r=0.05, σ=0.2, T=1."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        expected_price = 10.4506
        result = price_call(S, K, T, r, sigma)
        assert abs(result - expected_price) < 1e-4
    
    def test_put_golden_case(self):
        """Test put price for golden case: S=100, K=100, r=0.05, σ=0.2, T=1."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        expected_price = 5.5735
        result = price_put(S, K, T, r, sigma)
        assert abs(result - expected_price) < 1e-4
    
    def test_put_call_parity(self):
        """Test put-call parity: C - P = S - K*exp(-r*T)."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        call_price = price_call(S, K, T, r, sigma)
        put_price = price_put(S, K, T, r, sigma)
        
        expected_diff = S - K * math.exp(-r * T)
        actual_diff = call_price - put_price
        
        assert abs(actual_diff - expected_diff) < 1e-6
    
    def test_edge_case_zero_time(self):
        """Test pricing when T = 0 (expiration)."""
        S, K, r, sigma = 100.0, 100.0, 0.05, 0.2
        
        call_price = price_call(S, K, 0.0, r, sigma)
        put_price = price_put(S, K, 0.0, r, sigma)
        assert call_price == 0.0
        assert put_price == 0.0
        
        call_price = price_call(110, 100, 0.0, r, sigma)
        assert call_price == 10.0
        
        call_price = price_call(90, 100, 0.0, r, sigma)
        assert call_price == 0.0
        
        put_price = price_put(90, 100, 0.0, r, sigma)
        assert put_price == 10.0
        
        put_price = price_put(110, 100, 0.0, r, sigma)
        assert put_price == 0.0
    
    def test_edge_case_zero_volatility(self):
        """Test pricing when σ = 0 (deterministic)."""
        S, K, r, T = 100.0, 100.0, 0.05, 1.0
        
        # At-the-money
        call_price = price_call(S, K, T, r, 0.0)
        put_price = price_put(S, K, T, r, 0.0)
        
        expected_call = max(0, S - K * math.exp(-r * T))
        expected_put = max(0, K * math.exp(-r * T) - S)
        
        assert abs(call_price - expected_call) < 1e-6
        assert abs(put_price - expected_put) < 1e-6
    
    def test_input_validation(self):
        """Test input validation."""
        # Negative stock price
        with pytest.raises(ValueError, match="Stock price must be positive"):
            price_call(-100, 100, 1.0, 0.05, 0.2)
        
        # Negative strike price
        with pytest.raises(ValueError, match="Strike price must be positive"):
            price_call(100, -100, 1.0, 0.05, 0.2)
        
        # Negative volatility
        with pytest.raises(ValueError, match="Volatility must be non-negative"):
            price_call(100, 100, 1.0, 0.05, -0.2)
        
        # Negative time
        with pytest.raises(ValueError, match="Time to expiration must be non-negative"):
            price_call(100, 100, -1.0, 0.05, 0.2)


class TestBlackScholesPriceFunction:
    """Test the main black_scholes_price function."""
    
    def test_call_option(self):
        """Test call option pricing."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        expected_price = 10.4506
        result = black_scholes_price(S, K, T, r, sigma, "call")
        assert abs(result - expected_price) < 1e-4
    
    def test_put_option(self):
        """Test put option pricing."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        expected_price = 5.5735
        result = black_scholes_price(S, K, T, r, sigma, "put")
        assert abs(result - expected_price) < 1e-4
    
    def test_invalid_option_type(self):
        """Test invalid option type raises error."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        with pytest.raises(ValueError, match="option_type must be 'call' or 'put'"):
            black_scholes_price(S, K, T, r, sigma, "invalid")


class TestMonotonicity:
    """Test monotonicity properties of option prices."""
    
    def test_call_price_monotonicity_in_stock(self):
        """Test that call price increases with stock price."""
        K, r, sigma, T = 100.0, 0.05, 0.2, 1.0
        S_values = [80, 90, 100, 110, 120]
        prices = [price_call(S, K, T, r, sigma) for S in S_values]
        
        for i in range(len(prices) - 1):
            assert prices[i] < prices[i + 1]
    
    def test_put_price_monotonicity_in_stock(self):
        """Test that put price decreases with stock price."""
        K, r, sigma, T = 100.0, 0.05, 0.2, 1.0
        S_values = [80, 90, 100, 110, 120]
        prices = [price_put(S, K, T, r, sigma) for S in S_values]
        
        for i in range(len(prices) - 1):
            assert prices[i] > prices[i + 1]
    
    def test_price_monotonicity_in_volatility(self):
        """Test that both call and put prices increase with volatility."""
        S, K, r, T = 100.0, 100.0, 0.05, 1.0
        sigma_values = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        call_prices = [price_call(S, K, T, r, sigma) for sigma in sigma_values]
        put_prices = [price_put(S, K, T, r, sigma) for sigma in sigma_values]
        
        for i in range(len(call_prices) - 1):
            assert call_prices[i] < call_prices[i + 1]
            assert put_prices[i] < put_prices[i + 1]
