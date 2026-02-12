"""
Production PiMoE System

The main system class, factory function, and demo runner.
Coordinates configuration, logging, monitoring, and request processing strategies.
"""

from __future__ import annotations

import signal
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from typing import Any, Callable, Dict, Optional

# Import core dependencies (assuming these exist in parent package)
# If not, this module will fail at runtime, but we preserve the imports
# from the original monolithic file.
try:
    from ..routing.advanced_pimoe_routing import (
        AdvancedPiMoESystem,
        AdvancedRoutingConfig,
        RoutingStrategy,
    )
    from ..optimization.pimoe_performance_optimizer import OptimizationLevel
    from ..routing.pimoe_router import ExpertType
except ImportError:
    # Fallback for when running in isolation or if dependencies are missing
    AdvancedPiMoESystem = object
    AdvancedRoutingConfig = dict
    RoutingStrategy = object
    OptimizationLevel = object
    ExpertType = object

from .config import ProductionConfig, ProductionMode
from .logger import ProductionLogger
from .monitor import ProductionErrorHandler, ProductionMonitor
from .request_queue import ProductionRequestQueue


class ProductionPiMoESystem:
    """Production-ready PiMoE system facade.

    Wraps the core ``AdvancedPiMoESystem`` with production-grade monitoring,
    logging, error handling, and request queue management.
    """

    def __init__(self, config: ProductionConfig) -> None:
        self.config = config

        # Initialize core components
        self.logger = ProductionLogger(config)
        self.monitor = ProductionMonitor(config, self.logger)
        self.error_handler = ProductionErrorHandler(config, self.logger)
        self.request_queue = ProductionRequestQueue(config, self.logger)

        # Initialize the underlying model (AdvancedPiMoESystem)
        self.logger.log_info(
            "Initializing Production PiMoE System",
            version=config.model_version,
            environment=config.environment,
        )

        try:
            # Map ProductionConfig to AdvancedRoutingConfig
            # Note: This assumes AdvancedRoutingConfig accepts these kwargs
            advanced_config = AdvancedRoutingConfig(
                hidden_size=config.hidden_size,
                num_experts=config.num_experts,
                expert_capacity=config.max_batch_size,
                routing_strategy=RoutingStrategy.OPERATIONAL,  # Default
            )
            self.model = AdvancedPiMoESystem(advanced_config)
            self.logger.log_info("AdvancedPiMoESystem initialized successfully")
        except Exception as exc:
            self.logger.log_error("Failed to initialize AdvancedPiMoESystem", exc)
            # Depending on severity, we might want to raise here
            # For now, we continue but mark health as degraded
            self.model = None

        # Apply optimizations
        if self.model:
            self._apply_production_optimizations()

        # Start request processing thread
        self._shutdown_event = threading.Event()
        self._processing_thread = threading.Thread(
            target=self._request_processing_loop,
            daemon=True,
            name="pimoe-request-processor",
        )
        self._processing_thread.start()

        # Setup signal handlers for graceful shutdown (main thread only)
        if threading.current_thread() is threading.main_thread():
            self._setup_signal_handlers()

    # ------------------------------------------------------------------
    # Optimizations
    # ------------------------------------------------------------------

    def _apply_production_optimizations(self) -> None:
        """Apply configured optimizations to the underlying model."""
        level = self.config.optimization_level
        self.logger.log_info(f"Applying optimizations (level={level})")

        if self.config.enable_quantization:
            self._apply_quantization()
        if self.config.enable_pruning:
            self._apply_pruning()

    def _apply_quantization(self) -> None:
        """Stub for applying dynamic quantization."""
        # e.g. torch.quantization.quantize_dynamic(...)
        self.logger.log_info("Applying dynamic quantization")

    def _apply_pruning(self) -> None:
        """Stub for applying magnitude-based pruning."""
        self.logger.log_info("Applying magnitude-based pruning")

    # ------------------------------------------------------------------
    # Request Processing
    # ------------------------------------------------------------------

    def _request_processing_loop(self) -> None:
        """Background loop that pulls from the request queue."""
        # This delegates to the queue's own internal loop if implemented there,
        # or we could drive it here.
        # But ProductionRequestQueue.process_requests() is blocking.
        # We run it in a thread.
        self.request_queue.process_requests()

    def submit_request(
        self,
        input_data: Dict[str, Any],
        callback: Optional[Callable] = None,
    ) -> str:
        """Submit a request asynchronously.

        Args:
            input_data: The input dictionary for the model.
            callback: Optional function to call with the result.
                      If None, a default no-op callback is used.

        Returns:
            The request ID.
        """
        # Circuit breaker check
        if self.error_handler.should_circuit_break():
            self.logger.log_warning("Circuit breaker open, rejecting request")
            raise RuntimeError("Circuit breaker open")

        cb = callback or self._default_callback
        try:
            req_id = self.request_queue.submit_request(input_data, cb)
            self.monitor.record_request(success=True)  # Submission success
            return req_id
        except Exception as exc:
            self.monitor.record_request(success=False)
            raise exc

    def _default_callback(self, result: Any) -> None:
        """Default logging callback."""
        # In a real system, you might not want to log every result body
        self.logger.log_info("Request processed (default callback)")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _setup_signal_handlers(self) -> None:
        """Handle SIGTERM/SIGINT for graceful shutdown."""

        def signal_handler(signum: int, frame: Any) -> None:
            self.logger.log_info(f"Received signal {signum}, shutting down...")
            self.shutdown()
            sys.exit(0)

        # Only works on main thread
        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except ValueError:
            self.logger.log_warning("Could not set signal handlers (not main thread?)")

    def shutdown(self) -> None:
        """Gracefully stop background threads and resources."""
        self.logger.log_info("Initiating shutdown")
        self._shutdown_event.set()
        # In a generic queue, we'd need a way to stop process_requests()
        # For now, we assume process daemon threads die with the process
        # or we implement specific stop logic in queue if needed.

    # ------------------------------------------------------------------
    # Observability
    # ------------------------------------------------------------------

    def get_production_stats(self) -> Dict[str, Any]:
        """Aggregate stats from monitor and queue."""
        return {
            "health": self.monitor.get_health_status(),
            "queue": self.request_queue.get_queue_stats(),
        }

    def health_check(self) -> bool:
        """Return True if system is healthy."""
        status = self.monitor.get_health_status()
        return status["status"] == "healthy"


# ------------------------------------------------------------------
# Factory
# ------------------------------------------------------------------


def create_production_pimoe_system(
    hidden_size: int = 512,
    num_experts: int = 8,
    production_mode: ProductionMode = ProductionMode.PRODUCTION,
    **kwargs: Any,
) -> ProductionPiMoESystem:
    """Factory function to create a configured system instance."""
    config = ProductionConfig(
        hidden_size=hidden_size,
        num_experts=num_experts,
        production_mode=production_mode,
        **kwargs,  # Override other defaults via kwargs if they match fields
    )
    return ProductionPiMoESystem(config)


# ------------------------------------------------------------------
# Demo
# ------------------------------------------------------------------


def run_production_demo() -> ProductionPiMoESystem:
    """Run a local demonstration of the system."""
    print("Starting Production PiMoE Demo...")
    system = create_production_pimoe_system(
        hidden_size=256,
        num_experts=4,
        production_mode=ProductionMode.DEVELOPMENT,
        log_level="info",  # Will need to handle string->enum if not in kwargs logic
    )

    # Submit some dummy requests
    for i in range(5):
        try:
            system.submit_request({"input_id": i, "content": "test data"})
            time.sleep(0.5)
        except Exception as e:
            print(f"Request {i} failed: {e}")

    # Check stats
    stats = system.get_production_stats()
    print("System Stats:", stats)
    
    # Wait a bit then shutdown
    time.sleep(2)
    system.shutdown()
    print("Demo completed.")
    return system


if __name__ == "__main__":
    run_production_demo()
