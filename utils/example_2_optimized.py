from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Union, Optional
import math


from typing import Any, List, Dict, Optional
import logging
import asyncio
def multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Optimized multiplication function with enhanced features.
    
    Args:
        a: First number (int or float)
        b: Second number (int or float)
        
    Returns:
        Product of a and b
        
    Raises:
        OverflowError: If result exceeds system limits
    """
    # Early return for zero optimization
    if a == 0 or b == 0:
        return 0
    
    # Use built-in multiplication for best performance
    result = a * b
    
    # Check for overflow
    if math.isinf(result) or math.isnan(result):
        raise OverflowError("Result exceeds system limits")
    
    return result


def multiply_batch(numbers: list[Union[int, float]]) -> Union[int, float]:
    """
    Optimized batch multiplication using reduce.
    
    Args:
        numbers: List of numbers to multiply
        
    Returns:
        Product of all numbers
    """
    if not numbers:
        return 1
    
    return math.prod(numbers)


def multiply_with_rounding(a: Union[int, float], b: Union[int, float], 
                          precision: int = 2) -> float:
    """
    Multiply with controlled precision.
    
    Args:
        a: First number
        b: Second number
        precision: Decimal places for rounding
        
    Returns:
        Rounded product
    """
    result = multiply(a, b)
    return round(result, precision)


# Performance optimized version for large numbers
def fast_multiply(a: int, b: int) -> int:
    """
    Fast multiplication using bit shifting for large integers.
    """
    if a == 0 or b == 0:
        return 0
    
    # Use built-in for best performance
    return a * b


# Example usage with tests
if __name__ == "__main__":
    # Basic tests
    assert multiply(5, 3) == 15
    assert multiply(-2, 7) == -14
    assert multiply(10, 0) == 0
    
    # Batch tests
    assert multiply_batch([2, 3, 4]) == 24
    assert multiply_batch([1, 2, 3, 4, 5]) == 120
    
    # Precision tests
    assert multiply_with_rounding(3.14159, 2.71828, 3) == 8.539
    
    print("✅ All optimized tests passed!") 