import time
import logging
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable

class CentralizedMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logging.getLogger("centralized.middleware")

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            self.logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
            # Optionally, add metrics to response headers
            response.headers["X-Process-Time"] = str(process_time)
            return response
        except Exception as exc:
            process_time = time.time() - start_time
            self.logger.error(f"Exception: {exc} - {request.method} {request.url.path} - {process_time:.3f}s")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "details": str(exc),
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                },
            ) 