"""
Logging utilities for the Blaze AI module.

This module provides a simple logging interface that can be extended
to use the enhanced logging system when available.
"""

from __future__ import annotations

import logging
from typing import Optional


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name
        level: Optional logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if level is not None:
        logger.setLevel(level)
    
    # Add handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Setup basic logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Optional custom format string
        log_file: Optional log file path
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=format_string,
        handlers=[
            logging.StreamHandler(),
            *([logging.FileHandler(log_file)] if log_file else [])
        ]
    )


# Export main functions
__all__ = ["get_logger", "setup_logging"]


