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


# Test the function
if __name__ == "__main__":
    # Test cases
    print("Testing add function:")
    print(f"add(1, 2) = {add(1, 2)}")  # Should be 3
    print(f"add(5, 3) = {add(5, 3)}")  # Should be 8
    print(f"add(-2, 7) = {add(-2, 7)}")  # Should be 5
    
    # Assertion tests
    assert add(1, 2) == 3, f"Expected 3, but got {add(1, 2)}"
    assert add(5, 3) == 8, f"Expected 8, but got {add(5, 3)}"
    assert add(-2, 7) == 5, f"Expected 5, but got {add(-2, 7)}"
    
    print("✅ All tests passed!") 