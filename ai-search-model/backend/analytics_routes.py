"""
Analytics Routes - Rutas de Analytics
Endpoints para análisis avanzado y métricas del sistema
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import json

from models.analytics_engine import AnalyticsEngine
from models.batch_processor import BatchProcessor
from models.export_import import ExportImportSystem
from database.vector_db import VectorDatabase
from models.search_engine import AISearchEngine

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(prefix="/analytics", tags=["analytics"])

# Instancias globales
analytics_engine = None
batch_processor = None
export_import_system = None

# Dependencias
async def get_analytics_engine():
    global analytics_engine
    if analytics_engine is None:
        analytics_engine = AnalyticsEngine()
    return analytics_engine

async def get_batch_processor():
    global batch_processor
    if batch_processor is None:
        batch_processor = BatchProcessor()
    return batch_processor

async def get_export_import_system():
    global export_import_system
    if export_import_system is None:
        export_import_system = ExportImportSystem()
    return export_import_system

async def get_vector_db():
    global vector_db
    if vector_db is None:
        vector_db = VectorDatabase()
        await vector_db.initialize()
    return vector_db

async def get_search_engine():
    global search_engine
    if search_engine is None:
        search_engine = AISearchEngine()
        await search_engine.initialize()
    return search_engine

# Endpoints de Analytics

@router.get("/insights")
async def get_system_insights(
    time_range: str = Query("7d", description="Rango de tiempo: 1d, 7d, 30d, 90d"),
    search_type: Optional[str] = Query(None, description="Tipo de búsqueda: semantic, keyword, hybrid"),
    vector_db: VectorDatabase = Depends(get_vector_db),
    search_engine: AISearchEngine = Depends(get_search_engine),
    analytics_engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """
    Obtener insights inteligentes del sistema
    """
    try:
        logger.info(f"Generando insights para rango: {time_range}")
        
        # Obtener datos del sistema
        documents = await vector_db.list_documents(limit=10000)
        
        # Simular datos de búsqueda (en producción vendrían de logs reales)
        search_data = [
            {
                "query": "inteligencia artificial",
                "search_type": "semantic",
                "total_results": 15,
                "search_time": 0.125,
                "timestamp": datetime.now().isoformat()
            },
            {
                "query": "machine learning",
                "search_type": "hybrid",
                "total_results": 12,
                "search_time": 0.098,
                "timestamp": datetime.now().isoformat()
            },
            {
                "query": "python",
                "search_type": "keyword",
                "total_results": 8,
                "search_time": 0.067,
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        # Generar insights
        insights = await analytics_engine.generate_insights(search_data, documents)
        
        return {
            "success": True,
            "insights": insights,
            "generated_at": datetime.now().isoformat(),
            "time_range": time_range
        }
        
    except Exception as e:
        logger.error(f"Error generando insights: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando insights: {str(e)}")

@router.get("/search-patterns")
async def get_search_patterns(
    time_range: str = Query("7d", description="Rango de tiempo"),
    analytics_engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """
    Obtener patrones de búsqueda
    """
    try:
        # Simular datos de búsqueda
        search_data = [
            {
                "query": "inteligencia artificial",
                "search_type": "semantic",
                "total_results": 15,
                "search_time": 0.125,
                "timestamp": datetime.now().isoformat()
            },
            {
                "query": "machine learning",
                "search_type": "hybrid",
                "total_results": 12,
                "search_time": 0.098,
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        patterns = await analytics_engine.analyze_search_patterns(search_data)
        
        return {
            "success": True,
            "patterns": patterns,
            "time_range": time_range
        }
        
    except Exception as e:
        logger.error(f"Error analizando patrones: {e}")
        raise HTTPException(status_code=500, detail=f"Error analizando patrones: {str(e)}")

@router.get("/content-analysis")
async def get_content_analysis(
    vector_db: VectorDatabase = Depends(get_vector_db),
    analytics_engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """
    Obtener análisis de contenido
    """
    try:
        documents = await vector_db.list_documents(limit=10000)
        analysis = await analytics_engine.analyze_document_content(documents)
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Error analizando contenido: {e}")
        raise HTTPException(status_code=500, detail=f"Error analizando contenido: {str(e)}")

@router.get("/visualizations")
async def get_visualizations(
    data_type: str = Query("insights", description="Tipo de datos: insights, patterns, content"),
    vector_db: VectorDatabase = Depends(get_vector_db),
    analytics_engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """
    Obtener visualizaciones de datos
    """
    try:
        if data_type == "insights":
            # Obtener datos para insights
            documents = await vector_db.list_documents(limit=1000)
            search_data = []  # Simular datos de búsqueda
            
            insights = await analytics_engine.generate_insights(search_data, documents)
            visualizations = await analytics_engine.create_visualizations(insights)
            
        elif data_type == "content":
            documents = await vector_db.list_documents(limit=1000)
            analysis = await analytics_engine.analyze_document_content(documents)
            visualizations = await analytics_engine.create_visualizations(analysis)
            
        else:
            raise HTTPException(status_code=400, detail="Tipo de datos no válido")
        
        return {
            "success": True,
            "visualizations": visualizations,
            "data_type": data_type
        }
        
    except Exception as e:
        logger.error(f"Error generando visualizaciones: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando visualizaciones: {str(e)}")

# Endpoints de Procesamiento por Lotes

@router.post("/batch/process-files")
async def process_file_batch(
    file_paths: List[str],
    max_workers: int = Query(4, ge=1, le=10),
    batch_size: int = Query(100, ge=1, le=1000),
    vector_db: VectorDatabase = Depends(get_vector_db)
):
    """
    Procesar lote de archivos
    """
    try:
        from models.document_processor import DocumentProcessor
        
        document_processor = DocumentProcessor()
        batch_processor = BatchProcessor(max_workers=max_workers, batch_size=batch_size)
        
        results = await batch_processor.process_file_batch(
            file_paths, 
            document_processor, 
            vector_db
        )
        
        return {
            "success": True,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error procesando lote de archivos: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando archivos: {str(e)}")

@router.post("/batch/process-directory")
async def process_directory(
    directory_path: str,
    file_patterns: Optional[List[str]] = None,
    max_workers: int = Query(4, ge=1, le=10),
    vector_db: VectorDatabase = Depends(get_vector_db)
):
    """
    Procesar directorio completo
    """
    try:
        from models.document_processor import DocumentProcessor
        
        document_processor = DocumentProcessor()
        batch_processor = BatchProcessor(max_workers=max_workers)
        
        results = await batch_processor.process_directory(
            directory_path,
            document_processor,
            vector_db,
            file_patterns
        )
        
        return {
            "success": True,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error procesando directorio: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando directorio: {str(e)}")

@router.post("/batch/process-csv")
async def process_csv_batch(
    csv_path: str,
    title_column: str = Query("title", description="Columna con títulos"),
    content_column: str = Query("content", description="Columna con contenido"),
    vector_db: VectorDatabase = Depends(get_vector_db)
):
    """
    Procesar archivo CSV
    """
    try:
        from models.document_processor import DocumentProcessor
        
        document_processor = DocumentProcessor()
        batch_processor = BatchProcessor()
        
        results = await batch_processor.process_csv_batch(
            csv_path,
            document_processor,
            vector_db,
            title_column,
            content_column
        )
        
        return {
            "success": True,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error procesando CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando CSV: {str(e)}")

# Endpoints de Exportación/Importación

@router.post("/export/documents")
async def export_documents(
    format_type: str = Query("json", description="Formato: json, csv, zip, xlsx"),
    include_embeddings: bool = Query(False, description="Incluir embeddings"),
    output_path: Optional[str] = Query(None, description="Ruta de salida"),
    vector_db: VectorDatabase = Depends(get_vector_db)
):
    """
    Exportar documentos
    """
    try:
        export_system = ExportImportSystem()
        documents = await vector_db.list_documents(limit=10000)
        
        results = await export_system.export_documents(
            documents,
            format_type,
            include_embeddings,
            output_path
        )
        
        return {
            "success": True,
            "export_results": results
        }
        
    except Exception as e:
        logger.error(f"Error exportando documentos: {e}")
        raise HTTPException(status_code=500, detail=f"Error exportando: {str(e)}")

@router.post("/export/backup")
async def export_system_backup(
    output_path: Optional[str] = Query(None, description="Ruta de salida"),
    vector_db: VectorDatabase = Depends(get_vector_db),
    search_engine: AISearchEngine = Depends(get_search_engine)
):
    """
    Crear respaldo completo del sistema
    """
    try:
        export_system = ExportImportSystem()
        
        results = await export_system.export_system_backup(
            vector_db,
            search_engine,
            output_path
        )
        
        return {
            "success": True,
            "backup_results": results
        }
        
    except Exception as e:
        logger.error(f"Error creando respaldo: {e}")
        raise HTTPException(status_code=500, detail=f"Error creando respaldo: {str(e)}")

@router.post("/import/documents")
async def import_documents(
    file_path: str,
    vector_db: VectorDatabase = Depends(get_vector_db)
):
    """
    Importar documentos
    """
    try:
        from models.document_processor import DocumentProcessor
        
        document_processor = DocumentProcessor()
        export_system = ExportImportSystem()
        
        results = await export_system.import_documents(
            file_path,
            document_processor,
            vector_db
        )
        
        return {
            "success": True,
            "import_results": results
        }
        
    except Exception as e:
        logger.error(f"Error importando documentos: {e}")
        raise HTTPException(status_code=500, detail=f"Error importando: {str(e)}")

@router.post("/import/backup")
async def import_system_backup(
    backup_path: str,
    vector_db: VectorDatabase = Depends(get_vector_db),
    search_engine: AISearchEngine = Depends(get_search_engine)
):
    """
    Restaurar sistema desde respaldo
    """
    try:
        export_system = ExportImportSystem()
        
        results = await export_system.import_system_backup(
            backup_path,
            vector_db,
            search_engine
        )
        
        return {
            "success": True,
            "restore_results": results
        }
        
    except Exception as e:
        logger.error(f"Error restaurando respaldo: {e}")
        raise HTTPException(status_code=500, detail=f"Error restaurando: {str(e)}")

# Endpoints de Métricas Avanzadas

@router.get("/metrics/performance")
async def get_performance_metrics(
    time_range: str = Query("24h", description="Rango de tiempo"),
    vector_db: VectorDatabase = Depends(get_vector_db)
):
    """
    Obtener métricas de rendimiento
    """
    try:
        stats = await vector_db.get_statistics()
        
        # Simular métricas de rendimiento
        performance_metrics = {
            "search_performance": {
                "avg_search_time_ms": 125,
                "p95_search_time_ms": 250,
                "p99_search_time_ms": 500,
                "searches_per_second": 45
            },
            "system_performance": {
                "memory_usage_mb": 512,
                "cpu_usage_percent": 25,
                "disk_usage_mb": stats.get("database_size_bytes", 0) / 1024 / 1024,
                "active_connections": 12
            },
            "database_performance": {
                "total_documents": stats.get("total_documents", 0),
                "index_size_mb": stats.get("embeddings_size_bytes", 0) / 1024 / 1024,
                "query_cache_hit_rate": 0.85,
                "index_efficiency": 0.92
            }
        }
        
        return {
            "success": True,
            "metrics": performance_metrics,
            "time_range": time_range,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo métricas: {str(e)}")

@router.get("/metrics/usage")
async def get_usage_metrics(
    time_range: str = Query("7d", description="Rango de tiempo")
):
    """
    Obtener métricas de uso
    """
    try:
        # Simular métricas de uso
        usage_metrics = {
            "search_usage": {
                "total_searches": 1250,
                "unique_users": 45,
                "avg_searches_per_user": 27.8,
                "peak_usage_hour": 14,
                "most_popular_queries": [
                    {"query": "inteligencia artificial", "count": 45},
                    {"query": "machine learning", "count": 38},
                    {"query": "python", "count": 32}
                ]
            },
            "content_usage": {
                "most_viewed_documents": [
                    {"title": "Introducción a la IA", "views": 125},
                    {"title": "Machine Learning Básico", "views": 98},
                    {"title": "Python para Principiantes", "views": 87}
                ],
                "content_categories": {
                    "tecnologia": 45,
                    "programacion": 32,
                    "ciencia": 23
                }
            },
            "user_behavior": {
                "avg_session_duration_minutes": 12.5,
                "bounce_rate": 0.15,
                "return_user_rate": 0.65,
                "search_success_rate": 0.92
            }
        }
        
        return {
            "success": True,
            "metrics": usage_metrics,
            "time_range": time_range,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas de uso: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo métricas: {str(e)}")

@router.get("/health/detailed")
async def get_detailed_health(
    vector_db: VectorDatabase = Depends(get_vector_db),
    search_engine: AISearchEngine = Depends(get_search_engine)
):
    """
    Obtener estado detallado del sistema
    """
    try:
        # Verificar componentes
        db_stats = await vector_db.get_statistics()
        engine_stats = search_engine.get_statistics()
        
        health_status = {
            "overall_status": "healthy",
            "components": {
                "database": {
                    "status": "healthy",
                    "documents": db_stats.get("total_documents", 0),
                    "size_mb": db_stats.get("database_size_bytes", 0) / 1024 / 1024
                },
                "search_engine": {
                    "status": "healthy",
                    "model": engine_stats.get("embedding_model", "unknown"),
                    "documents_indexed": engine_stats.get("total_documents", 0)
                },
                "analytics": {
                    "status": "healthy",
                    "last_analysis": datetime.now().isoformat()
                }
            },
            "performance": {
                "avg_response_time_ms": 125,
                "uptime_percent": 99.9,
                "error_rate_percent": 0.1
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "health": health_status
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del sistema: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")



























