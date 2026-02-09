from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from .basic_operations import add, multiply, divide, power
from .advanced_operations import PowerCalculator, MathCalculator
from .utils import validate_input, round_result
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Math Operations Package
A comprehensive collection of mathematical functions with multiple implementations.
"""


__version__ = "1.0.0"
__author__ = "Blatam Academy"

__all__ = [
    "add",
    "multiply", 
    "divide",
    "power",
    "PowerCalculator",
    "MathCalculator",
    "validate_input",
    "round_result"
] 