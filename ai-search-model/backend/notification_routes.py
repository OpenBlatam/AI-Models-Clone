"""
Notification Routes - Rutas de Notificaciones
API endpoints para el sistema de notificaciones
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, Query
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime

from models.notification_system import NotificationSystem, NotificationType, NotificationPriority

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

# Instancia global (se inicializará en main.py)
notification_system: Optional[NotificationSystem] = None

def get_notification_system() -> NotificationSystem:
    """Dependency para obtener el sistema de notificaciones"""
    if notification_system is None:
        raise HTTPException(status_code=503, detail="Notification system not initialized")
    return notification_system

@router.get("/user/{user_id}")
async def get_user_notifications(
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    notifications: NotificationSystem = Depends(get_notification_system)
):
    """Obtener notificaciones de un usuario"""
    try:
        user_notifications = await notifications.get_user_notifications(
            user_id, limit, unread_only
        )
        
        return {
            "user_id": user_id,
            "notifications": user_notifications,
            "count": len(user_notifications),
            "unread_only": unread_only,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo notificaciones del usuario: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user/{user_id}/read/{notification_id}")
async def mark_notification_as_read(
    user_id: str,
    notification_id: str,
    notifications: NotificationSystem = Depends(get_notification_system)
):
    """Marcar notificación como leída"""
    try:
        success = await notifications.mark_notification_as_read(notification_id, user_id)
        
        if success:
            return {
                "success": True,
                "message": "Notificación marcada como leída",
                "notification_id": notification_id,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Notificación no encontrada o sin permisos")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marcando notificación como leída: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/user/{user_id}/{notification_id}")
async def delete_notification(
    user_id: str,
    notification_id: str,
    notifications: NotificationSystem = Depends(get_notification_system)
):
    """Eliminar notificación"""
    try:
        success = await notifications.delete_notification(notification_id, user_id)
        
        if success:
            return {
                "success": True,
                "message": "Notificación eliminada",
                "notification_id": notification_id,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Notificación no encontrada o sin permisos")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando notificación: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user/{user_id}/read-all")
async def mark_all_notifications_as_read(
    user_id: str,
    notifications: NotificationSystem = Depends(get_notification_system)
):
    """Marcar todas las notificaciones del usuario como leídas"""
    try:
        user_notifications = await notifications.get_user_notifications(user_id, limit=1000)
        marked_count = 0
        
        for notification in user_notifications:
            if not notification["read"]:
                success = await notifications.mark_notification_as_read(
                    notification["id"], user_id
                )
                if success:
                    marked_count += 1
        
        return {
            "success": True,
            "message": f"{marked_count} notificaciones marcadas como leídas",
            "user_id": user_id,
            "marked_count": marked_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error marcando todas las notificaciones como leídas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/user/{user_id}/all")
async def delete_all_user_notifications(
    user_id: str,
    notifications: NotificationSystem = Depends(get_notification_system)
):
    """Eliminar todas las notificaciones del usuario"""
    try:
        user_notifications = await notifications.get_user_notifications(user_id, limit=1000)
        deleted_count = 0
        
        for notification in user_notifications:
            success = await notifications.delete_notification(
                notification["id"], user_id
            )
            if success:
                deleted_count += 1
        
        return {
            "success": True,
            "message": f"{deleted_count} notificaciones eliminadas",
            "user_id": user_id,
            "deleted_count": deleted_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error eliminando todas las notificaciones: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_notification_stats(
    notifications: NotificationSystem = Depends(get_notification_system)
):
    """Obtener estadísticas del sistema de notificaciones"""
    try:
        stats = notifications.get_notification_stats()
        
        return {
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de notificaciones: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup")
async def cleanup_expired_notifications(
    notifications: NotificationSystem = Depends(get_notification_system)
):
    """Limpiar notificaciones expiradas"""
    try:
        await notifications.cleanup_expired_notifications()
        
        return {
            "success": True,
            "message": "Notificaciones expiradas limpiadas",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error limpiando notificaciones expiradas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send")
async def send_notification(
    notification_type: str,
    priority: str,
    title: str,
    message: str,
    user_id: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
    ttl_hours: Optional[int] = None,
    notifications: NotificationSystem = Depends(get_notification_system)
):
    """Enviar notificación personalizada"""
    try:
        # Validar tipo de notificación
        try:
            notif_type = NotificationType(notification_type)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de notificación inválido: {notification_type}"
            )
        
        # Validar prioridad
        try:
            notif_priority = NotificationPriority(priority)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Prioridad inválida: {priority}"
            )
        
        # Crear notificación
        from models.notification_system import Notification
        notification = Notification(
            id="",  # Se generará automáticamente
            type=notif_type,
            priority=notif_priority,
            title=title,
            message=message,
            data=data or {},
            user_id=user_id
        )
        
        # Establecer TTL personalizado si se proporciona
        if ttl_hours:
            from datetime import timedelta
            expires = datetime.now() + timedelta(hours=ttl_hours)
            notification.expires_at = expires.isoformat()
        
        # Enviar notificación
        notification_id = await notifications.send_notification(notification)
        
        return {
            "success": True,
            "message": "Notificación enviada exitosamente",
            "notification_id": notification_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enviando notificación: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    notifications: NotificationSystem = Depends(get_notification_system)
):
    """WebSocket endpoint para notificaciones en tiempo real"""
    await websocket.accept()
    
    try:
        # Suscribir usuario a notificaciones
        await notifications.subscribe_to_notifications(user_id, websocket)
        
        # Enviar mensaje de confirmación
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": f"Conectado a notificaciones para usuario {user_id}",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        # Mantener conexión activa
        while True:
            try:
                # Esperar mensajes del cliente
                data = await websocket.receive_text()
                message = json.loads(data)
                
                action = message.get("action")
                
                if action == "ping":
                    # Responder a ping con pong
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }))
                
                elif action == "get_notifications":
                    # Enviar notificaciones actuales del usuario
                    user_notifications = await notifications.get_user_notifications(
                        user_id, limit=20, unread_only=True
                    )
                    await websocket.send_text(json.dumps({
                        "type": "notifications",
                        "data": user_notifications,
                        "timestamp": datetime.now().isoformat()
                    }))
                
                elif action == "mark_read":
                    # Marcar notificación como leída
                    notification_id = message.get("notification_id")
                    if notification_id:
                        await notifications.mark_notification_as_read(notification_id, user_id)
                        await websocket.send_text(json.dumps({
                            "type": "notification_read",
                            "notification_id": notification_id,
                            "timestamp": datetime.now().isoformat()
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
        logger.error(f"Error en WebSocket: {e}")
    finally:
        # Desuscribir usuario
        await notifications.unsubscribe_from_notifications(user_id)

@router.get("/types")
async def get_notification_types():
    """Obtener tipos de notificaciones disponibles"""
    return {
        "notification_types": [
            {
                "value": notification_type.value,
                "name": notification_type.name,
                "description": _get_notification_type_description(notification_type)
            }
            for notification_type in NotificationType
        ],
        "priorities": [
            {
                "value": priority.value,
                "name": priority.name,
                "description": _get_priority_description(priority)
            }
            for priority in NotificationPriority
        ],
        "timestamp": datetime.now().isoformat()
    }

def _get_notification_type_description(notification_type: NotificationType) -> str:
    """Obtener descripción de tipo de notificación"""
    descriptions = {
        NotificationType.SEARCH_COMPLETED: "Notificación cuando se completa una búsqueda",
        NotificationType.DOCUMENT_UPLOADED: "Notificación cuando se sube un documento",
        NotificationType.SYSTEM_UPDATE: "Notificación de actualizaciones del sistema",
        NotificationType.RECOMMENDATION_READY: "Notificación cuando hay nuevas recomendaciones",
        NotificationType.ERROR_OCCURRED: "Notificación de errores del sistema",
        NotificationType.ANALYTICS_UPDATE: "Notificación de actualizaciones de analytics",
        NotificationType.BATCH_PROCESSING_COMPLETE: "Notificación de procesamiento por lotes completado"
    }
    return descriptions.get(notification_type, "Tipo de notificación personalizada")

def _get_priority_description(priority: NotificationPriority) -> str:
    """Obtener descripción de prioridad"""
    descriptions = {
        NotificationPriority.LOW: "Prioridad baja - No urgente",
        NotificationPriority.MEDIUM: "Prioridad media - Importante",
        NotificationPriority.HIGH: "Prioridad alta - Urgente",
        NotificationPriority.CRITICAL: "Prioridad crítica - Requiere atención inmediata"
    }
    return descriptions.get(priority, "Prioridad personalizada")


























