"""
Enhanced middleware for performance, security, and monitoring
"""
from typing import Dict, Any, Optional, Callable
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import time
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
import psutil
import json

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)

# Global metrics storage
_request_metrics: Dict[str, Any] = defaultdict(list)
_performance_metrics: Dict[str, Any] = defaultdict(list)
_security_metrics: Dict[str, Any] = defaultdict(list)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring and optimization."""
    
    def __init__(self, app: FastAPI, max_requests: int = 1000):
        super().__init__(app)
        self.max_requests = max_requests
        self.request_times = deque(maxlen=max_requests)
        self.response_sizes = deque(maxlen=max_requests)
        self.error_counts = defaultdict(int)
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with performance monitoring."""
        start_time = time.perf_counter()
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state
        request.state.request_id = request_id
        request.state.start_time = start_time
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate metrics
            process_time = time.perf_counter() - start_time
            response_size = int(response.headers.get("content-length", 0))
            
            # Store metrics
            self.request_times.append(process_time)
            self.response_sizes.append(response_size)
            
            # Add performance headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Performance-Score"] = str(self._calculate_performance_score(process_time))
            
            # Log performance metrics
            if process_time > 1.0:  # Log slow requests
                logger.warning(
                    f"Slow request {request_id}: {request.method} {request.url.path} "
                    f"took {process_time:.3f}s"
                )
            
            return response
            
        except Exception as e:
            # Track errors
            self.error_counts[type(e).__name__] += 1
            process_time = time.perf_counter() - start_time
            
            logger.error(
                f"Request error {request_id}: {request.method} {request.url.path} "
                f"failed after {process_time:.3f}s - {str(e)}"
            )
            
            raise
    
    def _calculate_performance_score(self, process_time: float) -> float:
        """Calculate performance score based on response time."""
        if process_time < 0.1:
            return 100.0
        elif process_time < 0.5:
            return 90.0
        elif process_time < 1.0:
            return 75.0
        elif process_time < 2.0:
            return 50.0
        else:
            return 25.0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        if not self.request_times:
            return {"error": "No requests processed yet"}
        
        return {
            "total_requests": len(self.request_times),
            "avg_response_time": sum(self.request_times) / len(self.request_times),
            "min_response_time": min(self.request_times),
            "max_response_time": max(self.request_times),
            "avg_response_size": sum(self.response_sizes) / len(self.response_sizes),
            "error_counts": dict(self.error_counts),
            "performance_score": self._calculate_performance_score(
                sum(self.request_times) / len(self.request_times)
            )
        }


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security monitoring and protection."""
    
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.suspicious_ips = defaultdict(int)
        self.rate_limits = defaultdict(list)
        self.blocked_ips = set()
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with security checks."""
        client_ip = request.client.host if request.client else "unknown"
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            return JSONResponse(
                status_code=403,
                content={"error": "IP blocked due to suspicious activity"}
            )
        
        # Rate limiting
        if not self._check_rate_limit(client_ip):
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )
        
        # Security headers
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Monitor suspicious activity
        self._monitor_suspicious_activity(request, client_ip)
        
        return response
    
    def _check_rate_limit(self, client_ip: str, max_requests: int = 100, window_minutes: int = 1) -> bool:
        """Check rate limit for client IP."""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Clean old requests
        self.rate_limits[client_ip] = [
            req_time for req_time in self.rate_limits[client_ip]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.rate_limits[client_ip]) >= max_requests:
            return False
        
        # Add current request
        self.rate_limits[client_ip].append(now)
        return True
    
    def _monitor_suspicious_activity(self, request: Request, client_ip: str) -> None:
        """Monitor for suspicious activity."""
        # Check for suspicious patterns
        if self._is_suspicious_request(request):
            self.suspicious_ips[client_ip] += 1
            
            # Block IP if too many suspicious requests
            if self.suspicious_ips[client_ip] > 10:
                self.blocked_ips.add(client_ip)
                logger.warning(f"Blocked suspicious IP: {client_ip}")
    
    def _is_suspicious_request(self, request: Request) -> bool:
        """Check if request is suspicious."""
        # Check for common attack patterns
        suspicious_patterns = [
            "script", "javascript", "eval", "exec", "union", "select",
            "drop", "delete", "insert", "update", "admin", "root"
        ]
        
        path = str(request.url.path).lower()
        query = str(request.url.query).lower()
        
        for pattern in suspicious_patterns:
            if pattern in path or pattern in query:
                return True
        
        return False
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics."""
        return {
            "suspicious_ips": dict(self.suspicious_ips),
            "blocked_ips": list(self.blocked_ips),
            "rate_limits": {
                ip: len(requests) for ip, requests in self.rate_limits.items()
            }
        }


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive system monitoring."""
    
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.system_metrics = deque(maxlen=1000)
        self.endpoint_metrics = defaultdict(lambda: {
            "count": 0,
            "total_time": 0.0,
            "errors": 0,
            "last_accessed": None
        })
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with comprehensive monitoring."""
        endpoint = f"{request.method} {request.url.path}"
        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
            
            # Calculate metrics
            process_time = time.perf_counter() - start_time
            
            # Update endpoint metrics
            self.endpoint_metrics[endpoint]["count"] += 1
            self.endpoint_metrics[endpoint]["total_time"] += process_time
            self.endpoint_metrics[endpoint]["last_accessed"] = datetime.utcnow()
            
            # Add monitoring headers
            response.headers["X-Endpoint-Metrics"] = json.dumps({
                "count": self.endpoint_metrics[endpoint]["count"],
                "avg_time": self.endpoint_metrics[endpoint]["total_time"] / self.endpoint_metrics[endpoint]["count"]
            })
            
            return response
            
        except Exception as e:
            # Track errors
            self.endpoint_metrics[endpoint]["errors"] += 1
            
            logger.error(f"Endpoint error: {endpoint} - {str(e)}")
            raise
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics."""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "endpoint_metrics": dict(self.endpoint_metrics)
            }
            
            self.system_metrics.append(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {"error": str(e)}
    
    def get_monitoring_metrics(self) -> Dict[str, Any]:
        """Get comprehensive monitoring metrics."""
        return {
            "system_metrics": list(self.system_metrics),
            "endpoint_metrics": dict(self.endpoint_metrics),
            "total_endpoints": len(self.endpoint_metrics),
            "most_accessed": max(
                self.endpoint_metrics.items(),
                key=lambda x: x[1]["count"]
            ) if self.endpoint_metrics else None
        }


def setup_performance_middleware(app: FastAPI) -> None:
    """Setup performance monitoring middleware."""
    app.add_middleware(PerformanceMiddleware)


def setup_security_middleware(app: FastAPI) -> None:
    """Setup security monitoring middleware."""
    app.add_middleware(SecurityMiddleware)


def setup_monitoring_middleware(app: FastAPI) -> None:
    """Setup comprehensive monitoring middleware."""
    app.add_middleware(MonitoringMiddleware)


# Global middleware instances for metrics access
_performance_middleware: Optional[PerformanceMiddleware] = None
_security_middleware: Optional[SecurityMiddleware] = None
_monitoring_middleware: Optional[MonitoringMiddleware] = None


def get_performance_metrics() -> Dict[str, Any]:
    """Get performance metrics from middleware."""
    if _performance_middleware:
        return _performance_middleware.get_metrics()
    return {"error": "Performance middleware not initialized"}


def get_security_metrics() -> Dict[str, Any]:
    """Get security metrics from middleware."""
    if _security_middleware:
        return _security_middleware.get_security_metrics()
    return {"error": "Security middleware not initialized"}


def get_monitoring_metrics() -> Dict[str, Any]:
    """Get monitoring metrics from middleware."""
    if _monitoring_middleware:
        return _monitoring_middleware.get_monitoring_metrics()
    return {"error": "Monitoring middleware not initialized"}


async def collect_system_metrics() -> Dict[str, Any]:
    """Collect current system metrics."""
    if _monitoring_middleware:
        return _monitoring_middleware.collect_system_metrics()
    return {"error": "Monitoring middleware not initialized"}