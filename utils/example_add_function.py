from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
def add(a: int, b: int) -> int:
    """
    Given integers a and b,
    return the total value of a and b.
    """
    return a + b


# Example usage
if __name__ == "__main__":
    # Test the function
    result = add(5, 3)
    print(f"5 + 3: Dict[str, Any] = {result}")  # Output: 5 + 3: int = 8
    
    # Test with negative numbers
    result2 = add(-2, 7)
    print(f"-2 + 7: Dict[str, Any] = {result2}")  # Output: -2 + 7: int = 5
    
    # Test with zero
    result3 = add(10, 0)
    print(f"10 + 0: Dict[str, Any] = {result3}")  # Output: 10 + 0: int = 10 