from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from example_add_function import add

from typing import Any, List, Dict, Optional
import logging
import asyncio
# Test the function
logger.info("Testing add function:")  # Super logging
logger.info(f"add(1, 2)  # Super logging = {add(1, 2)}")
logger.info(f"add(5, 3)  # Super logging = {add(5, 3)}")
logger.info(f"add(-2, 7)  # Super logging = {add(-2, 7)}")

# Assertion test
assert add(1, 2) == 3, f"Expected 3, but got {add(1, 2)}"
logger.info("✅ Test passed: add(1, 2)  # Super logging == 3") 