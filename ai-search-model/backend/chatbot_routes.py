"""
Chatbot Routes - Rutas del Chatbot de IA
API endpoints para el sistema de chatbot inteligente
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, Query
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime

from models.ai_chatbot import AIChatbot, ChatMessage, ChatSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])

# Instancia global (se inicializará en main.py)
chatbot: Optional[AIChatbot] = None

def get_chatbot() -> AIChatbot:
    """Dependency para obtener el chatbot"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    return chatbot

@router.post("/sessions")
async def create_chat_session(
    user_id: str,
    chatbot: AIChatbot = Depends(get_chatbot)
):
    """Crear nueva sesión de chat"""
    try:
        session_id = await chatbot.create_session(user_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "user_id": user_id,
            "message": "Sesión de chat creada exitosamente",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creando sesión de chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    message: str,
    chatbot: AIChatbot = Depends(get_chatbot)
):
    """Enviar mensaje al chatbot"""
    try:
        if not message or len(message.strip()) < 1:
            raise HTTPException(status_code=400, detail="Mensaje no puede estar vacío")
        
        # Obtener motor de búsqueda y base de datos vectorial (si están disponibles)
        search_engine = None
        vector_db = None
        
        try:
            from backend.main import search_engine, vector_db
        except ImportError:
            pass
        
        # Enviar mensaje al chatbot
        response = await chatbot.send_message(
            session_id, message, search_engine, vector_db
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "response": response.response,
            "confidence": response.confidence_score,
            "intent": response.intent,
            "source_documents": response.source_documents,
            "entities": response.entities,
            "timestamp": datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error enviando mensaje: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/history")
async def get_chat_history(
    session_id: str,
    limit: int = Query(20, ge=1, le=100),
    chatbot: AIChatbot = Depends(get_chatbot)
):
    """Obtener historial de chat"""
    try:
        messages = await chatbot.get_session_history(session_id, limit)
        
        # Convertir mensajes a formato serializable
        serialized_messages = []
        for msg in messages:
            serialized_messages.append({
                "id": msg.id,
                "user_id": msg.user_id,
                "message": msg.message,
                "response": msg.response,
                "timestamp": msg.timestamp,
                "message_type": msg.message_type,
                "confidence_score": msg.confidence_score,
                "source_documents": msg.source_documents,
                "intent": msg.intent,
                "entities": msg.entities
            })
        
        return {
            "session_id": session_id,
            "messages": serialized_messages,
            "count": len(serialized_messages),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo historial de chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def end_chat_session(
    session_id: str,
    chatbot: AIChatbot = Depends(get_chatbot)
):
    """Terminar sesión de chat"""
    try:
        success = await chatbot.end_session(session_id)
        
        if success:
            return {
                "success": True,
                "message": "Sesión de chat terminada exitosamente",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error terminando sesión: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def get_active_sessions(
    chatbot: AIChatbot = Depends(get_chatbot)
):
    """Obtener sesiones activas"""
    try:
        active_sessions = chatbot.get_active_sessions()
        
        return {
            "active_sessions": active_sessions,
            "count": len(active_sessions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo sesiones activas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_chatbot_stats(
    chatbot: AIChatbot = Depends(get_chatbot)
):
    """Obtener estadísticas del chatbot"""
    try:
        stats = chatbot.get_chatbot_stats()
        
        return {
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas del chatbot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intents")
async def get_supported_intents():
    """Obtener intenciones soportadas por el chatbot"""
    intents = {
        "search_document": {
            "name": "Búsqueda de Documentos",
            "description": "Buscar información en documentos",
            "examples": ["buscar documento", "encontrar información", "buscar en", "dónde está"]
        },
        "explain_concept": {
            "name": "Explicar Conceptos",
            "description": "Explicar conceptos y definiciones",
            "examples": ["qué significa", "explica", "definir", "qué es"]
        },
        "summarize": {
            "name": "Resumir Contenido",
            "description": "Crear resúmenes de documentos",
            "examples": ["resumen", "resumir", "síntesis", "puntos principales"]
        },
        "compare": {
            "name": "Comparar Elementos",
            "description": "Comparar diferentes elementos",
            "examples": ["comparar", "diferencias", "similitudes", "vs"]
        },
        "recommend": {
            "name": "Recomendar Contenido",
            "description": "Recomendar documentos o información",
            "examples": ["recomendar", "sugerir", "qué me recomiendas"]
        },
        "help": {
            "name": "Ayuda y Soporte",
            "description": "Obtener ayuda sobre el sistema",
            "examples": ["ayuda", "help", "cómo usar", "tutorial"]
        }
    }
    
    return {
        "intents": intents,
        "count": len(intents),
        "timestamp": datetime.now().isoformat()
    }

@router.websocket("/ws/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    chatbot: AIChatbot = Depends(get_chatbot)
):
    """WebSocket para chat en tiempo real"""
    await websocket.accept()
    
    try:
        # Verificar que la sesión existe
        if session_id not in chatbot.sessions:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Sesión no encontrada"
            }))
            await websocket.close()
            return
        
        # Enviar mensaje de confirmación
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": f"Conectado al chat de la sesión {session_id}",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        # Mantener conexión activa
        while True:
            try:
                # Recibir mensaje del cliente
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                action = message_data.get("action")
                
                if action == "send_message":
                    message = message_data.get("message", "")
                    
                    if message:
                        # Obtener motor de búsqueda y base de datos vectorial
                        search_engine = None
                        vector_db = None
                        
                        try:
                            from backend.main import search_engine, vector_db
                        except ImportError:
                            pass
                        
                        # Enviar mensaje al chatbot
                        response = await chatbot.send_message(
                            session_id, message, search_engine, vector_db
                        )
                        
                        # Enviar respuesta
                        await websocket.send_text(json.dumps({
                            "type": "message_response",
                            "response": response.response,
                            "confidence": response.confidence_score,
                            "intent": response.intent,
                            "source_documents": response.source_documents,
                            "entities": response.entities,
                            "timestamp": datetime.now().isoformat()
                        }))
                
                elif action == "get_history":
                    # Obtener historial
                    limit = message_data.get("limit", 20)
                    messages = await chatbot.get_session_history(session_id, limit)
                    
                    # Serializar mensajes
                    serialized_messages = []
                    for msg in messages:
                        serialized_messages.append({
                            "id": msg.id,
                            "message": msg.message,
                            "response": msg.response,
                            "timestamp": msg.timestamp,
                            "message_type": msg.message_type,
                            "confidence_score": msg.confidence_score,
                            "intent": msg.intent
                        })
                    
                    await websocket.send_text(json.dumps({
                        "type": "chat_history",
                        "messages": serialized_messages,
                        "timestamp": datetime.now().isoformat()
                    }))
                
                elif action == "ping":
                    # Responder a ping
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }))
                
                else:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Acción no reconocida"
                    }))
            
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Formato de mensaje inválido"
                }))
            except Exception as e:
                logger.error(f"Error procesando mensaje WebSocket: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Error procesando mensaje"
                }))
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Error en WebSocket de chat: {e}")
    finally:
        logger.info(f"Conexión WebSocket cerrada para sesión {session_id}")

@router.post("/sessions/{session_id}/feedback")
async def provide_feedback(
    session_id: str,
    message_id: str,
    feedback_type: str = Query(..., regex="^(positive|negative|neutral)$"),
    feedback_text: Optional[str] = None,
    chatbot: AIChatbot = Depends(get_chatbot)
):
    """Proporcionar feedback sobre una respuesta del chatbot"""
    try:
        # Verificar que la sesión existe
        if session_id not in chatbot.sessions:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        session = chatbot.sessions[session_id]
        
        # Buscar el mensaje
        message = None
        for msg in session.messages:
            if msg.id == message_id:
                message = msg
                break
        
        if not message:
            raise HTTPException(status_code=404, detail="Mensaje no encontrado")
        
        # Aquí podrías implementar lógica para procesar el feedback
        # Por ejemplo, actualizar el modelo de clasificación de intenciones
        
        return {
            "success": True,
            "message": "Feedback registrado exitosamente",
            "message_id": message_id,
            "feedback_type": feedback_type,
            "feedback_text": feedback_text,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registrando feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/analytics")
async def get_session_analytics(
    session_id: str,
    chatbot: AIChatbot = Depends(get_chatbot)
):
    """Obtener analytics de una sesión de chat"""
    try:
        # Verificar que la sesión existe
        if session_id not in chatbot.sessions:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        session = chatbot.sessions[session_id]
        
        # Analizar mensajes de la sesión
        total_messages = len(session.messages)
        user_messages = [msg for msg in session.messages if msg.message_type == "user"]
        assistant_messages = [msg for msg in session.messages if msg.message_type == "assistant"]
        
        # Contar intenciones
        intent_counts = {}
        for msg in assistant_messages:
            if msg.intent:
                intent_counts[msg.intent] = intent_counts.get(msg.intent, 0) + 1
        
        # Calcular confianza promedio
        confidence_scores = [msg.confidence_score for msg in assistant_messages if msg.confidence_score > 0]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Contar documentos fuente utilizados
        source_documents = set()
        for msg in assistant_messages:
            if msg.source_documents:
                source_documents.update(msg.source_documents)
        
        analytics = {
            "session_id": session_id,
            "user_id": session.user_id,
            "total_messages": total_messages,
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "intent_distribution": intent_counts,
            "average_confidence": round(avg_confidence, 3),
            "source_documents_used": len(source_documents),
            "session_duration": "N/A",  # Podrías calcular esto si tienes timestamps
            "created_at": session.created_at,
            "last_activity": session.last_activity
        }
        
        return {
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo analytics de sesión: {e}")
        raise HTTPException(status_code=500, detail=str(e))


























