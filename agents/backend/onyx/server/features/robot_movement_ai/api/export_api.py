"""
Export API Endpoints
====================

Endpoints para exportación de datos.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
import logging

from ..core.export_utils import get_export_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/export", tags=["export"])


@router.post("/json")
async def export_to_json(
    data: Dict[str, Any],
    filepath: str = Query(..., description="Path to export file")
) -> Dict[str, Any]:
    """Exportar datos a JSON."""
    try:
        manager = get_export_manager()
        exported_path = manager.export_json(data, filepath)
        return {
            "message": "Data exported successfully",
            "filepath": exported_path,
            "format": "json"
        }
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/yaml")
async def export_to_yaml(
    data: Dict[str, Any],
    filepath: str = Query(..., description="Path to export file")
) -> Dict[str, Any]:
    """Exportar datos a YAML."""
    try:
        manager = get_export_manager()
        exported_path = manager.export_yaml(data, filepath)
        return {
            "message": "Data exported successfully",
            "filepath": exported_path,
            "format": "yaml"
        }
    except Exception as e:
        logger.error(f"Error exporting to YAML: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/csv")
async def export_to_csv(
    data: list,
    filepath: str = Query(..., description="Path to export file"),
    fieldnames: Optional[list] = None
) -> Dict[str, Any]:
    """Exportar datos a CSV."""
    try:
        manager = get_export_manager()
        exported_path = manager.export_csv(data, filepath, fieldnames=fieldnames)
        return {
            "message": "Data exported successfully",
            "filepath": exported_path,
            "format": "csv"
        }
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/markdown")
async def export_to_markdown(
    data: Dict[str, Any],
    filepath: str = Query(..., description="Path to export file"),
    title: str = Query("Data Export", description="Document title")
) -> Dict[str, Any]:
    """Exportar datos a Markdown."""
    try:
        manager = get_export_manager()
        exported_path = manager.export_markdown(data, filepath, title=title)
        return {
            "message": "Data exported successfully",
            "filepath": exported_path,
            "format": "markdown"
        }
    except Exception as e:
        logger.error(f"Error exporting to Markdown: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_export_history(
    limit: int = Query(100, ge=1, le=1000)
) -> Dict[str, Any]:
    """Obtener historial de exportaciones."""
    try:
        manager = get_export_manager()
        history = manager.get_export_history(limit=limit)
        return {
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"Error getting export history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))






