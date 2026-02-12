"""
Production-Ready PiMoE System  (backward-compatibility shim)

This module re-exports everything from the ``production`` subpackage so that
existing ``from .production_pimoe_system import ...`` statements keep working.
"""

# Re-export the full public API
from ..production import (  # noqa: F401
    LogLevel,
    ProductionConfig,
    ProductionErrorHandler,
    ProductionLogger,
    ProductionMode,
    ProductionMonitor,
    ProductionPiMoESystem,
    ProductionRequestQueue,
    create_production_pimoe_system,
)

__all__ = [
    "ProductionMode",
    "LogLevel",
    "ProductionConfig",
    "ProductionLogger",
    "ProductionMonitor",
    "ProductionErrorHandler",
    "ProductionRequestQueue",
    "ProductionPiMoESystem",
    "create_production_pimoe_system",
    "run_production_demo",
]

if __name__ == "__main__":
    system = run_production_demo()
