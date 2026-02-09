#!/usr/bin/env python3
"""
Deployment Retry Logic
Implements retry mechanisms with exponential backoff
"""

import time
import logging
from typing import Callable, Any, Optional, Tuple
from functools import wraps
from enum import Enum


logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """Retry strategies"""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"


class RetryConfig:
    """Configuration for retry logic"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.strategy = strategy


class RetryHandler:
    """Handles retry logic with configurable strategies"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt"""
        if self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.initial_delay * (self.config.backoff_multiplier ** (attempt - 1))
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self.config.initial_delay * attempt
        else:  # FIXED
            delay = self.config.initial_delay
        
        return min(delay, self.config.max_delay)
    
    def retry(
        self,
        func: Callable[[], Tuple[bool, Any]],
        operation_name: str = "operation"
    ) -> Tuple[bool, Any, int]:
        """
        Execute function with retry logic
        
        Returns:
            Tuple of (success: bool, result: Any, attempts: int)
        """
        last_error = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                success, result = func()
                
                if success:
                    if attempt > 1:
                        logger.info(f"{operation_name} succeeded on attempt {attempt}")
                    return True, result, attempt
                else:
                    last_error = result
                    logger.warning(f"{operation_name} failed on attempt {attempt}: {result}")
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"{operation_name} raised exception on attempt {attempt}: {e}")
            
            # Don't wait after last attempt
            if attempt < self.config.max_attempts:
                delay = self.calculate_delay(attempt)
                logger.info(f"Retrying {operation_name} in {delay:.1f}s (attempt {attempt + 1}/{self.config.max_attempts})")
                time.sleep(delay)
        
        logger.error(f"{operation_name} failed after {self.config.max_attempts} attempts")
        return False, last_error, self.config.max_attempts


def retry_on_failure(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
):
    """Decorator for retrying functions on failure"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            config = RetryConfig(
                max_attempts=max_attempts,
                initial_delay=initial_delay,
                strategy=strategy
            )
            handler = RetryHandler(config)
            
            def attempt():
                try:
                    result = func(*args, **kwargs)
                    # Assume function returns success boolean or (success, value) tuple
                    if isinstance(result, tuple) and len(result) == 2:
                        return result
                    else:
                        return (bool(result), result)
                except Exception as e:
                    return (False, str(e))
            
            success, result, attempts = handler.retry(attempt, func.__name__)
            return result if success else None
        
        return wrapper
    return decorator
