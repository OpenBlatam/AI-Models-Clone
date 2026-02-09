"""
Notification System - Sistema de Notificaciones
Sistema de notificaciones en tiempo real para el motor de búsqueda
"""

import asyncio
import logging
import json
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import uuid
from dataclasses import dataclass, asdict
import websockets
from websockets.server import WebSocketServerProtocol
import threading
import queue

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Tipos de notificaciones"""
    SEARCH_COMPLETED = "search_completed"
    DOCUMENT_UPLOADED = "document_uploaded"
    SYSTEM_UPDATE = "system_update"
    RECOMMENDATION_READY = "recommendation_ready"
    ERROR_OCCURRED = "error_occurred"
    ANALYTICS_UPDATE = "analytics_update"
    BATCH_PROCESSING_COMPLETE = "batch_processing_complete"

class NotificationPriority(Enum):
    """Prioridades de notificaciones"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Notification:
    """Estructura de una notificación"""
    id: str
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    data: Dict[str, Any]
    user_id: Optional[str] = None
    created_at: str = None
    expires_at: Optional[str] = None
    read: bool = False
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        
        if self.expires_at is None and self.priority != NotificationPriority.CRITICAL:
            # Las notificaciones expiran en 24 horas por defecto
            expires = datetime.now() + timedelta(hours=24)
            self.expires_at = expires.isoformat()

class NotificationSystem:
    """
    Sistema de notificaciones en tiempo real
    """
    
    def __init__(self):
        self.notifications: Dict[str, Notification] = {}
        self.user_notifications: Dict[str, List[str]] = {}
        self.websocket_connections: Dict[str, WebSocketServerProtocol] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
        self.notification_queue = queue.Queue()
        self.websocket_server = None
        self.server_thread = None
        self.running = False
        
    async def initialize(self, host: str = "localhost", port: int = 8765):
        """Inicializar el sistema de notificaciones"""
        try:
            logger.info("Inicializando sistema de notificaciones...")
            
            # Iniciar servidor WebSocket
            self.websocket_server = await websockets.serve(
                self._handle_websocket_connection,
                host, port
            )
            
            # Iniciar hilo para procesar notificaciones
            self.running = True
            self.server_thread = threading.Thread(target=self._process_notifications)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            logger.info(f"Sistema de notificaciones iniciado en ws://{host}:{port}")
            
        except Exception as e:
            logger.error(f"Error inicializando sistema de notificaciones: {e}")
            raise
    
    async def shutdown(self):
        """Cerrar el sistema de notificaciones"""
        try:
            self.running = False
            
            if self.websocket_server:
                self.websocket_server.close()
                await self.websocket_server.wait_closed()
            
            if self.server_thread:
                self.server_thread.join(timeout=5)
            
            logger.info("Sistema de notificaciones cerrado")
            
        except Exception as e:
            logger.error(f"Error cerrando sistema de notificaciones: {e}")
    
    async def send_notification(self, notification: Notification) -> str:
        """Enviar una notificación"""
        try:
            # Generar ID único si no existe
            if not notification.id:
                notification.id = str(uuid.uuid4())
            
            # Guardar notificación
            self.notifications[notification.id] = notification
            
            # Agregar a notificaciones del usuario si aplica
            if notification.user_id:
                if notification.user_id not in self.user_notifications:
                    self.user_notifications[notification.user_id] = []
                self.user_notifications[notification.user_id].append(notification.id)
            
            # Agregar a cola para procesamiento
            self.notification_queue.put(notification)
            
            logger.info(f"Notificación enviada: {notification.id}")
            return notification.id
            
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
            raise
    
    async def send_search_completed_notification(self, user_id: str, query: str, 
                                               results_count: int, search_time: float):
        """Enviar notificación de búsqueda completada"""
        notification = Notification(
            id=str(uuid.uuid4()),
            type=NotificationType.SEARCH_COMPLETED,
            priority=NotificationPriority.LOW,
            title="Búsqueda Completada",
            message=f"Se encontraron {results_count} resultados para '{query}' en {search_time:.2f}s",
            data={
                "query": query,
                "results_count": results_count,
                "search_time": search_time
            },
            user_id=user_id
        )
        
        return await self.send_notification(notification)
    
    async def send_document_uploaded_notification(self, user_id: str, document_title: str, 
                                                document_id: str):
        """Enviar notificación de documento subido"""
        notification = Notification(
            id=str(uuid.uuid4()),
            type=NotificationType.DOCUMENT_UPLOADED,
            priority=NotificationPriority.MEDIUM,
            title="Documento Subido",
            message=f"El documento '{document_title}' ha sido procesado exitosamente",
            data={
                "document_title": document_title,
                "document_id": document_id
            },
            user_id=user_id
        )
        
        return await self.send_notification(notification)
    
    async def send_system_update_notification(self, message: str, priority: NotificationPriority = NotificationPriority.MEDIUM):
        """Enviar notificación de actualización del sistema"""
        notification = Notification(
            id=str(uuid.uuid4()),
            type=NotificationType.SYSTEM_UPDATE,
            priority=priority,
            title="Actualización del Sistema",
            message=message,
            data={}
        )
        
        return await self.send_notification(notification)
    
    async def send_recommendation_notification(self, user_id: str, recommendation_count: int):
        """Enviar notificación de recomendaciones listas"""
        notification = Notification(
            id=str(uuid.uuid4()),
            type=NotificationType.RECOMMENDATION_READY,
            priority=NotificationPriority.LOW,
            title="Nuevas Recomendaciones",
            message=f"Tienes {recommendation_count} nuevas recomendaciones personalizadas",
            data={
                "recommendation_count": recommendation_count
            },
            user_id=user_id
        )
        
        return await self.send_notification(notification)
    
    async def send_error_notification(self, error_message: str, error_details: Dict[str, Any] = None):
        """Enviar notificación de error"""
        notification = Notification(
            id=str(uuid.uuid4()),
            type=NotificationType.ERROR_OCCURRED,
            priority=NotificationPriority.HIGH,
            title="Error del Sistema",
            message=error_message,
            data=error_details or {}
        )
        
        return await self.send_notification(notification)
    
    async def send_analytics_update_notification(self, user_id: str, analytics_data: Dict[str, Any]):
        """Enviar notificación de actualización de analytics"""
        notification = Notification(
            id=str(uuid.uuid4()),
            type=NotificationType.ANALYTICS_UPDATE,
            priority=NotificationPriority.LOW,
            title="Analytics Actualizados",
            message="Los datos de analytics han sido actualizados",
            data=analytics_data,
            user_id=user_id
        )
        
        return await self.send_notification(notification)
    
    async def send_batch_processing_notification(self, user_id: str, batch_id: str, 
                                               status: str, processed_count: int = 0):
        """Enviar notificación de procesamiento por lotes"""
        priority = NotificationPriority.HIGH if status == "error" else NotificationPriority.MEDIUM
        
        notification = Notification(
            id=str(uuid.uuid4()),
            type=NotificationType.BATCH_PROCESSING_COMPLETE,
            priority=priority,
            title="Procesamiento por Lotes Completado",
            message=f"Lote {batch_id}: {status} - {processed_count} documentos procesados",
            data={
                "batch_id": batch_id,
                "status": status,
                "processed_count": processed_count
            },
            user_id=user_id
        )
        
        return await self.send_notification(notification)
    
    async def get_user_notifications(self, user_id: str, limit: int = 50, 
                                   unread_only: bool = False) -> List[Dict[str, Any]]:
        """Obtener notificaciones de un usuario"""
        try:
            if user_id not in self.user_notifications:
                return []
            
            notification_ids = self.user_notifications[user_id]
            notifications = []
            
            for notification_id in notification_ids:
                if notification_id in self.notifications:
                    notification = self.notifications[notification_id]
                    
                    # Filtrar por estado de lectura si se solicita
                    if unread_only and notification.read:
                        continue
                    
                    # Verificar si la notificación ha expirado
                    if notification.expires_at:
                        expires = datetime.fromisoformat(notification.expires_at)
                        if datetime.now() > expires:
                            continue
                    
                    notifications.append(asdict(notification))
            
            # Ordenar por fecha de creación (más recientes primero)
            notifications.sort(key=lambda x: x["created_at"], reverse=True)
            
            return notifications[:limit]
            
        except Exception as e:
            logger.error(f"Error obteniendo notificaciones del usuario: {e}")
            return []
    
    async def mark_notification_as_read(self, notification_id: str, user_id: str = None) -> bool:
        """Marcar notificación como leída"""
        try:
            if notification_id in self.notifications:
                notification = self.notifications[notification_id]
                
                # Verificar que el usuario tenga acceso a esta notificación
                if user_id and notification.user_id and notification.user_id != user_id:
                    return False
                
                notification.read = True
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error marcando notificación como leída: {e}")
            return False
    
    async def delete_notification(self, notification_id: str, user_id: str = None) -> bool:
        """Eliminar notificación"""
        try:
            if notification_id in self.notifications:
                notification = self.notifications[notification_id]
                
                # Verificar que el usuario tenga acceso a esta notificación
                if user_id and notification.user_id and notification.user_id != user_id:
                    return False
                
                # Eliminar de la lista de notificaciones del usuario
                if notification.user_id and notification.user_id in self.user_notifications:
                    if notification_id in self.user_notifications[notification.user_id]:
                        self.user_notifications[notification.user_id].remove(notification_id)
                
                # Eliminar la notificación
                del self.notifications[notification_id]
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error eliminando notificación: {e}")
            return False
    
    async def cleanup_expired_notifications(self):
        """Limpiar notificaciones expiradas"""
        try:
            current_time = datetime.now()
            expired_notifications = []
            
            for notification_id, notification in self.notifications.items():
                if notification.expires_at:
                    expires = datetime.fromisoformat(notification.expires_at)
                    if current_time > expires:
                        expired_notifications.append(notification_id)
            
            for notification_id in expired_notifications:
                await self.delete_notification(notification_id)
            
            if expired_notifications:
                logger.info(f"Eliminadas {len(expired_notifications)} notificaciones expiradas")
            
        except Exception as e:
            logger.error(f"Error limpiando notificaciones expiradas: {e}")
    
    async def subscribe_to_notifications(self, user_id: str, websocket: WebSocketServerProtocol):
        """Suscribir usuario a notificaciones en tiempo real"""
        try:
            self.websocket_connections[user_id] = websocket
            logger.info(f"Usuario {user_id} suscrito a notificaciones")
            
        except Exception as e:
            logger.error(f"Error suscribiendo usuario a notificaciones: {e}")
    
    async def unsubscribe_from_notifications(self, user_id: str):
        """Desuscribir usuario de notificaciones"""
        try:
            if user_id in self.websocket_connections:
                del self.websocket_connections[user_id]
                logger.info(f"Usuario {user_id} desuscrito de notificaciones")
            
        except Exception as e:
            logger.error(f"Error desuscribiendo usuario: {e}")
    
    async def _handle_websocket_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Manejar conexión WebSocket"""
        try:
            user_id = None
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    action = data.get("action")
                    
                    if action == "subscribe":
                        user_id = data.get("user_id")
                        if user_id:
                            await self.subscribe_to_notifications(user_id, websocket)
                            await websocket.send(json.dumps({
                                "type": "subscription_confirmed",
                                "message": f"Suscrito a notificaciones para usuario {user_id}"
                            }))
                    
                    elif action == "unsubscribe":
                        if user_id:
                            await self.unsubscribe_from_notifications(user_id)
                            user_id = None
                    
                    elif action == "mark_read":
                        notification_id = data.get("notification_id")
                        if notification_id and user_id:
                            await self.mark_notification_as_read(notification_id, user_id)
                    
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Formato de mensaje inválido"
                    }))
                except Exception as e:
                    logger.error(f"Error procesando mensaje WebSocket: {e}")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Error procesando mensaje"
                    }))
        
        except websockets.exceptions.ConnectionClosed:
            if user_id:
                await self.unsubscribe_from_notifications(user_id)
        except Exception as e:
            logger.error(f"Error en conexión WebSocket: {e}")
    
    def _process_notifications(self):
        """Procesar notificaciones en cola (ejecutar en hilo separado)"""
        while self.running:
            try:
                # Obtener notificación de la cola (con timeout)
                try:
                    notification = self.notification_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # Procesar notificación
                asyncio.run_coroutine_threadsafe(
                    self._process_single_notification(notification),
                    asyncio.get_event_loop()
                )
                
            except Exception as e:
                logger.error(f"Error procesando notificación: {e}")
    
    async def _process_single_notification(self, notification: Notification):
        """Procesar una notificación individual"""
        try:
            # Enviar a suscriptores WebSocket
            if notification.user_id and notification.user_id in self.websocket_connections:
                websocket = self.websocket_connections[notification.user_id]
                try:
                    await websocket.send(json.dumps({
                        "type": "notification",
                        "data": asdict(notification)
                    }))
                except websockets.exceptions.ConnectionClosed:
                    await self.unsubscribe_from_notifications(notification.user_id)
            
            # Notificar a suscriptores internos
            notification_type = notification.type.value
            if notification_type in self.subscribers:
                for callback in self.subscribers[notification_type]:
                    try:
                        await callback(notification)
                    except Exception as e:
                        logger.error(f"Error en callback de notificación: {e}")
            
            logger.info(f"Notificación procesada: {notification.id}")
            
        except Exception as e:
            logger.error(f"Error procesando notificación individual: {e}")
    
    def subscribe_to_notification_type(self, notification_type: NotificationType, 
                                     callback: Callable):
        """Suscribirse a un tipo específico de notificación"""
        try:
            type_key = notification_type.value
            if type_key not in self.subscribers:
                self.subscribers[type_key] = []
            self.subscribers[type_key].append(callback)
            
        except Exception as e:
            logger.error(f"Error suscribiéndose a tipo de notificación: {e}")
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema de notificaciones"""
        try:
            total_notifications = len(self.notifications)
            unread_count = sum(1 for n in self.notifications.values() if not n.read)
            
            # Contar por tipo
            type_counts = {}
            for notification in self.notifications.values():
                type_key = notification.type.value
                type_counts[type_key] = type_counts.get(type_key, 0) + 1
            
            # Contar por prioridad
            priority_counts = {}
            for notification in self.notifications.values():
                priority_key = notification.priority.value
                priority_counts[priority_key] = priority_counts.get(priority_key, 0) + 1
            
            return {
                "total_notifications": total_notifications,
                "unread_notifications": unread_count,
                "active_connections": len(self.websocket_connections),
                "notifications_by_type": type_counts,
                "notifications_by_priority": priority_counts,
                "queue_size": self.notification_queue.qsize()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de notificaciones: {e}")
            return {}


























