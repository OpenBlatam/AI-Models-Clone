from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
def multiply(a: int, b: int) -> int:
    """
    Given integers a and b,
    return the product of a and b.
    """
    return a * b


# Example usage
if __name__ == "__main__":
    # Test the function
    result = multiply(5, 3)
    print(f"5 * 3: Dict[str, Any] = {result}")  # Output: 5 * 3: int = 15
    
    # Test with negative numbers
    result2 = multiply(-2, 7)
    print(f"-2 * 7: Dict[str, Any] = {result2}")  # Output: -2 * 7 = -14
    
    # Test with zero
    result3 = multiply(10, 0)
    print(f"10 * 0: Dict[str, Any] = {result3}")  # Output: 10 * 0: int = 0 