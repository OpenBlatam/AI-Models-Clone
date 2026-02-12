"""
Production Configuration for PiMoE System

Enums and dataclass defining all production deployment settings.
Values are populated from environment variables with sensible defaults
so the same image works across dev / staging / prod without code changes.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict

from ..optimization.pimoe_performance_optimizer import OptimizationLevel


# ------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------


class ProductionMode(Enum):
    """Production deployment modes."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    HIGH_PERFORMANCE = "high_performance"
    COST_OPTIMIZED = "cost_optimized"


class LogLevel(Enum):
    """Logging levels for production."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _env(key: str, default: str) -> str:
    """Read an environment variable with a fallback default."""
    return os.environ.get(key, default)


def _env_int(key: str, default: int) -> int:
    """Read an integer-valued environment variable."""
    return int(os.environ.get(key, str(default)))


def _env_float(key: str, default: float) -> float:
    """Read a float-valued environment variable."""
    return float(os.environ.get(key, str(default)))


def _env_bool(key: str, default: bool) -> bool:
    """Read a boolean environment variable (accepts '1', 'true', 'yes')."""
    raw = os.environ.get(key, str(default)).lower()
    return raw in ("1", "true", "yes")


# ------------------------------------------------------------------
# Dataclass
# ------------------------------------------------------------------


@dataclass
class ProductionConfig:
    """Production configuration for PiMoE system.

    Every field reads its initial value from the corresponding
    ``PIMOE_*`` environment variable so that operators can override
    settings at deploy-time without touching code.
    """

    # System configuration
    hidden_size: int = field(
        default_factory=lambda: _env_int("PIMOE_HIDDEN_SIZE", 512),
    )
    num_experts: int = field(
        default_factory=lambda: _env_int("PIMOE_NUM_EXPERTS", 8),
    )
    max_batch_size: int = field(
        default_factory=lambda: _env_int("PIMOE_MAX_BATCH_SIZE", 32),
    )
    max_sequence_length: int = field(
        default_factory=lambda: _env_int("PIMOE_MAX_SEQUENCE_LENGTH", 2048),
    )

    # Production settings
    production_mode: ProductionMode = field(
        default_factory=lambda: ProductionMode(
            _env("PIMOE_PRODUCTION_MODE", "production")
        ),
    )
    log_level: LogLevel = field(
        default_factory=lambda: LogLevel(_env("PIMOE_LOG_LEVEL", "info")),
    )
    enable_monitoring: bool = field(
        default_factory=lambda: _env_bool("PIMOE_ENABLE_MONITORING", True),
    )
    enable_metrics: bool = field(
        default_factory=lambda: _env_bool("PIMOE_ENABLE_METRICS", True),
    )
    enable_health_checks: bool = field(
        default_factory=lambda: _env_bool("PIMOE_ENABLE_HEALTH_CHECKS", True),
    )

    # Performance settings
    optimization_level: OptimizationLevel = field(
        default=OptimizationLevel.EXTREME,
    )
    enable_quantization: bool = field(
        default_factory=lambda: _env_bool("PIMOE_ENABLE_QUANTIZATION", True),
    )
    enable_pruning: bool = field(
        default_factory=lambda: _env_bool("PIMOE_ENABLE_PRUNING", True),
    )
    enable_distillation: bool = field(
        default_factory=lambda: _env_bool("PIMOE_ENABLE_DISTILLATION", False),
    )
    mixed_precision: bool = field(
        default_factory=lambda: _env_bool("PIMOE_MIXED_PRECISION", True),
    )

    # Scalability settings
    max_concurrent_requests: int = field(
        default_factory=lambda: _env_int("PIMOE_MAX_CONCURRENT_REQUESTS", 100),
    )
    request_timeout: float = field(
        default_factory=lambda: _env_float("PIMOE_REQUEST_TIMEOUT", 30.0),
    )
    memory_threshold_mb: float = field(
        default_factory=lambda: _env_float("PIMOE_MEMORY_THRESHOLD_MB", 8000.0),
    )
    cpu_threshold_percent: float = field(
        default_factory=lambda: _env_float("PIMOE_CPU_THRESHOLD_PERCENT", 80.0),
    )

    # Monitoring settings
    metrics_interval: float = field(
        default_factory=lambda: _env_float("PIMOE_METRICS_INTERVAL", 1.0),
    )
    health_check_interval: float = field(
        default_factory=lambda: _env_float("PIMOE_HEALTH_CHECK_INTERVAL", 5.0),
    )
    log_interval: float = field(
        default_factory=lambda: _env_float("PIMOE_LOG_INTERVAL", 10.0),
    )

    # Error handling
    max_retries: int = field(
        default_factory=lambda: _env_int("PIMOE_MAX_RETRIES", 3),
    )
    retry_delay: float = field(
        default_factory=lambda: _env_float("PIMOE_RETRY_DELAY", 1.0),
    )
    circuit_breaker_threshold: int = field(
        default_factory=lambda: _env_int("PIMOE_CIRCUIT_BREAKER_THRESHOLD", 10),
    )

    # Deployment settings
    model_version: str = field(
        default_factory=lambda: _env("PIMOE_MODEL_VERSION", "1.0.0"),
    )
    deployment_id: str = field(
        default_factory=lambda: _env("PIMOE_DEPLOYMENT_ID", "pimoe-prod-001"),
    )
    environment: str = field(
        default_factory=lambda: _env("PIMOE_ENVIRONMENT", "production"),
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:
        """Validate field values after initialisation."""
        errors: list[str] = []

        if self.hidden_size <= 0:
            errors.append(f"hidden_size must be > 0, got {self.hidden_size}")
        if self.num_experts <= 0:
            errors.append(f"num_experts must be > 0, got {self.num_experts}")
        if self.max_batch_size <= 0:
            errors.append(
                f"max_batch_size must be > 0, got {self.max_batch_size}"
            )
        if self.max_concurrent_requests <= 0:
            errors.append(
                f"max_concurrent_requests must be > 0, got "
                f"{self.max_concurrent_requests}"
            )
        if self.request_timeout <= 0:
            errors.append(
                f"request_timeout must be > 0, got {self.request_timeout}"
            )
        if not 0 < self.cpu_threshold_percent <= 100:
            errors.append(
                f"cpu_threshold_percent must be in (0, 100], got "
                f"{self.cpu_threshold_percent}"
            )

        if errors:
            raise ValueError(
                "Invalid ProductionConfig:\n  - " + "\n  - ".join(errors)
            )

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serialise configuration to a plain dictionary."""
        from dataclasses import asdict

        return asdict(self)
