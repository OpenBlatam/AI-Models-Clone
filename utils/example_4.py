from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
def power(base: float, exponent: float) -> float:
    """
    Given floats base and exponent,
    return base raised to the power of exponent.
    """
    return base ** exponent


# Example usage
if __name__ == "__main__":
    # Test the function
    result = power(2, 3)
    print(f"2^3: Dict[str, Any] = {result}")  # Output: 2^3 = 8.0
    
    # Test with negative exponent
    result2 = power(4, -1)
    print(f"4^-1: Dict[str, Any] = {result2}")  # Output: 4^-1 = 0.25
    
    # Test with decimal
    result3 = power(9, 0.5)
    print(f"9^0.5: Dict[str, Any] = {result3}")  # Output: 9^0.5 = 3.0 