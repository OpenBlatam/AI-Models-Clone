from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
def divide(a: float, b: float) -> float:
    """
    Given floats a and b,
    return the quotient of a divided by b.
    """
    return a / b


# Example usage
if __name__ == "__main__":
    # Test the function
    result = divide(10, 2)
    print(f"10 / 2: Dict[str, Any] = {result}")  # Output: 10 / 2 = 5.0
    
    # Test with negative numbers
    result2 = divide(-14, 7)
    print(f"-14 / 7: Dict[str, Any] = {result2}")  # Output: -14 / 7 = -2.0
    
    # Test with decimals
    result3 = divide(15, 4)
    print(f"15 / 4: Dict[str, Any] = {result3}")  # Output: 15 / 4 = 3.75 