from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from .security_testing import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Security Testing Framework Module

Provides security testing and penetration testing capabilities.
"""

    SecurityTestRequest,
    SecurityTestResult,
    PenetrationTestRequest,
    PenetrationTestResult,
    run_security_tests_async,
    run_penetration_test_async
)

__all__ = [
    "SecurityTestRequest",
    "SecurityTestResult",
    "PenetrationTestRequest",
    "PenetrationTestResult",
    "run_security_tests_async",
    "run_penetration_test_async"
] 