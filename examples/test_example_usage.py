#!/usr/bin/env python3
"""
Test file for example_usage.py - demonstrates TDD practices
"""

import pytest
from example_usage import calculate_fibonacci, factorial, is_prime

class TestFibonacci:
    """Test cases for Fibonacci calculation"""
    
    def test_fibonacci_base_cases(self):
        """Test base cases for Fibonacci"""
        assert calculate_fibonacci(0) == 0
        assert calculate_fibonacci(1) == 1
    
    def test_fibonacci_small_numbers(self):
        """Test Fibonacci for small numbers"""
        assert calculate_fibonacci(2) == 1
        assert calculate_fibonacci(3) == 2
        assert calculate_fibonacci(4) == 3
        assert calculate_fibonacci(5) == 5
    
    def test_fibonacci_larger_numbers(self):
        """Test Fibonacci for larger numbers"""
        assert calculate_fibonacci(10) == 55
        assert calculate_fibonacci(15) == 610

class TestFactorial:
    """Test cases for factorial calculation"""
    
    def test_factorial_base_case(self):
        """Test factorial of 0"""
        assert factorial(0) == 1
    
    def test_factorial_positive_numbers(self):
        """Test factorial for positive numbers"""
        assert factorial(1) == 1
        assert factorial(5) == 120
        assert factorial(10) == 3628800
    
    def test_factorial_negative_raises_error(self):
        """Test that factorial raises error for negative numbers"""
        with pytest.raises(ValueError):
            factorial(-1)

class TestPrime:
    """Test cases for prime number checking"""
    
    def test_numbers_less_than_two_not_prime(self):
        """Test that numbers < 2 are not prime"""
        assert not is_prime(0)
        assert not is_prime(1)
        assert not is_prime(-5)
    
    def test_known_primes(self):
        """Test known prime numbers"""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        for p in primes:
            assert is_prime(p), f"{p} should be prime"
    
    def test_known_composites(self):
        """Test known composite numbers"""
        composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20]
        for c in composites:
            assert not is_prime(c), f"{c} should not be prime"

# Example of TDD workflow:
# 1. Write these tests first (they will fail)
# 2. Run: tdd-python example_usage.py (will fail)
# 3. Implement the functions in example_usage.py
# 4. Run: tdd-python example_usage.py (will pass)
# 5. Refactor if needed while keeping tests green

if __name__ == "__main__":
    pytest.main([__file__, "-v"])