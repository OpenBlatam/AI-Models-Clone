"""
Health API - Health Check and Monitoring Endpoints.

Comprehensive health monitoring with system metrics,
optimizer status, and performance indicators.
"""

import time
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import ORJSONResponse, PlainTextResponse

from prometheus_client import generate_latest

from ..monitoring import (
    comprehensive_health_check,
    track_performance,
    performance_tracker
)
from ..core.app_factory import get_app_state

router = APIRouter()


@router.get("/health", response_class=ORJSONResponse)
@track_performance("health_check", "monitoring")
async def health_check():
    """Comprehensive health check with system status."""
    try:
        app_state = get_app_state()
        health_status = await comprehensive_health_check()
        
        # Check optimizer health
        optimizer_health = {"healthy": False, "message": "Not initialized"}
        if app_state.master_optimizer:
            try:
                metrics = app_state.master_optimizer.get_comprehensive_metrics()
                optimizer_health = {
                    "healthy": True,
                    "available_optimizers": metrics["master"]["available_optimizers"],
                    "successful_initializations": metrics["master"]["successful_initializations"]
                }
            except Exception as e:
                optimizer_health = {"healthy": False, "error": str(e)}
        
        # Overall health assessment
        overall_healthy = (
            all(status.healthy for status in health_status.values()) and
            optimizer_health["healthy"]
        )
        
        return {
            "status": "healthy" if overall_healthy else "degraded",
            "timestamp": health_status["system"].timestamp.isoformat(),
            "version": app_state.config.version if app_state.config else "unknown",
            "environment": app_state.config.environment.value if app_state.config else "unknown",
            "uptime_seconds": time.time() - app_state.startup_time if app_state.initialized else 0,
            "services": {
                name: {
                    "healthy": status.healthy,
                    "message": status.message,
                    "details": status.details
                }
                for name, status in health_status.items()
            },
            "optimizers": optimizer_health
        }
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@router.get("/health/live", response_class=ORJSONResponse)
async def liveness_probe():
    """Lightweight liveness probe for Kubernetes."""
    app_state = get_app_state()
    return {
        "status": "alive",
        "timestamp": time.time(),
        "uptime_seconds": time.time() - app_state.startup_time if app_state.initialized else 0
    }


@router.get("/health/ready", response_class=ORJSONResponse)
async def readiness_probe():
    """Readiness probe for Kubernetes."""
    app_state = get_app_state()
    
    if not app_state.initialized:
        raise HTTPException(status_code=503, detail="Application not ready")
    
    # Quick health checks
    ready = True
    issues = []
    
    if not app_state.master_optimizer:
        ready = False
        issues.append("Optimizer not initialized")
    
    if ready:
        return {
            "status": "ready",
            "timestamp": time.time()
        }
    else:
        raise HTTPException(
            status_code=503, 
            detail={"status": "not_ready", "issues": issues}
        )


@router.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    try:
        return generate_latest()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Metrics unavailable")


@router.get("/metrics/detailed", response_class=ORJSONResponse)
@track_performance("detailed_metrics", "monitoring")
async def detailed_metrics():
    """Comprehensive performance metrics."""
    try:
        app_state = get_app_state()
        
        metrics = {
            "timestamp": time.time(),
            "uptime_seconds": time.time() - app_state.startup_time if app_state.initialized else 0,
            "app_info": {
                "name": app_state.config.app_name if app_state.config else "Onyx",
                "version": app_state.config.version if app_state.config else "unknown",
                "environment": app_state.config.environment.value if app_state.config else "unknown"
            }
        }
        
        # Add optimizer metrics
        if app_state.master_optimizer:
            try:
                metrics["optimizers"] = app_state.master_optimizer.get_comprehensive_metrics()
            except Exception as e:
                metrics["optimizers"] = {"error": str(e)}
        
        # Add performance tracker metrics
        try:
            performance_stats = {}
            for operation in performance_tracker._metrics.keys():
                performance_stats[operation] = performance_tracker.get_stats(operation)
            metrics["performance_tracker"] = performance_stats
        except Exception as e:
            metrics["performance_tracker"] = {"error": str(e)}
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics generation failed: {str(e)}")


@router.get("/status", response_class=ORJSONResponse)
async def application_status():
    """Comprehensive application status."""
    app_state = get_app_state()
    
    if not app_state.config:
        raise HTTPException(status_code=503, detail="Application not configured")
    
    return {
        "application": app_state.config.get_summary(),
        "runtime": {
            "initialized": app_state.initialized,
            "startup_time_seconds": app_state.startup_time,
            "uptime_seconds": time.time() - app_state.startup_time if app_state.initialized else 0
        },
        "optimizers": {
            "available": app_state.master_optimizer is not None,
            "count": len(app_state.master_optimizer.get_comprehensive_metrics()["master"]["available_optimizers"]) if app_state.master_optimizer else 0
        }
    } 