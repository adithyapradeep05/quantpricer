"""
Tests for normal distribution functions.
"""

import pytest
import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from core.normals import normal_pdf, normal_cdf


class TestNormalPDF:
    """Test normal probability density function."""
    
    def test_normal_pdf_zero(self):
        """Test φ(0) = 1/√(2π) ≈ 0.3989422804."""
        expected = 1 / math.sqrt(2 * math.pi)
        result = normal_pdf(0.0)
        assert abs(result - expected) < 1e-10
        assert abs(result - 0.3989422804) < 1e-7
    
    def test_normal_pdf_one(self):
        """Test φ(1) ≈ 0.2419707245."""
        expected = 0.2419707245
        result = normal_pdf(1.0)
        assert abs(result - expected) < 1e-7
    
    def test_normal_pdf_symmetry(self):
        """Test φ(-x) = φ(x) for symmetry."""
        x_values = [0.5, 1.0, 2.0, 3.0]
        for x in x_values:
            assert abs(normal_pdf(x) - normal_pdf(-x)) < 1e-10
    
    def test_normal_pdf_negative(self):
        """Test φ(-1) ≈ 0.2419707245."""
        expected = 0.2419707245
        result = normal_pdf(-1.0)
        assert abs(result - expected) < 1e-7
    
    def test_normal_pdf_large_values(self):
        """Test φ(x) for large values approaches zero."""
        large_values = [5.0, 10.0, 20.0]
        for x in large_values:
            result = normal_pdf(x)
            assert result > 0  # Should be positive
            assert result < 1e-5  # Should be very small (relaxed tolerance)


class TestNormalCDF:
    """Test normal cumulative distribution function."""
    
    def test_normal_cdf_zero(self):
        """Test Φ(0) = 0.5."""
        expected = 0.5
        result = normal_cdf(0.0)
        assert abs(result - expected) < 1e-10
    
    def test_normal_cdf_one(self):
        """Test Φ(1) ≈ 0.8413447461."""
        expected = 0.8413447461
        result = normal_cdf(1.0)
        assert abs(result - expected) < 1e-7
    
    def test_normal_cdf_symmetry(self):
        """Test Φ(-x) = 1 - Φ(x) for symmetry."""
        x_values = [0.5, 1.0, 2.0, 3.0]
        for x in x_values:
            assert abs(normal_cdf(-x) - (1 - normal_cdf(x))) < 1e-10
    
    def test_normal_cdf_negative(self):
        """Test Φ(-1) ≈ 0.1586552539."""
        expected = 0.1586552539
        result = normal_cdf(-1.0)
        assert abs(result - expected) < 1e-7
    
    def test_normal_cdf_extreme_values(self):
        """Test Φ(x) for extreme values."""
        # Very negative values should approach 0
        assert normal_cdf(-10.0) < 1e-10
        
        # Very positive values should approach 1
        assert normal_cdf(10.0) > 1 - 1e-10
    
    def test_normal_cdf_monotonicity(self):
        """Test that Φ(x) is monotonically increasing."""
        x_values = [-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0]
        for i in range(len(x_values) - 1):
            assert normal_cdf(x_values[i]) < normal_cdf(x_values[i + 1])


class TestNormalFunctionsIntegration:
    """Integration tests for normal functions."""
    
    def test_pdf_cdf_relationship(self):
        """Test that PDF and CDF are consistent."""
        # The CDF should be the integral of the PDF
        # For small intervals, we can approximate the integral
        x = 1.0
        dx = 0.001
        
        # Approximate integral: ∫φ(t)dt from x-dx/2 to x+dx/2 ≈ φ(x) * dx
        pdf_at_x = normal_pdf(x)
        cdf_diff = normal_cdf(x + dx/2) - normal_cdf(x - dx/2)
        pdf_approx = cdf_diff / dx
        
        # Should be approximately equal
        assert abs(pdf_at_x - pdf_approx) < 1e-3
    
    def test_known_values(self):
        """Test against known mathematical values."""
        # Test some standard normal values
        test_cases = [
            (0.0, 0.3989422804, 0.5),
            (1.0, 0.2419707245, 0.8413447461),
            (2.0, 0.0539909665, 0.9772498681),
            (-1.0, 0.2419707245, 0.1586552539),
            (-2.0, 0.0539909665, 0.0227501319)
        ]
        
        for x, expected_pdf, expected_cdf in test_cases:
            assert abs(normal_pdf(x) - expected_pdf) < 1e-7
            assert abs(normal_cdf(x) - expected_cdf) < 1e-7
