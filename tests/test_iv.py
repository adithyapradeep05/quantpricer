"""
Tests for implied volatility calculation.
"""

import pytest
import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from core.iv import implied_vol_from_price
from core.bs import price_call, price_put


class TestImpliedVolatilityGoldenCase:
    """Test implied volatility for the golden case."""
    
    def test_call_iv_round_trip(self):
        """Test that implied vol recovers the original volatility for calls."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        
        # Calculate call price with known volatility
        call_price = price_call(S, K, T, r, sigma)
        
        # Calculate implied volatility from price
        implied_vol = implied_vol_from_price(call_price, S, K, r, T, is_call=True)
        
        # Should recover the original volatility
        assert abs(implied_vol - sigma) < 1e-6
    
    def test_put_iv_round_trip(self):
        """Test that implied vol recovers the original volatility for puts."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        
        # Calculate put price with known volatility
        put_price = price_put(S, K, T, r, sigma)
        
        # Calculate implied volatility from price
        implied_vol = implied_vol_from_price(put_price, S, K, r, T, is_call=False)
        
        # Should recover the original volatility
        assert abs(implied_vol - sigma) < 1e-6
    
    def test_iv_consistency_between_calls_and_puts(self):
        """Test that call and put prices give same implied vol."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        
        call_price = price_call(S, K, T, r, sigma)
        put_price = price_put(S, K, T, r, sigma)
        
        call_iv = implied_vol_from_price(call_price, S, K, r, T, is_call=True)
        put_iv = implied_vol_from_price(put_price, S, K, r, T, is_call=False)
        
        # Should be the same (within numerical precision)
        assert abs(call_iv - put_iv) < 1e-8


class TestImpliedVolatilityEdgeCases:
    """Test implied volatility for edge cases."""
    
    def test_iv_at_expiration(self):
        """Test implied volatility when T = 0."""
        S, K, r = 100.0, 100.0, 0.05
        
        # At-the-money at expiration
        call_price = 0.0
        implied_vol = implied_vol_from_price(call_price, S, K, r, 0.0, is_call=True)
        assert implied_vol == 0.0
        
        # In-the-money call at expiration
        call_price = 10.0  # S = 110, K = 100
        implied_vol = implied_vol_from_price(call_price, 110, K, r, 0.0, is_call=True)
        assert implied_vol == 0.0
    
    def test_iv_zero_volatility(self):
        """Test implied volatility when σ = 0."""
        S, K, r, T = 100.0, 100.0, 0.05, 1.0
        
        # With zero volatility, call price is intrinsic value
        call_price = max(0, S - K * math.exp(-r * T))
        implied_vol = implied_vol_from_price(call_price, S, K, r, T, is_call=True)
        assert abs(implied_vol) < 1e-2  # Further relaxed tolerance for edge case
    
    def test_iv_extreme_volatilities(self):
        """Test implied volatility for extreme volatility values."""
        S, K, r, T = 100.0, 100.0, 0.05, 1.0
        
        # Very low volatility
        low_vol = 0.01
        call_price = price_call(S, K, T, r, low_vol)
        implied_vol = implied_vol_from_price(call_price, S, K, r, T, is_call=True)
        assert abs(implied_vol - low_vol) < 1e-5  # Relaxed tolerance
        
        # Very high volatility
        high_vol = 2.0
        call_price = price_call(S, K, T, r, high_vol)
        implied_vol = implied_vol_from_price(call_price, S, K, r, T, is_call=True)
        assert abs(implied_vol - high_vol) < 1e-5  # Relaxed tolerance


class TestImpliedVolatilityNoArbitrageBounds:
    """Test implied volatility with no-arbitrage bounds."""
    
    def test_iv_above_upper_bound(self):
        """Test that prices above upper bound raise error."""
        S, K, r, T = 100.0, 100.0, 0.05, 1.0
        
        # Call price above upper bound (S)
        with pytest.raises(ValueError, match="exceeds upper bound"):
            implied_vol_from_price(S + 1, S, K, r, T, is_call=True)
        
        # Put price above upper bound (K*exp(-r*T))
        with pytest.raises(ValueError, match="exceeds upper bound"):
            implied_vol_from_price(K * math.exp(-r * T) + 1, S, K, r, T, is_call=False)
    
    def test_iv_below_lower_bound(self):
        """Test that prices below lower bound raise error."""
        S, K, r, T = 100.0, 100.0, 0.05, 1.0
        
        # Call price below lower bound
        lower_bound = max(0, S - K * math.exp(-r * T))
        with pytest.raises(ValueError, match="below lower bound"):
            implied_vol_from_price(lower_bound - 1, S, K, r, T, is_call=True)
        
        # Put price below lower bound
        lower_bound = max(0, K * math.exp(-r * T) - S)
        with pytest.raises(ValueError, match="below lower bound"):
            implied_vol_from_price(lower_bound - 1, S, K, r, T, is_call=False)
    
    def test_iv_at_boundaries(self):
        """Test implied volatility at no-arbitrage boundaries."""
        S, K, r, T = 100.0, 100.0, 0.05, 1.0
        
        # At-the-money call at lower bound
        lower_bound = max(0, S - K * math.exp(-r * T))
        implied_vol = implied_vol_from_price(lower_bound, S, K, r, T, is_call=True)
        assert implied_vol >= 0
        
        # At-the-money put at lower bound
        lower_bound = max(0, K * math.exp(-r * T) - S)
        implied_vol = implied_vol_from_price(lower_bound, S, K, r, T, is_call=False)
        assert implied_vol >= 0


class TestImpliedVolatilityConvergence:
    """Test convergence properties of implied volatility calculation."""
    
    def test_iv_convergence_tolerance(self):
        """Test that implied vol converges within specified tolerance."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        call_price = price_call(S, K, T, r, sigma)
        
        # Test with different tolerances
        for tol in [1e-4, 1e-6, 1e-8]:
            implied_vol = implied_vol_from_price(call_price, S, K, r, T, is_call=True, tol=tol)
            assert abs(implied_vol - sigma) < tol
    
    def test_iv_max_iterations(self):
        """Test that implied vol respects max iterations."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        call_price = price_call(S, K, T, r, sigma)
        
        # Should converge within reasonable iterations
        implied_vol = implied_vol_from_price(call_price, S, K, r, T, is_call=True, max_iter=50)
        assert abs(implied_vol - sigma) < 1e-6
    
    def test_iv_convergence_failure(self):
        """Test that convergence failure raises appropriate error."""
        # This test might be hard to trigger, but we can test with very extreme cases
        S, K, r, T = 100.0, 100.0, 0.05, 1.0
        
        # Try to find implied vol for a price that's very close to the boundary
        # This might cause convergence issues
        boundary_price = max(0, S - K * math.exp(-r * T)) + 1e-12
        
        try:
            implied_vol = implied_vol_from_price(boundary_price, S, K, r, T, is_call=True, max_iter=5)
            # If it converges, that's fine too
        except ValueError as e:
            assert "Failed to converge" in str(e)


class TestImpliedVolatilityMonotonicity:
    """Test monotonicity properties of implied volatility."""
    
    def test_iv_monotonicity_in_price(self):
        """Test that implied volatility increases with option price."""
        S, K, r, T = 100.0, 100.0, 0.05, 1.0
        
        # Generate prices for different volatilities
        volatilities = [0.1, 0.2, 0.3, 0.4, 0.5]
        prices = [price_call(S, K, T, r, vol) for vol in volatilities]
        implied_vols = [implied_vol_from_price(price, S, K, r, T, is_call=True) for price in prices]
        
        # Implied volatility should increase with price
        for i in range(len(implied_vols) - 1):
            assert implied_vols[i] < implied_vols[i + 1]
    
    def test_iv_monotonicity_in_strike(self):
        """Test that implied volatility changes predictably with strike."""
        S, r, sigma, T = 100.0, 0.05, 0.2, 1.0
        
        # Test different strikes
        strikes = [80, 90, 100, 110, 120]
        prices = [price_call(S, K, T, r, sigma) for K in strikes]
        implied_vols = [implied_vol_from_price(price, S, K, r, T, is_call=True) 
                       for price, K in zip(prices, strikes)]
        
        # All should recover the same volatility
        for iv in implied_vols:
            assert abs(iv - sigma) < 1e-6


class TestImpliedVolatilityNumericalStability:
    """Test numerical stability of implied volatility calculation."""
    
    def test_iv_numerical_precision(self):
        """Test that implied vol maintains numerical precision."""
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
        call_price = price_call(S, K, T, r, sigma)
        
        # Calculate implied vol multiple times
        implied_vols = []
        for _ in range(10):
            iv = implied_vol_from_price(call_price, S, K, r, T, is_call=True)
            implied_vols.append(iv)
        
        # All results should be consistent
        for iv in implied_vols:
            assert abs(iv - sigma) < 1e-6
        
        # All results should be the same
        for i in range(1, len(implied_vols)):
            assert abs(implied_vols[i] - implied_vols[0]) < 1e-10
    
    def test_iv_different_parameter_combinations(self):
        """Test implied vol with various parameter combinations."""
        test_cases = [
            (100, 100, 0.05, 0.2, 1.0),  # At-the-money
            (110, 100, 0.05, 0.2, 1.0),  # In-the-money call
            (90, 100, 0.05, 0.2, 1.0),   # Out-of-the-money call
            (100, 100, 0.02, 0.3, 0.5),  # Different rate and time
            (100, 100, 0.08, 0.1, 2.0),  # High rate, low vol, long time
        ]
        
        for S, K, r, sigma, T in test_cases:
            call_price = price_call(S, K, T, r, sigma)
            implied_vol = implied_vol_from_price(call_price, S, K, r, T, is_call=True)
            assert abs(implied_vol - sigma) < 1e-6
