"""
AI Search Model - FastAPI Backend
Sistema de búsqueda inteligente con IA para documentos
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import asyncio
import logging
from datetime import datetime
import os
import sys

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.search_engine import AISearchEngine
from models.document_processor import DocumentProcessor
from database.vector_db import VectorDatabase
from config.settings import Settings
from backend.analytics_routes import router as analytics_router
from backend.recommendation_routes import router as recommendation_router
from backend.notification_routes import router as notification_router
from backend.chatbot_routes import router as chatbot_router
from backend.voice_routes import router as voice_router

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="AI Search Model API",
    description="API para búsqueda inteligente de documentos usando IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas de analytics
app.include_router(analytics_router)
app.include_router(recommendation_router)
app.include_router(notification_router)
app.include_router(chatbot_router)
app.include_router(voice_router)

# Configuración global
settings = Settings()

# Instancias globales
search_engine = None
document_processor = None
vector_db = None
analytics_engine = None
batch_processor = None
export_import = None
recommendation_engine = None
notification_system = None
cache_system = None
chatbot = None
voice_system = None
advanced_ml = None
multi_language = None

# Modelos Pydantic
class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10
    filters: Optional[Dict[str, Any]] = None
    search_type: Optional[str] = "semantic"  # semantic, keyword, hybrid

class SearchResult(BaseModel):
    document_id: str
    title: str
    content: str
    score: float
    metadata: Dict[str, Any]
    snippet: str

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_results: int
    query: str
    search_time: float
    timestamp: datetime

class DocumentUpload(BaseModel):
    title: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    document_type: Optional[str] = "text"

class IndexResponse(BaseModel):
    document_id: str
    status: str
    message: str

# Dependencias
async def get_search_engine():
    global search_engine
    if search_engine is None:
        search_engine = AISearchEngine()
        await search_engine.initialize()
    return search_engine

async def get_document_processor():
    global document_processor
    if document_processor is None:
        document_processor = DocumentProcessor()
    return document_processor

async def get_vector_db():
    global vector_db
    if vector_db is None:
        vector_db = VectorDatabase()
        await vector_db.initialize()
    return vector_db

# Eventos de la aplicación
@app.on_event("startup")
async def startup_event():
    """Inicializar servicios al arrancar la aplicación"""
    logger.info("Iniciando AI Search Model API...")
    
    try:
        # Inicializar componentes
        search_engine = await get_search_engine()
        document_processor = await get_document_processor()
        vector_db = await get_vector_db()
        
        logger.info("Todos los servicios inicializados correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar servicios: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Limpiar recursos al cerrar la aplicación"""
    logger.info("Cerrando AI Search Model API...")
    
    if vector_db:
        await vector_db.close()

# Rutas de la API

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "AI Search Model API",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Verificar estado de la API"""
    try:
        # Verificar que todos los servicios estén funcionando
        search_engine = await get_search_engine()
        vector_db = await get_vector_db()
        
        return {
            "status": "healthy",
            "services": {
                "search_engine": "active",
                "vector_database": "active",
                "document_processor": "active"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    search_engine: AISearchEngine = Depends(get_search_engine)
):
    """
    Buscar documentos usando IA semántica
    """
    try:
        start_time = datetime.now()
        
        logger.info(f"Búsqueda iniciada: '{request.query}'")
        
        # Realizar búsqueda
        results = await search_engine.search(
            query=request.query,
            limit=request.limit,
            filters=request.filters,
            search_type=request.search_type
        )
        
        end_time = datetime.now()
        search_time = (end_time - start_time).total_seconds()
        
        # Convertir resultados al formato de respuesta
        search_results = []
        for result in results:
            search_results.append(SearchResult(
                document_id=result["document_id"],
                title=result["title"],
                content=result["content"],
                score=result["score"],
                metadata=result["metadata"],
                snippet=result["snippet"]
            ))
        
        response = SearchResponse(
            results=search_results,
            total_results=len(search_results),
            query=request.query,
            search_time=search_time,
            timestamp=end_time
        )
        
        logger.info(f"Búsqueda completada en {search_time:.3f}s, {len(search_results)} resultados")
        
        return response
        
    except Exception as e:
        logger.error(f"Error en búsqueda: {e}")
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")

@app.post("/documents", response_model=IndexResponse)
async def index_document(
    document: DocumentUpload,
    document_processor: DocumentProcessor = Depends(get_document_processor),
    vector_db: VectorDatabase = Depends(get_vector_db)
):
    """
    Indexar un nuevo documento en la base de datos
    """
    try:
        logger.info(f"Indexando documento: '{document.title}'")
        
        # Procesar documento
        processed_doc = await document_processor.process_document(
            title=document.title,
            content=document.content,
            metadata=document.metadata,
            document_type=document.document_type
        )
        
        # Guardar en base de datos vectorial
        document_id = await vector_db.add_document(processed_doc)
        
        logger.info(f"Documento indexado exitosamente: {document_id}")
        
        return IndexResponse(
            document_id=document_id,
            status="success",
            message="Documento indexado correctamente"
        )
        
    except Exception as e:
        logger.error(f"Error al indexar documento: {e}")
        raise HTTPException(status_code=500, detail=f"Error al indexar: {str(e)}")

@app.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    vector_db: VectorDatabase = Depends(get_vector_db)
):
    """
    Obtener un documento específico por ID
    """
    try:
        document = await vector_db.get_document(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener documento: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener documento: {str(e)}")

@app.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    vector_db: VectorDatabase = Depends(get_vector_db)
):
    """
    Eliminar un documento de la base de datos
    """
    try:
        success = await vector_db.delete_document(document_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        return {"message": "Documento eliminado correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar documento: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar documento: {str(e)}")

@app.get("/documents")
async def list_documents(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    vector_db: VectorDatabase = Depends(get_vector_db)
):
    """
    Listar documentos en la base de datos
    """
    try:
        documents = await vector_db.list_documents(limit=limit, offset=offset)
        total_count = await vector_db.count_documents()
        
        return {
            "documents": documents,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error al listar documentos: {e}")
        raise HTTPException(status_code=500, detail=f"Error al listar documentos: {str(e)}")

@app.get("/stats")
async def get_statistics(
    vector_db: VectorDatabase = Depends(get_vector_db)
):
    """
    Obtener estadísticas de la base de datos
    """
    try:
        stats = await vector_db.get_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Inicializar componentes al arrancar la aplicación"""
    global search_engine, document_processor, vector_db, analytics_engine, batch_processor, export_import, recommendation_engine, notification_system, cache_system, chatbot, voice_system, advanced_ml, multi_language
    
    try:
        logger.info("Inicializando componentes...")
        
        # Inicializar base de datos vectorial
        vector_db = VectorDatabase()
        await vector_db.initialize()
        
        # Inicializar procesador de documentos
        document_processor = DocumentProcessor()
        await document_processor.initialize()
        
        # Inicializar motor de búsqueda
        search_engine = AISearchEngine()
        await search_engine.initialize()
        
        # Inicializar motor de analytics
        from models.analytics_engine import AnalyticsEngine
        analytics_engine = AnalyticsEngine()
        await analytics_engine.initialize()
        
        # Inicializar procesador por lotes
        from models.batch_processor import BatchProcessor
        batch_processor = BatchProcessor()
        await batch_processor.initialize()
        
        # Inicializar sistema de export/import
        from models.export_import import ExportImportSystem
        export_import = ExportImportSystem()
        await export_import.initialize()
        
        # Inicializar motor de recomendaciones
        from models.recommendation_engine import RecommendationEngine
        recommendation_engine = RecommendationEngine()
        await recommendation_engine.initialize()
        
        # Inicializar sistema de notificaciones
        from models.notification_system import NotificationSystem
        notification_system = NotificationSystem()
        await notification_system.initialize()
        
        # Inicializar sistema de cache
        from models.cache_system import CacheSystem
        cache_system = CacheSystem()
        cache_system.start_cleanup_thread()
        
        # Inicializar chatbot de IA
        from models.ai_chatbot import AIChatbot
        chatbot = AIChatbot()
        await chatbot.initialize()
        
        # Inicializar sistema de búsqueda por voz
        from models.voice_search import VoiceSearchSystem
        voice_system = VoiceSearchSystem()
        await voice_system.initialize()
        
        # Inicializar sistema de ML avanzado
        from models.advanced_ml import AdvancedMLSystem
        advanced_ml = AdvancedMLSystem()
        await advanced_ml.initialize()
        
        # Inicializar sistema multiidioma
        from models.multi_language import MultiLanguageSystem
        multi_language = MultiLanguageSystem()
        await multi_language.initialize()
        
        # Configurar instancias globales en los routers
        from backend import analytics_routes, recommendation_routes, notification_routes, chatbot_routes, voice_routes
        analytics_routes.analytics_engine = analytics_engine
        analytics_routes.batch_processor = batch_processor
        analytics_routes.export_import = export_import
        recommendation_routes.recommendation_engine = recommendation_engine
        recommendation_routes.cache_system = cache_system
        recommendation_routes.notification_system = notification_system
        notification_routes.notification_system = notification_system
        chatbot_routes.chatbot = chatbot
        voice_routes.voice_system = voice_system
        
        logger.info("Componentes inicializados exitosamente")
        
    except Exception as e:
        logger.error(f"Error inicializando componentes: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Limpiar recursos al cerrar la aplicación"""
    global cache_system, notification_system, voice_system
    
    try:
        logger.info("Cerrando componentes...")
        
        if cache_system:
            cache_system.stop_cleanup_thread()
        
        if notification_system:
            await notification_system.shutdown()
        
        if voice_system:
            await voice_system.shutdown()
        
        logger.info("Componentes cerrados exitosamente")
        
    except Exception as e:
        logger.error(f"Error cerrando componentes: {e}")

# Manejo de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
