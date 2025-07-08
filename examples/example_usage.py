#!/usr/bin/env python3
"""
Example of using the TDD wrapper with Claude Code
"""

import sys
from pathlib import Path

# This file demonstrates how the TDD wrapper enforces test-driven development

def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def factorial(n):
    """Calculate factorial of n"""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0:
        return 1
    return n * factorial(n - 1)

def is_prime(n):
    """Check if a number is prime"""
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def main():
    """Main function demonstrating TDD workflow"""
    print("TDD Example - Mathematical Functions")
    print("=" * 40)
    
    # This code will only run if tests pass!
    print(f"Fibonacci(10) = {calculate_fibonacci(10)}")
    print(f"Factorial(5) = {factorial(5)}")
    print(f"Is 17 prime? {is_prime(17)}")
    
    print("\n✅ All functions executed successfully!")
    print("This means all tests passed before execution.")

if __name__ == "__main__":
    main()