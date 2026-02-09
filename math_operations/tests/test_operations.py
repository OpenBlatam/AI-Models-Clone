from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import unittest
from math_operations import add, multiply, divide, power, PowerCalculator, MathCalculator
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Test suite for math operations package.
"""



class TestBasicOperations(unittest.TestCase):
    """Test basic mathematical operations."""
    
    def test_add(self) -> Any:
        """Test addition function."""
        self.assertEqual(add(1, 2), 3)
        self.assertEqual(add(-1, 1), 0)
        self.assertEqual(add(0.1, 0.2), 0.3)
    
    def test_multiply(self) -> Any:
        """Test multiplication function."""
        self.assertEqual(multiply(2, 3), 6)
        self.assertEqual(multiply(-2, 3), -6)
        self.assertEqual(multiply(0, 5), 0)
    
    def test_divide(self) -> Any:
        """Test division function."""
        self.assertEqual(divide(6, 2), 3.0)
        self.assertEqual(divide(5, 2), 2.5)
        with self.assertRaises(ZeroDivisionError):
            divide(1, 0)
    
    def test_power(self) -> Any:
        """Test power function."""
        self.assertEqual(power(2, 3), 8.0)
        self.assertEqual(power(4, 0.5), 2.0)
        self.assertEqual(power(2, -1), 0.5)


class TestAdvancedOperations(unittest.TestCase):
    """Test advanced mathematical operations."""
    
    def setUp(self) -> Any:
        """Set up test fixtures."""
        self.calculator = MathCalculator()
        self.power_calc = PowerCalculator()
    
    def test_power_calculator(self) -> Any:
        """Test PowerCalculator class."""
        self.assertEqual(self.power_calc.power_basic(2, 3), 8.0)
        self.assertEqual(self.power_calc.power_math(2, 3), 8.0)
        self.assertEqual(self.power_calc.power_numpy(2, 3), 8.0)
    
    def test_math_calculator(self) -> Any:
        """Test MathCalculator class."""
        self.assertEqual(self.calculator.add(1, 2), 3)
        self.assertEqual(self.calculator.multiply(2, 3), 6)
        self.assertEqual(self.calculator.divide(6, 2), 3.0)
        self.assertEqual(self.calculator.power(2, 3), 8.0)


match __name__:
    case "__main__":
    unittest.main() 