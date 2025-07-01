"""
Metrics Endpoints
================

Metrics and monitoring API endpoints.
"""

from fastapi import APIRouter, Response
from ...core.interfaces.metrics_interface import IMetricsService


class MetricsEndpoints:
    """Metrics endpoints."""
    
    def __init__(self, metrics_service: IMetricsService):
        self.metrics_service = metrics_service
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup metrics routes."""
        
        @self.router.get("/metrics")
        async def get_prometheus_metrics():
            """Get Prometheus formatted metrics."""
            metrics_data = self.metrics_service.get_prometheus_metrics()
            
            return Response(
                content=metrics_data,
                media_type="text/plain; version=0.0.4; charset=utf-8"
            )
        
        @self.router.get("/metrics/json")
        async def get_json_metrics():
            """Get metrics in JSON format."""
            metrics_data = self.metrics_service.get_metrics_data()
            
            return {
                "timestamp": metrics_data.timestamp.isoformat(),
                "metrics": {
                    "requests": {
                        "total": metrics_data.request_count,
                        "errors": metrics_data.error_count,
                        "error_rate": metrics_data.get_error_rate(),
                        "average_response_time": metrics_data.average_response_time
                    },
                    "cache": {
                        "hit_ratio": metrics_data.cache_hit_ratio
                    },
                    "connections": {
                        "active": metrics_data.active_connections
                    },
                    "circuit_breakers": metrics_data.circuit_breaker_states,
                    "custom": metrics_data.custom_metrics
                }
            }
        
        @self.router.get("/stats")
        async def get_system_stats():
            """Get system statistics."""
            metrics_data = self.metrics_service.get_metrics_data()
            
            return {
                "service": "Enterprise API",
                "version": "2.0.0",
                "architecture": "Clean Architecture",
                "uptime_metrics": {
                    "total_requests": metrics_data.request_count,
                    "error_count": metrics_data.error_count,
                    "success_rate": 1.0 - metrics_data.get_error_rate(),
                    "average_response_time_ms": metrics_data.average_response_time * 1000,
                    "cache_hit_ratio": metrics_data.cache_hit_ratio
                },
                "performance": {
                    "status": "excellent" if metrics_data.get_error_rate() < 0.01 else "good" if metrics_data.get_error_rate() < 0.05 else "needs_attention",
                    "cache_efficiency": "excellent" if metrics_data.cache_hit_ratio > 0.8 else "good" if metrics_data.cache_hit_ratio > 0.5 else "poor"
                }
            } 