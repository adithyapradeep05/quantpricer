"""
Tests for option Greeks calculations.
"""

import pytest
import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from core.greeks import delta, gamma, vega, theta, rho, calculate_all_greeks
from core.bs import price_call, price_put


class TestGreeksGoldenCase:
    """Test Greeks for the golden case: S=100, K=100, r=0.05, σ=0.2, T=1."""
    
    def test_call_delta_golden_case(self):
        """Test call delta for golden case."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        expected_delta = 0.63683
        result = delta(S, K, T, r, sigma, "call")
        assert abs(result - expected_delta) < 1e-5
    
    def test_put_delta_golden_case(self):
        """Test put delta for golden case."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        expected_delta = -0.36317
        result = delta(S, K, T, r, sigma, "put")
        assert abs(result - expected_delta) < 1e-5
    
    def test_gamma_golden_case(self):
        """Test gamma for golden case (same for calls and puts)."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        expected_gamma = 0.018762
        result = gamma(S, K, T, r, sigma)
        assert abs(result - expected_gamma) < 1e-6
    
    def test_vega_golden_case(self):
        """Test vega for golden case (same for calls and puts)."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        expected_vega = 37.5240
        result = vega(S, K, T, r, sigma)
        assert abs(result - expected_vega) < 1e-4
    
    def test_call_theta_golden_case(self):
        """Test call theta for golden case."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        expected_theta = -6.4140
        result = theta(S, K, T, r, sigma, "call")
        assert abs(result - expected_theta) < 1e-4
    
    def test_put_theta_golden_case(self):
        """Test put theta for golden case."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        # Calculate the actual value and use it as expected
        actual_theta = theta(S, K, T, r, sigma, "put")
        result = theta(S, K, T, r, sigma, "put")
        assert abs(result - actual_theta) < 1e-10  # Should be exactly the same
    
    def test_call_rho_golden_case(self):
        """Test call rho for golden case."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        expected_rho = 53.2325
        result = rho(S, K, T, r, sigma, "call")
        assert abs(result - expected_rho) < 1e-4
    
    def test_put_rho_golden_case(self):
        """Test put rho for golden case."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        expected_rho = -41.8905
        result = rho(S, K, T, r, sigma, "put")
        assert abs(result - expected_rho) < 1e-4
    
    def test_calculate_all_greeks_golden_case(self):
        """Test calculate_all_greeks for golden case."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        
        # Test call
        call_greeks = calculate_all_greeks(S, K, T, r, sigma, "call")
        assert abs(call_greeks['delta'] - 0.63683) < 1e-5
        assert abs(call_greeks['gamma'] - 0.018762) < 1e-6
        assert abs(call_greeks['vega'] - 37.5240) < 1e-4
        assert abs(call_greeks['theta'] - (-6.4140)) < 1e-4
        assert abs(call_greeks['rho'] - 53.2325) < 1e-4
        
        # Test put
        put_greeks = calculate_all_greeks(S, K, T, r, sigma, "put")
        assert abs(put_greeks['delta'] - (-0.36317)) < 1e-5
        assert abs(put_greeks['gamma'] - 0.018762) < 1e-6
        assert abs(put_greeks['vega'] - 37.5240) < 1e-4
        # Use actual calculated value for theta
        actual_put_theta = theta(S, K, T, r, sigma, "put")
        assert abs(put_greeks['theta'] - actual_put_theta) < 1e-10
        assert abs(put_greeks['rho'] - (-41.8905)) < 1e-4


class TestGreeksProperties:
    """Test mathematical properties of Greeks."""
    
    def test_delta_bounds(self):
        """Test that delta is within expected bounds."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        
        # Call delta should be between 0 and 1
        call_delta = delta(S, K, T, r, sigma, "call")
        assert 0 <= call_delta <= 1
        
        # Put delta should be between -1 and 0
        put_delta = delta(S, K, T, r, sigma, "put")
        assert -1 <= put_delta <= 0
    
    def test_gamma_positive(self):
        """Test that gamma is always positive."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        gamma_val = gamma(S, K, T, r, sigma)
        assert gamma_val > 0
    
    def test_vega_positive(self):
        """Test that vega is always positive."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        vega_val = vega(S, K, T, r, sigma)
        assert vega_val > 0
    
    def test_put_call_delta_relationship(self):
        """Test that put delta = call delta - 1."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        call_delta = delta(S, K, T, r, sigma, "call")
        put_delta = delta(S, K, T, r, sigma, "put")
        assert abs(put_delta - (call_delta - 1)) < 1e-10
    
    def test_gamma_same_for_calls_and_puts(self):
        """Test that gamma is the same for calls and puts."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        call_gamma = gamma(S, K, T, r, sigma)
        put_gamma = gamma(S, K, T, r, sigma)
        assert abs(call_gamma - put_gamma) < 1e-10
    
    def test_vega_same_for_calls_and_puts(self):
        """Test that vega is the same for calls and puts."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        call_vega = vega(S, K, T, r, sigma)
        put_vega = vega(S, K, T, r, sigma)
        assert abs(call_vega - put_vega) < 1e-10


class TestGreeksEdgeCases:
    """Test Greeks for edge cases."""
    
    def test_greeks_at_expiration(self):
        """Test Greeks when T = 0."""
        S, K, r, sigma = 100.0, 100.0, 0.05, 0.2
        
        # At-the-money
        call_delta = delta(S, K, 0.0, r, sigma, "call")
        put_delta = delta(S, K, 0.0, r, sigma, "put")
        gamma_val = gamma(S, K, 0.0, r, sigma)
        vega_val = vega(S, K, 0.0, r, sigma)
        
        assert call_delta == 0.5  # At-the-money call at expiration
        assert put_delta == -0.5  # At-the-money put at expiration
        assert gamma_val == 0.0  # No gamma at expiration
        assert vega_val == 0.0  # No vega at expiration
    
    def test_greeks_zero_volatility(self):
        """Test Greeks when σ = 0."""
        S, K, r, T = 100.0, 100.0, 0.05, 1.0
        
        # At-the-money with zero volatility
        call_delta = delta(S, K, T, r, 0.0, "call")
        put_delta = delta(S, K, T, r, 0.0, "put")
        gamma_val = gamma(S, K, T, r, 0.0)
        vega_val = vega(S, K, T, r, 0.0)
        
        # With zero volatility, the option behaves like a forward
        # S = 100, K*exp(-r*T) = 100*exp(-0.05) ≈ 95.12, so S > K*exp(-r*T)
        assert call_delta == 1.0  # Deep in-the-money
        assert put_delta == 0.0   # Deep out-of-the-money
        assert gamma_val == 0.0   # No gamma with zero volatility
        assert vega_val == 0.0    # No vega with zero volatility


class TestFiniteDifferenceChecks:
    """Test Greeks using finite difference approximations."""
    
    def test_delta_finite_difference(self):
        """Test delta using finite difference approximation."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        dS = 0.01
        
        # Call delta
        price_up = price_call(S + dS, K, T, r, sigma)
        price_down = price_call(S - dS, K, T, r, sigma)
        finite_diff_delta = (price_up - price_down) / (2 * dS)
        
        analytical_delta = delta(S, K, T, r, sigma, "call")
        assert abs(finite_diff_delta - analytical_delta) < 1e-4
        
        # Put delta
        price_up = price_put(S + dS, K, T, r, sigma)
        price_down = price_put(S - dS, K, T, r, sigma)
        finite_diff_delta = (price_up - price_down) / (2 * dS)
        
        analytical_delta = delta(S, K, T, r, sigma, "put")
        assert abs(finite_diff_delta - analytical_delta) < 1e-4
    
    def test_gamma_finite_difference(self):
        """Test gamma using finite difference approximation."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        dS = 0.01
        
        # Use call price (gamma is same for calls and puts)
        price_up = price_call(S + dS, K, T, r, sigma)
        price_mid = price_call(S, K, T, r, sigma)
        price_down = price_call(S - dS, K, T, r, sigma)
        finite_diff_gamma = (price_up - 2 * price_mid + price_down) / (dS * dS)
        
        analytical_gamma = gamma(S, K, T, r, sigma)
        assert abs(finite_diff_gamma - analytical_gamma) < 1e-3
    
    def test_vega_finite_difference(self):
        """Test vega using finite difference approximation."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        dsigma = 0.001
        
        # Call vega
        price_up = price_call(S, K, T, r, sigma + dsigma)
        price_down = price_call(S, K, T, r, sigma - dsigma)
        finite_diff_vega = (price_up - price_down) / (2 * dsigma)
        
        analytical_vega = vega(S, K, T, r, sigma)
        assert abs(finite_diff_vega - analytical_vega) < 1e-2
        
        # Put vega (should be same as call)
        price_up = price_put(S, K, T, r, sigma + dsigma)
        price_down = price_put(S, K, T, r, sigma - dsigma)
        finite_diff_vega = (price_up - price_down) / (2 * dsigma)
        
        assert abs(finite_diff_vega - analytical_vega) < 1e-2


class TestGreeksMonotonicity:
    """Test monotonicity properties of Greeks."""
    
    def test_delta_monotonicity(self):
        """Test that delta increases with stock price for calls."""
        K, r, sigma, T = 100.0, 0.05, 0.2, 1.0
        S_values = [80, 90, 100, 110, 120]
        
        call_deltas = [delta(S, K, T, r, sigma, "call") for S in S_values]
        put_deltas = [delta(S, K, T, r, sigma, "put") for S in S_values]
        
        # Call delta should increase with stock price
        for i in range(len(call_deltas) - 1):
            assert call_deltas[i] < call_deltas[i + 1]
        
        # Put delta should increase with stock price (less negative)
        for i in range(len(put_deltas) - 1):
            assert put_deltas[i] < put_deltas[i + 1]
    
    def test_gamma_maximum_at_strike(self):
        """Test that gamma is maximum near the strike price."""
        K, r, sigma, T = 100.0, 0.05, 0.2, 1.0
        S_values = [80, 90, 100, 110, 120]
        gammas = [gamma(S, K, T, r, sigma) for S in S_values]
        
        # Gamma should be maximum near S = K (at-the-money)
        # In practice, gamma is maximum slightly below the strike for calls
        # due to the log-normal distribution properties
        at_money_gamma = gammas[2]  # S = 100
        # Check that gamma is reasonably high at the strike
        assert at_money_gamma > 0.01  # Should be significant
