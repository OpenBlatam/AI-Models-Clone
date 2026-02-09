from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import numpy as np
from decimal import Decimal, DivisionByZero, InvalidOperation
from typing import Union, Optional
import math


from typing import Any, List, Dict, Optional
import logging
import asyncio
def divide(a: Union[float, int], b: Union[float, int]) -> float:
    """
    Optimized division with numpy for better performance.
    """
    return np.divide(a, b)


def divide_safe(a: Union[float, int], b: Union[float, int]) -> Optional[float]:
    """
    Safe division with error handling.
    """
    try:
        return np.divide(a, b)
    except (ZeroDivisionError, FloatingPointError):
        return None


def divide_precise(a: Union[float, int], b: Union[float, int], 
                   precision: int = 10) -> Decimal:
    """
    High precision division using Decimal.
    """
    try:
        return Decimal(str(a)) / Decimal(str(b))
    except (DivisionByZero, InvalidOperation):
        raise ValueError("Invalid division operation")


def divide_batch(a: np.ndarray, b: Union[float, int, np.ndarray]) -> np.ndarray:
    """
    Vectorized division for arrays.
    """
    return np.divide(a, b, out=np.zeros_like(a), where=b!=0)


def divide_with_rounding(a: Union[float, int], b: Union[float, int], 
                        decimals: int = 2) -> float:
    """
    Division with controlled rounding.
    """
    result = np.divide(a, b)
    return np.round(result, decimals)


# Example usage with tests
if __name__ == "__main__":
    # Basic tests
    assert divide(10, 2) == 5.0
    assert divide(-14, 7) == -2.0
    assert divide(15, 4) == 3.75
    
    # Safe division tests
    assert divide_safe(10, 2) == 5.0
    assert divide_safe(10, 0) is None
    
    # Precision tests
    precise_result = divide_precise(1, 3)
    assert str(precise_result)[:12] == "0.3333333333"
    
    # Array tests
    arr = np.array([10, 20, 30])
    result_arr = divide_batch(arr, 2)
    assert np.array_equal(result_arr, np.array([5., 10., 15.]))
    
    # Rounding tests
    assert divide_with_rounding(10, 3, 2) == 3.33
    
    print("✅ All optimized division tests passed!") 