from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Union
import math
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Basic Mathematical Operations
Simple, efficient implementations of fundamental math operations.
"""



def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Add two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b


def multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Multiply two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Product of a and b
    """
    return a * b


def divide(a: Union[int, float], b: Union[int, float]) -> float:
    """
    Divide a by b.
    
    Args:
        a: Numerator
        b: Denominator
        
    Returns:
        Quotient of a divided by b
        
    Raises:
        ZeroDivisionError: If b is zero
    """
    if b == 0:
        raise ZeroDivisionError("Division by zero")
    return a / b


def power(base: Union[int, float], exponent: Union[int, float]) -> float:
    """
    Raise base to the power of exponent.
    
    Args:
        base: The base number
        exponent: The exponent
        
    Returns:
        base raised to the power of exponent
    """
    return base ** exponent 