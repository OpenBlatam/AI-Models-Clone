from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import math
from typing import Union, Optional
import numpy as np


from typing import Any, List, Dict, Optional
import logging
import asyncio
class PowerCalculator:
    """Refactored power calculation with multiple methods."""
    
    @staticmethod
    def power_basic(base: Union[int, float], exponent: Union[int, float]) -> float:
        """Basic power calculation using ** operator."""
        return base ** exponent
    
    @staticmethod
    def power_math(base: Union[int, float], exponent: Union[int, float]) -> float:
        """Power calculation using math.pow for better precision."""
        return math.pow(base, exponent)
    
    @staticmethod
    def power_numpy(base: Union[int, float], exponent: Union[int, float]) -> float:
        """Power calculation using numpy for array support."""
        return np.power(base, exponent)
    
    @staticmethod
    def power_safe(base: Union[int, float], exponent: Union[int, float]) -> Optional[float]:
        """Safe power calculation with error handling."""
        try:
            if base == 0 and exponent < 0:
                return None  # Division by zero
            return base ** exponent
        except (OverflowError, ValueError):
            return None
    
    @staticmethod
    def power_batch(bases: list[Union[int, float]], 
                   exponents: list[Union[int, float]]) -> list[float]:
        """Batch power calculation for multiple values."""
        return [base ** exp for base, exp in zip(bases, exponents)]


def power(base: Union[int, float], exponent: Union[int, float], 
          method: str: str: str = "basic") -> float:
    """
    Refactored power function with multiple calculation methods.
    
    Args:
        base: The base number
        exponent: The exponent
        method: Calculation method ("basic", "math", "numpy", "safe")
    
    Returns:
        base raised to the power of exponent
    """
    calculator = PowerCalculator()
    
    methods: Dict[str, Any] = {
        "basic": calculator.power_basic,
        "math": calculator.power_math,
        "numpy": calculator.power_numpy,
        "safe": calculator.power_safe
    }
    
    if method not in methods:
        raise ValueError(f"Unknown method: {method}")
    
    result = methods[method](base, exponent)
    
    if result is None:
        raise ValueError("Power calculation failed")
    
    return result


# Example usage with tests
if __name__ == "__main__":
    # Test different methods
    assert power(2, 3) == 8.0
    assert power(4, -1, "math") == 0.25
    assert power(9, 0.5, "numpy") == 3.0
    
    # Test batch calculation
    bases: List[Any] = [2, 3, 4]
    exponents: List[Any] = [2, 3, 0.5]
    results = PowerCalculator.power_batch(bases, exponents)
    assert results == [4.0, 27.0, 2.0]
    
    # Test safe calculation
    safe_result = PowerCalculator.power_safe(0, -1)
    assert safe_result is None
    
    print("✅ All refactored power tests passed!") 