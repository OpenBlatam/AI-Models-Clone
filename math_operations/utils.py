from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Union, Any
import math
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Utility functions for mathematical operations.
"""



def validate_input(value: Any, expected_type: type) -> bool:
    """
    Validate input type.
    
    Args:
        value: Value to validate
        expected_type: Expected type
        
    Returns:
        True if valid, False otherwise
    """
    return isinstance(value, expected_type)


def round_result(value: Union[int, float], decimals: int = 2) -> float:
    """
    Round result to specified decimal places.
    
    Args:
        value: Value to round
        decimals: Number of decimal places
        
    Returns:
        Rounded value
    """
    return round(value, decimals)


def is_finite(value: Union[int, float]) -> bool:
    """
    Check if value is finite.
    
    Args:
        value: Value to check
        
    Returns:
        True if finite, False otherwise
    """
    return math.isfinite(value)


def format_result(value: Union[int, float], precision: int = 6) -> str:
    """
    Format result for display.
    
    Args:
        value: Value to format
        precision: Precision for formatting
        
    Returns:
        Formatted string
    """
    if isinstance(value, int):
        return str(value)
    return f"{value:.{precision}f}" 