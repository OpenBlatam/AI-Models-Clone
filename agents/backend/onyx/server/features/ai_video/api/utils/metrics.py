"""
Metrics Utilities - Performance tracking
"""

import time
from functools import wraps
from typing import Dict, Any
import logging


logger = logging.getLogger(__name__)


async def record_metric(name: str, value: float, tags: Dict[str, Any] = None) -> None:
    """Record a metric value."""
    tags = tags or {}
    logger.info(f"Metric: {name}={value}, tags={tags}")


def track_processing_time(operation_name: str):
    """Decorator to track processing time."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                await record_metric(f"{operation_name}_duration", duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                await record_metric(f"{operation_name}_error", duration)
                raise
        return wrapper
    return decorator 