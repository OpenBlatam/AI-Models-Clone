"""
Metrics API Endpoints
====================

Endpoints para exponer métricas del sistema.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from ..core.metrics import get_metrics_collector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])


@router.get("/")
async def get_all_metrics() -> Dict[str, Any]:
    """Obtener todas las métricas."""
    try:
        collector = get_metrics_collector()
        return collector.get_all_metrics()
    except Exception as e:
        logger.error(f"Error getting metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_metrics_summary() -> Dict[str, Any]:
    """Obtener resumen de métricas."""
    try:
        collector = get_metrics_collector()
        return collector.get_metrics_summary()
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{metric_name}")
async def get_metric(metric_name: str) -> Dict[str, Any]:
    """Obtener métrica específica."""
    try:
        collector = get_metrics_collector()
        metric = collector.get_metric(metric_name)
        
        if metric is None:
            raise HTTPException(status_code=404, detail=f"Metric {metric_name} not found")
        
        return metric.get_statistics()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metric {metric_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{metric_name}")
async def reset_metric(metric_name: str) -> Dict[str, str]:
    """Resetear métrica específica."""
    try:
        collector = get_metrics_collector()
        collector.reset_metric(metric_name)
        return {"message": f"Metric {metric_name} reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting metric {metric_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))






