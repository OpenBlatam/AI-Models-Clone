"""
Production Logger for PiMoE System

Structured logging with separate channels for application, metrics, and errors.
Handlers are deduplicated so repeated ``ProductionLogger`` instantiation
never stacks duplicate handlers on the same ``logging.Logger``.
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from .config import ProductionConfig


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

_LOG_DIR = Path(os.environ.get("PIMOE_LOG_DIR", "."))


def _ensure_log_dir() -> None:
    """Create the log directory if it does not exist."""
    _LOG_DIR.mkdir(parents=True, exist_ok=True)


def _safe_add_handler(logger: logging.Logger, handler: logging.Handler) -> None:
    """Add *handler* only if the logger does not already carry one of the
    same type pointing at the same target (prevents duplicate output when
    the module is re-imported or a second ``ProductionLogger`` is created).
    """
    for existing in logger.handlers:
        if type(existing) is type(handler):
            if isinstance(handler, logging.FileHandler):
                # Compare resolved paths
                if (
                    getattr(existing, "baseFilename", None)
                    == getattr(handler, "baseFilename", None)
                ):
                    return
            elif isinstance(handler, logging.StreamHandler):
                if existing.stream == handler.stream:  # type: ignore[attr-defined]
                    return
    logger.addHandler(handler)


# ------------------------------------------------------------------
# Public class
# ------------------------------------------------------------------


class ProductionLogger:
    """Production-ready logging system.

    Creates three independent ``logging.Logger`` instances:

    * **application** — general operational messages.
    * **metrics** — one JSON-object-per-line metrics file.
    * **errors** — errors with source-location context.
    """

    def __init__(self, config: ProductionConfig) -> None:
        self.config = config
        _ensure_log_dir()
        self.logger = self._setup_logger()
        self.metrics_logger = self._setup_metrics_logger()
        self.error_logger = self._setup_error_logger()

    # ------------------------------------------------------------------
    # Logger setup
    # ------------------------------------------------------------------

    def _setup_logger(self) -> logging.Logger:
        """Setup main application logger."""
        logger = logging.getLogger("pimoe_production")
        logger.setLevel(getattr(logging, self.config.log_level.value.upper()))

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        file_handler = logging.FileHandler(
            str(_LOG_DIR / "pimoe_production.log"),
        )
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        _safe_add_handler(logger, console_handler)
        _safe_add_handler(logger, file_handler)

        return logger

    def _setup_metrics_logger(self) -> logging.Logger:
        """Setup metrics logger (JSON lines)."""
        logger = logging.getLogger("pimoe_metrics")
        logger.setLevel(logging.INFO)

        metrics_handler = logging.FileHandler(
            str(_LOG_DIR / "pimoe_metrics.log"),
        )
        metrics_handler.setLevel(logging.INFO)
        metrics_handler.setFormatter(logging.Formatter("%(message)s"))

        _safe_add_handler(logger, metrics_handler)
        logger.propagate = False

        return logger

    def _setup_error_logger(self) -> logging.Logger:
        """Setup error logger with source-location context."""
        logger = logging.getLogger("pimoe_errors")
        logger.setLevel(logging.ERROR)

        error_handler = logging.FileHandler(
            str(_LOG_DIR / "pimoe_errors.log"),
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - "
                "%(funcName)s:%(lineno)d - %(message)s",
            ),
        )

        _safe_add_handler(logger, error_handler)
        logger.propagate = False

        return logger

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log_info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        extra = f" | {kwargs}" if kwargs else ""
        self.logger.info(f"{message}{extra}")

    def log_warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        extra = f" | {kwargs}" if kwargs else ""
        self.logger.warning(f"{message}{extra}")

    def log_error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        **kwargs: Any,
    ) -> None:
        """Log error message."""
        extra = f" | {kwargs}" if kwargs else ""
        if exception:
            self.error_logger.error(
                f"{message}{extra}",
                exc_info=exception,
            )
        else:
            self.error_logger.error(f"{message}{extra}")

    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log metrics as a single JSON line."""
        payload = {
            **metrics,
            "timestamp": time.time(),
            "deployment_id": self.config.deployment_id,
        }
        self.metrics_logger.info(json.dumps(payload, default=str))
