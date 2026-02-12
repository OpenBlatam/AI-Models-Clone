"""
Production Request Queue for PiMoE System

Thread-pool based request queue with submit/process lifecycle.
Ensures thread-safe tracking of active/completed/failed request counts.
"""

from __future__ import annotations

import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Optional

from .config import ProductionConfig
from .logger import ProductionLogger


class ProductionRequestQueue:
    """Production request queue for handling concurrent requests.

    Manages a bounded queue of incoming requests and dispatches them
    to a thread pool for execution. Tracks detailed queue statistics.
    """

    def __init__(
        self,
        config: ProductionConfig,
        logger: ProductionLogger,
    ) -> None:
        self.config = config
        self.logger = logger

        # Thread-safe queue for incoming requests
        self._request_queue: queue.Queue = queue.Queue(
            maxsize=config.max_concurrent_requests
        )

        # Thread pool for processing requests
        self._processing_pool = ThreadPoolExecutor(
            max_workers=config.max_concurrent_requests,
            thread_name_prefix="pimoe-worker",
        )

        # Counters (protected by lock)
        self._lock = threading.Lock()
        self._active_requests: int = 0
        self._completed_requests: int = 0
        self._failed_requests: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def submit_request(
        self,
        request_data: Dict[str, Any],
        callback: Callable[[Dict[str, Any]], None],
    ) -> str:
        """Submit a request for processing.

        Args:
            request_data: The payload to process.
            callback: Function to call with the result payload.

        Returns:
            The generated request_id.

        Raises:
            RuntimeError: If the queue is full (backpressure).
        """
        request_id = f"req_{int(time.time() * 1000)}"

        try:
            self._request_queue.put(
                {
                    "request_id": request_id,
                    "data": request_data,
                    "callback": callback,
                    "timestamp": time.time(),
                },
                timeout=1.0,
            )
            self.logger.log_info(f"Request submitted: {request_id}")
            return request_id

        except queue.Full:
            self.logger.log_error(
                f"Request queue full, rejecting request: {request_id}",
            )
            raise RuntimeError("Request queue is full")

    def process_requests(self) -> None:
        """Process requests from the queue (blocking consumer loop).

        Continually pulls items from the queue and submits them to the
        thread pool. This method blocks until the process is interrupted.
        """
        while True:
            try:
                # Block briefly to allow interruption
                request = self._request_queue.get(timeout=1.0)
                self._processing_pool.submit(self._process_single_request, request)
            except queue.Empty:
                continue
            except Exception as exc:
                self.logger.log_error("Error in request processing loop", exc)
                time.sleep(0.1)

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics (thread-safe snapshot)."""
        with self._lock:
            active = self._active_requests
            completed = self._completed_requests
            failed = self._failed_requests

        total = completed + failed
        return {
            "queue_size": self._request_queue.qsize(),
            "active_requests": active,
            "completed_requests": completed,
            "failed_requests": failed,
            "success_rate": completed / max(total, 1),
        }

    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the thread pool."""
        self._processing_pool.shutdown(wait=wait)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _process_single_request(self, request: Dict[str, Any]) -> None:
        """Process a single request item."""
        request_id = request["request_id"]
        start_time = time.time()

        with self._lock:
            self._active_requests += 1

        try:
            # Execute the callback (the actual work)
            request["callback"](request["data"])

            processing_time = time.time() - start_time
            with self._lock:
                self._completed_requests += 1

            self.logger.log_info(
                f"Request completed: {request_id}",
                processing_time=processing_time,
                active_requests=self._active_requests,
            )

        except Exception as exc:
            processing_time = time.time() - start_time
            with self._lock:
                self._failed_requests += 1

            self.logger.log_error(
                f"Request failed: {request_id}",
                exc,
                processing_time=processing_time,
                active_requests=self._active_requests,
            )

        finally:
            with self._lock:
                self._active_requests -= 1
