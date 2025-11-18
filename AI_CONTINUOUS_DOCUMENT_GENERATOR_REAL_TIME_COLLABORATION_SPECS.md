# Especificaciones de Colaboración en Tiempo Real: IA Generadora Continua de Documentos

## Resumen

Este documento define las especificaciones técnicas para un sistema de colaboración en tiempo real que permite a múltiples usuarios trabajar simultáneamente en la generación y edición de documentos, con sincronización automática, control de versiones, y gestión de conflictos.

## 1. Arquitectura de Colaboración en Tiempo Real

### 1.1 Componentes del Sistema de Colaboración

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        REAL-TIME COLLABORATION SYSTEM                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │   WEBSOCKET     │  │   OPERATIONAL   │  │   CONFLICT      │                │
│  │   MANAGER       │  │   TRANSFORM     │  │   RESOLUTION    │                │
│  │                 │  │   ENGINE        │  │   ENGINE        │                │
│  │ • Connection    │  │ • Operation     │  │ • Conflict      │                │
│  │   Management    │  │   Tracking      │  │   Detection     │                │
│  │ • Message       │  │ • Transform     │  │ • Automatic     │                │
│  │   Routing       │  │   Algorithms    │  │   Resolution    │                │
│  │ • Authentication│  │ • State         │  │ • Manual        │                │
│  │ • Rate Limiting │  │   Synchronization│  │   Resolution    │                │
│  │ • Heartbeat     │  │ • Consistency   │  │ • Version       │                │
│  │   Monitoring    │  │   Guarantees    │  │   Management    │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │   USER          │  │   DOCUMENT      │  │   PERMISSION    │                │
│  │   PRESENCE      │  │   LOCKING       │  │   MANAGER       │                │
│  │   SYSTEM        │  │   SYSTEM        │  │                 │                │
│  │                 │  │                 │  │ • Role-based    │                │
│  │ • Online        │  │ • Granular      │  │   Access        │                │
│  │   Status        │  │   Locking       │  │ • Permission    │                │
│  │ • Cursor        │  │ • Lock          │  │   Inheritance   │                │
│  │   Tracking      │  │   Timeout       │  │ • Dynamic       │                │
│  │ • Activity      │  │ • Lock          │  │   Permissions   │                │
│  │   Indicators    │  │   Hierarchy     │  │ • Audit Trail   │                │
│  │ • User          │  │ • Deadlock      │  │ • Access        │                │
│  │   Avatars       │  │   Prevention    │  │   Control       │                │
│  │ • Typing        │  │ • Lock          │  │ • Resource      │                │
│  │   Indicators    │  │   Recovery      │  │   Protection    │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │   CHAT          │  │   COMMENT       │  │   NOTIFICATION  │                │
│  │   SYSTEM        │  │   SYSTEM        │  │   SYSTEM        │                │
│  │                 │  │                 │  │                 │                │
│  │ • Real-time     │  │ • Inline        │  │ • Real-time     │                │
│  │   Messaging     │  │   Comments      │  │   Notifications │                │
│  │ • Thread        │  │ • Comment       │  │ • Email         │                │
│  │   Management    │  │   Threads       │  │   Notifications │                │
│  │ • File          │  │ • Mention       │  │ • Push          │                │
│  │   Sharing       │  │   System        │  │   Notifications │                │
│  │ • Emoji         │  │ • Comment       │  │ • SMS           │                │
│  │   Reactions     │  │   Resolution    │  │   Notifications │                │
│  │ • Message       │  │ • Comment       │  │ • Webhook       │                │
│  │   History       │  │   Analytics     │  │   Integration   │                │
│  │ • Search        │  │ • Comment       │  │ • Notification  │                │
│  │   & Filter      │  │   Templates     │  │   Preferences   │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 2. Modelos de Datos de Colaboración

### 2.1 Estructuras de Colaboración

```python
# app/models/collaboration.py
from enum import Enum
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid
import json

class CollaborationRole(Enum):
    """Roles de colaboración"""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    VIEWER = "viewer"
    COMMENTOR = "commentor"

class OperationType(Enum):
    """Tipos de operaciones"""
    INSERT = "insert"
    DELETE = "delete"
    RETAIN = "retain"
    FORMAT = "format"
    MOVE = "move"
    COPY = "copy"
    PASTE = "paste"
    UNDO = "undo"
    REDO = "redo"

class ConflictResolutionStrategy(Enum):
    """Estrategias de resolución de conflictos"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MERGE = "merge"
    USER_CHOICE = "user_choice"

class LockType(Enum):
    """Tipos de bloqueo"""
    READ = "read"
    WRITE = "write"
    EXCLUSIVE = "exclusive"
    SHARED = "shared"
    INTENT_SHARED = "intent_shared"
    INTENT_EXCLUSIVE = "intent_exclusive"

@dataclass
class CollaborationSession:
    """Sesión de colaboración"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str = ""
    name: str = ""
    description: str = ""
    owner_id: str = ""
    participants: List[str] = field(default_factory=list)
    roles: Dict[str, CollaborationRole] = field(default_factory=dict)
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"  # active, paused, archived
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

@dataclass
class UserPresence:
    """Presencia de usuario"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    session_id: str = ""
    document_id: str = ""
    status: str = "online"  # online, away, busy, offline
    cursor_position: Optional[Dict[str, int]] = None
    selection_range: Optional[Dict[str, int]] = None
    last_activity: datetime = field(default_factory=datetime.now)
    typing: bool = False
    typing_text: str = ""
    avatar_url: Optional[str] = None
    display_name: str = ""
    color: str = "#007bff"

@dataclass
class DocumentOperation:
    """Operación en documento"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    user_id: str = ""
    document_id: str = ""
    operation_type: OperationType = OperationType.RETAIN
    position: int = 0
    length: int = 0
    content: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    vector_clock: Dict[str, int] = field(default_factory=dict)
    parent_operation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DocumentLock:
    """Bloqueo de documento"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str = ""
    user_id: str = ""
    lock_type: LockType = LockType.WRITE
    start_position: int = 0
    end_position: int = 0
    acquired_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(minutes=30))
    auto_renew: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConflictResolution:
    """Resolución de conflicto"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    document_id: str = ""
    operation1_id: str = ""
    operation2_id: str = ""
    conflict_type: str = ""
    resolution_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.AUTOMATIC
    resolved_operation: Optional[DocumentOperation] = None
    resolution_notes: str = ""
    resolved_by: str = ""
    resolved_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChatMessage:
    """Mensaje de chat"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    user_id: str = ""
    document_id: str = ""
    content: str = ""
    message_type: str = "text"  # text, file, image, emoji, system
    reply_to: Optional[str] = None
    thread_id: Optional[str] = None
    mentions: List[str] = field(default_factory=list)
    reactions: Dict[str, List[str]] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    edited: bool = False
    edited_at: Optional[datetime] = None
    deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Comment:
    """Comentario en documento"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str = ""
    user_id: str = ""
    content: str = ""
    position: int = 0
    selection_range: Optional[Dict[str, int]] = None
    thread_id: Optional[str] = None
    parent_comment_id: Optional[str] = None
    mentions: List[str] = field(default_factory=list)
    reactions: Dict[str, List[str]] = field(default_factory=dict)
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class Notification:
    """Notificación"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    type: str = ""  # mention, comment, edit, lock, conflict, system
    title: str = ""
    message: str = ""
    document_id: Optional[str] = None
    session_id: Optional[str] = None
    related_entity_id: Optional[str] = None
    priority: str = "normal"  # low, normal, high, urgent
    read: bool = False
    read_at: Optional[datetime] = None
    action_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

@dataclass
class CollaborationMetrics:
    """Métricas de colaboración"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    document_id: str = ""
    user_id: str = ""
    metric_name: str = ""
    metric_value: float = 0.0
    metric_unit: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

## 3. Motor de Colaboración en Tiempo Real

### 3.1 Clase Principal del Motor

```python
# app/services/collaboration/real_time_collaboration_engine.py
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union, Set, Tuple
from datetime import datetime, timedelta
import json
import hashlib
from collections import defaultdict, deque
from dataclasses import asdict

from ..models.collaboration import *
from ..core.database import get_database
from ..core.cache import get_cache
from ..core.websocket import WebSocketManager
from ..core.analytics import AnalyticsEngine

logger = logging.getLogger(__name__)

class RealTimeCollaborationEngine:
    """
    Motor de colaboración en tiempo real
    """
    
    def __init__(self):
        self.db = get_database()
        self.cache = get_cache()
        self.websocket_manager = WebSocketManager()
        self.analytics = AnalyticsEngine()
        
        # Estado de colaboración
        self.active_sessions = {}
        self.user_presence = {}
        self.document_locks = {}
        self.operation_queues = defaultdict(deque)
        self.conflict_resolutions = {}
        
        # Configuración
        self.config = {
            "max_operations_per_second": 100,
            "operation_timeout": 30,  # segundos
            "lock_timeout": 30,  # minutos
            "presence_timeout": 5,  # minutos
            "conflict_resolution_timeout": 60,  # segundos
            "max_concurrent_users": 50,
            "heartbeat_interval": 30,  # segundos
            "typing_indicator_timeout": 3  # segundos
        }
        
        # Inicializar WebSocket handlers
        self._initialize_websocket_handlers()
    
    async def create_collaboration_session(
        self,
        document_id: str,
        name: str,
        owner_id: str,
        description: str = "",
        participants: List[str] = None,
        settings: Dict[str, Any] = None
    ) -> str:
        """
        Crea una sesión de colaboración
        """
        try:
            logger.info(f"Creating collaboration session for document: {document_id}")
            
            # Crear sesión
            session = CollaborationSession(
                document_id=document_id,
                name=name,
                description=description,
                owner_id=owner_id,
                participants=participants or [],
                settings=settings or {}
            )
            
            # Configurar roles por defecto
            session.roles[owner_id] = CollaborationRole.OWNER
            for participant in session.participants:
                if participant != owner_id:
                    session.roles[participant] = CollaborationRole.EDITOR
            
            # Configurar permisos por defecto
            session.permissions = self._get_default_permissions(session.roles)
            
            # Guardar sesión
            session_id = await self._save_collaboration_session(session)
            session.id = session_id
            
            # Inicializar estado de sesión
            self.active_sessions[session_id] = {
                "session": session,
                "operations": deque(),
                "users": set(),
                "locks": {},
                "conflicts": []
            }
            
            # Registrar en analytics
            await self.analytics.record_collaboration_session_created(session)
            
            logger.info(f"Collaboration session created: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating collaboration session: {e}")
            raise
    
    async def join_collaboration_session(
        self,
        session_id: str,
        user_id: str,
        websocket_connection
    ) -> bool:
        """
        Une un usuario a una sesión de colaboración
        """
        try:
            logger.info(f"User {user_id} joining session {session_id}")
            
            # Verificar sesión
            if session_id not in self.active_sessions:
                raise ValueError("Session not found or not active")
            
            session_data = self.active_sessions[session_id]
            session = session_data["session"]
            
            # Verificar permisos
            if not await self._check_join_permissions(session, user_id):
                raise ValueError("Insufficient permissions to join session")
            
            # Crear presencia de usuario
            presence = UserPresence(
                user_id=user_id,
                session_id=session_id,
                document_id=session.document_id,
                status="online"
            )
            
            # Guardar presencia
            await self._save_user_presence(presence)
            self.user_presence[f"{session_id}:{user_id}"] = presence
            
            # Agregar usuario a sesión
            session_data["users"].add(user_id)
            
            # Registrar conexión WebSocket
            await self.websocket_manager.add_connection(
                connection_id=f"{session_id}:{user_id}",
                websocket=websocket_connection,
                user_id=user_id,
                session_id=session_id
            )
            
            # Notificar a otros usuarios
            await self._broadcast_user_joined(session_id, user_id, presence)
            
            # Enviar estado actual al usuario
            await self._send_session_state(websocket_connection, session_id, user_id)
            
            logger.info(f"User {user_id} joined session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error joining collaboration session: {e}")
            return False
    
    async def leave_collaboration_session(
        self,
        session_id: str,
        user_id: str
    ) -> bool:
        """
        Remueve un usuario de una sesión de colaboración
        """
        try:
            logger.info(f"User {user_id} leaving session {session_id}")
            
            # Verificar sesión
            if session_id not in self.active_sessions:
                return False
            
            session_data = self.active_sessions[session_id]
            
            # Remover usuario de sesión
            session_data["users"].discard(user_id)
            
            # Liberar bloqueos del usuario
            await self._release_user_locks(session_id, user_id)
            
            # Actualizar presencia
            presence_key = f"{session_id}:{user_id}"
            if presence_key in self.user_presence:
                presence = self.user_presence[presence_key]
                presence.status = "offline"
                presence.last_activity = datetime.now()
                await self._save_user_presence(presence)
                del self.user_presence[presence_key]
            
            # Remover conexión WebSocket
            await self.websocket_manager.remove_connection(f"{session_id}:{user_id}")
            
            # Notificar a otros usuarios
            await self._broadcast_user_left(session_id, user_id)
            
            # Limpiar sesión si está vacía
            if not session_data["users"]:
                await self._cleanup_empty_session(session_id)
            
            logger.info(f"User {user_id} left session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error leaving collaboration session: {e}")
            return False
    
    async def apply_operation(
        self,
        session_id: str,
        user_id: str,
        operation: DocumentOperation
    ) -> bool:
        """
        Aplica una operación en tiempo real
        """
        try:
            # Verificar sesión
            if session_id not in self.active_sessions:
                raise ValueError("Session not found")
            
            session_data = self.active_sessions[session_id]
            session = session_data["session"]
            
            # Verificar permisos
            if not await self._check_operation_permissions(session, user_id, operation):
                raise ValueError("Insufficient permissions for operation")
            
            # Verificar bloqueos
            if not await self._check_operation_locks(session_id, operation):
                raise ValueError("Operation conflicts with existing locks")
            
            # Transformar operación
            transformed_operation = await self._transform_operation(
                session_id, operation, session_data["operations"]
            )
            
            # Aplicar operación
            success = await self._apply_transformed_operation(
                session_id, transformed_operation
            )
            
            if success:
                # Agregar a cola de operaciones
                session_data["operations"].append(transformed_operation)
                
                # Limpiar cola antigua
                await self._cleanup_operation_queue(session_data["operations"])
                
                # Guardar operación
                await self._save_document_operation(transformed_operation)
                
                # Broadcast a otros usuarios
                await self._broadcast_operation(session_id, transformed_operation)
                
                # Actualizar métricas
                await self._update_collaboration_metrics(
                    session_id, user_id, "operation_applied", 1
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Error applying operation: {e}")
            return False
    
    async def acquire_lock(
        self,
        session_id: str,
        user_id: str,
        document_id: str,
        start_position: int,
        end_position: int,
        lock_type: LockType = LockType.WRITE
    ) -> Optional[str]:
        """
        Adquiere un bloqueo en el documento
        """
        try:
            # Verificar sesión
            if session_id not in self.active_sessions:
                raise ValueError("Session not found")
            
            session_data = self.active_sessions[session_id]
            session = session_data["session"]
            
            # Verificar permisos
            if not await self._check_lock_permissions(session, user_id, lock_type):
                raise ValueError("Insufficient permissions for lock")
            
            # Verificar conflictos de bloqueo
            if await self._check_lock_conflicts(
                session_id, start_position, end_position, lock_type
            ):
                raise ValueError("Lock conflicts with existing locks")
            
            # Crear bloqueo
            lock = DocumentLock(
                document_id=document_id,
                user_id=user_id,
                lock_type=lock_type,
                start_position=start_position,
                end_position=end_position
            )
            
            # Guardar bloqueo
            lock_id = await self._save_document_lock(lock)
            lock.id = lock_id
            
            # Agregar a estado de sesión
            session_data["locks"][lock_id] = lock
            
            # Notificar a otros usuarios
            await self._broadcast_lock_acquired(session_id, lock)
            
            # Programar expiración
            await self._schedule_lock_expiration(lock_id)
            
            logger.info(f"Lock acquired: {lock_id} by user {user_id}")
            return lock_id
            
        except Exception as e:
            logger.error(f"Error acquiring lock: {e}")
            return None
    
    async def release_lock(
        self,
        session_id: str,
        lock_id: str,
        user_id: str
    ) -> bool:
        """
        Libera un bloqueo
        """
        try:
            # Verificar sesión
            if session_id not in self.active_sessions:
                return False
            
            session_data = self.active_sessions[session_id]
            
            # Verificar bloqueo
            if lock_id not in session_data["locks"]:
                return False
            
            lock = session_data["locks"][lock_id]
            
            # Verificar permisos
            if lock.user_id != user_id:
                raise ValueError("Cannot release lock owned by another user")
            
            # Remover bloqueo
            del session_data["locks"][lock_id]
            
            # Marcar como liberado en base de datos
            await self._mark_lock_released(lock_id)
            
            # Notificar a otros usuarios
            await self._broadcast_lock_released(session_id, lock_id)
            
            logger.info(f"Lock released: {lock_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error releasing lock: {e}")
            return False
    
    async def send_chat_message(
        self,
        session_id: str,
        user_id: str,
        content: str,
        message_type: str = "text",
        reply_to: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> str:
        """
        Envía un mensaje de chat
        """
        try:
            # Crear mensaje
            message = ChatMessage(
                session_id=session_id,
                user_id=user_id,
                document_id=self.active_sessions[session_id]["session"].document_id,
                content=content,
                message_type=message_type,
                reply_to=reply_to,
                thread_id=thread_id
            )
            
            # Procesar menciones
            message.mentions = await self._extract_mentions(content)
            
            # Guardar mensaje
            message_id = await self._save_chat_message(message)
            message.id = message_id
            
            # Broadcast a usuarios de la sesión
            await self._broadcast_chat_message(session_id, message)
            
            # Enviar notificaciones de menciones
            await self._send_mention_notifications(message)
            
            logger.info(f"Chat message sent: {message_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Error sending chat message: {e}")
            raise
    
    async def add_comment(
        self,
        session_id: str,
        user_id: str,
        content: str,
        position: int,
        selection_range: Optional[Dict[str, int]] = None,
        parent_comment_id: Optional[str] = None
    ) -> str:
        """
        Agrega un comentario al documento
        """
        try:
            # Crear comentario
            comment = Comment(
                document_id=self.active_sessions[session_id]["session"].document_id,
                user_id=user_id,
                content=content,
                position=position,
                selection_range=selection_range,
                parent_comment_id=parent_comment_id
            )
            
            # Procesar menciones
            comment.mentions = await self._extract_mentions(content)
            
            # Guardar comentario
            comment_id = await self._save_comment(comment)
            comment.id = comment_id
            
            # Broadcast a usuarios de la sesión
            await self._broadcast_comment_added(session_id, comment)
            
            # Enviar notificaciones
            await self._send_comment_notifications(comment)
            
            logger.info(f"Comment added: {comment_id}")
            return comment_id
            
        except Exception as e:
            logger.error(f"Error adding comment: {e}")
            raise
    
    async def update_user_presence(
        self,
        session_id: str,
        user_id: str,
        status: str = None,
        cursor_position: Optional[Dict[str, int]] = None,
        selection_range: Optional[Dict[str, int]] = None,
        typing: bool = False,
        typing_text: str = ""
    ):
        """
        Actualiza presencia de usuario
        """
        try:
            presence_key = f"{session_id}:{user_id}"
            
            if presence_key not in self.user_presence:
                return
            
            presence = self.user_presence[presence_key]
            
            # Actualizar campos
            if status is not None:
                presence.status = status
            if cursor_position is not None:
                presence.cursor_position = cursor_position
            if selection_range is not None:
                presence.selection_range = selection_range
            if typing is not None:
                presence.typing = typing
            if typing_text is not None:
                presence.typing_text = typing_text
            
            presence.last_activity = datetime.now()
            
            # Guardar presencia
            await self._save_user_presence(presence)
            
            # Broadcast a otros usuarios
            await self._broadcast_presence_update(session_id, presence)
            
        except Exception as e:
            logger.error(f"Error updating user presence: {e}")
    
    # Métodos de transformación de operaciones
    async def _transform_operation(
        self,
        session_id: str,
        operation: DocumentOperation,
        operation_queue: deque
    ) -> DocumentOperation:
        """
        Transforma una operación contra operaciones concurrentes
        """
        transformed_operation = DocumentOperation(
            id=operation.id,
            session_id=operation.session_id,
            user_id=operation.user_id,
            document_id=operation.document_id,
            operation_type=operation.operation_type,
            position=operation.position,
            length=operation.length,
            content=operation.content,
            attributes=operation.attributes.copy(),
            timestamp=operation.timestamp,
            vector_clock=operation.vector_clock.copy(),
            parent_operation_id=operation.parent_operation_id,
            metadata=operation.metadata.copy()
        )
        
        # Aplicar transformaciones contra operaciones concurrentes
        for concurrent_op in operation_queue:
            if concurrent_op.id != operation.id and concurrent_op.timestamp < operation.timestamp:
                transformed_operation = await self._transform_against_operation(
                    transformed_operation, concurrent_op
                )
        
        return transformed_operation
    
    async def _transform_against_operation(
        self,
        op1: DocumentOperation,
        op2: DocumentOperation
    ) -> DocumentOperation:
        """
        Transforma op1 contra op2
        """
        # Implementar algoritmos de transformación operacional
        if op1.operation_type == OperationType.INSERT and op2.operation_type == OperationType.INSERT:
            return await self._transform_insert_insert(op1, op2)
        elif op1.operation_type == OperationType.INSERT and op2.operation_type == OperationType.DELETE:
            return await self._transform_insert_delete(op1, op2)
        elif op1.operation_type == OperationType.DELETE and op2.operation_type == OperationType.INSERT:
            return await self._transform_delete_insert(op1, op2)
        elif op1.operation_type == OperationType.DELETE and op2.operation_type == OperationType.DELETE:
            return await self._transform_delete_delete(op1, op2)
        else:
            return op1
    
    async def _transform_insert_insert(
        self,
        op1: DocumentOperation,
        op2: DocumentOperation
    ) -> DocumentOperation:
        """
        Transforma insert contra insert
        """
        if op2.position <= op1.position:
            op1.position += len(op2.content)
        return op1
    
    async def _transform_insert_delete(
        self,
        op1: DocumentOperation,
        op2: DocumentOperation
    ) -> DocumentOperation:
        """
        Transforma insert contra delete
        """
        if op2.position < op1.position:
            op1.position -= op2.length
        elif op2.position == op1.position:
            # Insert después del delete
            pass
        return op1
    
    async def _transform_delete_insert(
        self,
        op1: DocumentOperation,
        op2: DocumentOperation
    ) -> DocumentOperation:
        """
        Transforma delete contra insert
        """
        if op2.position <= op1.position:
            op1.position += len(op2.content)
        return op1
    
    async def _transform_delete_delete(
        self,
        op1: DocumentOperation,
        op2: DocumentOperation
    ) -> DocumentOperation:
        """
        Transforma delete contra delete
        """
        if op2.position < op1.position:
            if op2.position + op2.length <= op1.position:
                op1.position -= op2.length
            elif op2.position + op2.length <= op1.position + op1.length:
                # Overlap parcial
                overlap = op2.position + op2.length - op1.position
                op1.length -= overlap
                op1.position = op2.position
            else:
                # op2 contiene completamente a op1
                op1.length = 0
        elif op2.position == op1.position:
            if op2.length >= op1.length:
                op1.length = 0
            else:
                op1.length -= op2.length
        else:
            # op2.position > op1.position
            if op2.position < op1.position + op1.length:
                if op2.position + op2.length <= op1.position + op1.length:
                    # op2 está dentro de op1
                    op1.length -= op2.length
                else:
                    # Overlap parcial
                    overlap = op1.position + op1.length - op2.position
                    op1.length -= overlap
        
        return op1
    
    # Métodos de utilidad
    def _get_default_permissions(self, roles: Dict[str, CollaborationRole]) -> Dict[str, List[str]]:
        """
        Obtiene permisos por defecto según roles
        """
        permissions = {}
        
        for user_id, role in roles.items():
            if role == CollaborationRole.OWNER:
                permissions[user_id] = ["read", "write", "delete", "admin", "invite"]
            elif role == CollaborationRole.ADMIN:
                permissions[user_id] = ["read", "write", "delete", "admin"]
            elif role == CollaborationRole.EDITOR:
                permissions[user_id] = ["read", "write", "comment"]
            elif role == CollaborationRole.REVIEWER:
                permissions[user_id] = ["read", "comment", "approve"]
            elif role == CollaborationRole.COMMENTOR:
                permissions[user_id] = ["read", "comment"]
            else:  # VIEWER
                permissions[user_id] = ["read"]
        
        return permissions
    
    async def _check_join_permissions(self, session: CollaborationSession, user_id: str) -> bool:
        """
        Verifica permisos para unirse a la sesión
        """
        # El propietario siempre puede unirse
        if user_id == session.owner_id:
            return True
        
        # Verificar si el usuario está en la lista de participantes
        if user_id in session.participants:
            return True
        
        # Verificar si la sesión permite unirse libremente
        if session.settings.get("allow_public_join", False):
            return True
        
        return False
    
    async def _check_operation_permissions(
        self,
        session: CollaborationSession,
        user_id: str,
        operation: DocumentOperation
    ) -> bool:
        """
        Verifica permisos para operación
        """
        user_permissions = session.permissions.get(user_id, [])
        
        if operation.operation_type in [OperationType.INSERT, OperationType.DELETE, OperationType.FORMAT]:
            return "write" in user_permissions
        elif operation.operation_type == OperationType.RETAIN:
            return "read" in user_permissions
        
        return False
    
    async def _check_operation_locks(
        self,
        session_id: str,
        operation: DocumentOperation
    ) -> bool:
        """
        Verifica si la operación conflictúa con bloqueos existentes
        """
        session_data = self.active_sessions[session_id]
        
        for lock in session_data["locks"].values():
            if lock.user_id == operation.user_id:
                continue  # El usuario puede operar en sus propios bloqueos
            
            # Verificar overlap
            if self._ranges_overlap(
                operation.position, operation.position + operation.length,
                lock.start_position, lock.end_position
            ):
                if lock.lock_type in [LockType.WRITE, LockType.EXCLUSIVE]:
                    return False
        
        return True
    
    def _ranges_overlap(self, start1: int, end1: int, start2: int, end2: int) -> bool:
        """
        Verifica si dos rangos se superponen
        """
        return start1 < end2 and start2 < end1
    
    async def _extract_mentions(self, content: str) -> List[str]:
        """
        Extrae menciones del contenido
        """
        import re
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, content)
        return mentions
    
    # Métodos de persistencia
    async def _save_collaboration_session(self, session: CollaborationSession) -> str:
        """Guarda sesión de colaboración"""
        # Implementar guardado en base de datos
        pass
    
    async def _save_user_presence(self, presence: UserPresence):
        """Guarda presencia de usuario"""
        # Implementar guardado en base de datos
        pass
    
    async def _save_document_operation(self, operation: DocumentOperation):
        """Guarda operación de documento"""
        # Implementar guardado en base de datos
        pass
    
    async def _save_document_lock(self, lock: DocumentLock) -> str:
        """Guarda bloqueo de documento"""
        # Implementar guardado en base de datos
        pass
    
    async def _save_chat_message(self, message: ChatMessage) -> str:
        """Guarda mensaje de chat"""
        # Implementar guardado en base de datos
        pass
    
    async def _save_comment(self, comment: Comment) -> str:
        """Guarda comentario"""
        # Implementar guardado en base de datos
        pass
    
    # Métodos de WebSocket
    def _initialize_websocket_handlers(self):
        """Inicializa handlers de WebSocket"""
        # Implementar inicialización de handlers
        pass
    
    async def _broadcast_user_joined(self, session_id: str, user_id: str, presence: UserPresence):
        """Broadcast usuario unido"""
        # Implementar broadcast
        pass
    
    async def _broadcast_user_left(self, session_id: str, user_id: str):
        """Broadcast usuario salido"""
        # Implementar broadcast
        pass
    
    async def _broadcast_operation(self, session_id: str, operation: DocumentOperation):
        """Broadcast operación"""
        # Implementar broadcast
        pass
    
    async def _broadcast_lock_acquired(self, session_id: str, lock: DocumentLock):
        """Broadcast bloqueo adquirido"""
        # Implementar broadcast
        pass
    
    async def _broadcast_lock_released(self, session_id: str, lock_id: str):
        """Broadcast bloqueo liberado"""
        # Implementar broadcast
        pass
    
    async def _broadcast_chat_message(self, session_id: str, message: ChatMessage):
        """Broadcast mensaje de chat"""
        # Implementar broadcast
        pass
    
    async def _broadcast_comment_added(self, session_id: str, comment: Comment):
        """Broadcast comentario agregado"""
        # Implementar broadcast
        pass
    
    async def _broadcast_presence_update(self, session_id: str, presence: UserPresence):
        """Broadcast actualización de presencia"""
        # Implementar broadcast
        pass
    
    async def _send_session_state(self, websocket, session_id: str, user_id: str):
        """Envía estado de sesión"""
        # Implementar envío de estado
        pass
    
    # Métodos de limpieza
    async def _cleanup_operation_queue(self, operation_queue: deque):
        """Limpia cola de operaciones"""
        # Mantener solo las últimas 1000 operaciones
        while len(operation_queue) > 1000:
            operation_queue.popleft()
    
    async def _cleanup_empty_session(self, session_id: str):
        """Limpia sesión vacía"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    async def _release_user_locks(self, session_id: str, user_id: str):
        """Libera bloqueos del usuario"""
        session_data = self.active_sessions[session_id]
        locks_to_remove = []
        
        for lock_id, lock in session_data["locks"].items():
            if lock.user_id == user_id:
                locks_to_remove.append(lock_id)
        
        for lock_id in locks_to_remove:
            await self.release_lock(session_id, lock_id, user_id)
    
    async def _schedule_lock_expiration(self, lock_id: str):
        """Programa expiración de bloqueo"""
        # Implementar programación de expiración
        pass
    
    async def _mark_lock_released(self, lock_id: str):
        """Marca bloqueo como liberado"""
        # Implementar marcado de liberación
        pass
    
    async def _send_mention_notifications(self, message: ChatMessage):
        """Envía notificaciones de menciones"""
        # Implementar envío de notificaciones
        pass
    
    async def _send_comment_notifications(self, comment: Comment):
        """Envía notificaciones de comentarios"""
        # Implementar envío de notificaciones
        pass
    
    async def _update_collaboration_metrics(
        self,
        session_id: str,
        user_id: str,
        metric_name: str,
        metric_value: float
    ):
        """Actualiza métricas de colaboración"""
        # Implementar actualización de métricas
        pass
```

## 4. API Endpoints de Colaboración

### 4.1 Endpoints de Colaboración en Tiempo Real

```python
# app/api/collaboration_endpoints.py
from fastapi import APIRouter, HTTPException, Depends, Query, Body, WebSocket, WebSocketDisconnect
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from ..models.collaboration import CollaborationRole, OperationType, LockType
from ..services.collaboration.real_time_collaboration_engine import RealTimeCollaborationEngine
from ..core.security import get_current_user

router = APIRouter(prefix="/api/collaboration", tags=["Real-time Collaboration"])

class CollaborationSessionRequest(BaseModel):
    document_id: str
    name: str
    description: str = ""
    participants: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None

class JoinSessionRequest(BaseModel):
    session_id: str

class OperationRequest(BaseModel):
    session_id: str
    operation_type: str
    position: int
    length: int
    content: str = ""
    attributes: Optional[Dict[str, Any]] = None

class LockRequest(BaseModel):
    session_id: str
    start_position: int
    end_position: int
    lock_type: str = "write"

class ChatMessageRequest(BaseModel):
    session_id: str
    content: str
    message_type: str = "text"
    reply_to: Optional[str] = None
    thread_id: Optional[str] = None

class CommentRequest(BaseModel):
    session_id: str
    content: str
    position: int
    selection_range: Optional[Dict[str, int]] = None
    parent_comment_id: Optional[str] = None

@router.post("/sessions/create")
async def create_collaboration_session(
    request: CollaborationSessionRequest,
    current_user = Depends(get_current_user),
    engine: RealTimeCollaborationEngine = Depends()
):
    """
    Crea una sesión de colaboración
    """
    try:
        # Crear sesión
        session_id = await engine.create_collaboration_session(
            document_id=request.document_id,
            name=request.name,
            description=request.description,
            owner_id=current_user.id,
            participants=request.participants,
            settings=request.settings
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Collaboration session created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}")
async def get_collaboration_session(
    session_id: str,
    current_user = Depends(get_current_user),
    engine: RealTimeCollaborationEngine = Depends()
):
    """
    Obtiene información de una sesión de colaboración
    """
    try:
        # Obtener sesión
        session_data = engine.active_sessions.get(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = session_data["session"]
        
        return {
            "success": True,
            "session": {
                "id": session.id,
                "document_id": session.document_id,
                "name": session.name,
                "description": session.description,
                "owner_id": session.owner_id,
                "participants": session.participants,
                "roles": {k: v.value for k, v in session.roles.items()},
                "permissions": session.permissions,
                "settings": session.settings,
                "status": session.status,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "active_users": list(session_data["users"]),
                "active_locks": len(session_data["locks"])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/sessions/{session_id}/join")
async def join_collaboration_session_websocket(
    websocket: WebSocket,
    session_id: str,
    current_user = Depends(get_current_user),
    engine: RealTimeCollaborationEngine = Depends()
):
    """
    WebSocket para unirse a sesión de colaboración
    """
    try:
        # Aceptar conexión WebSocket
        await websocket.accept()
        
        # Unirse a sesión
        success = await engine.join_collaboration_session(
            session_id=session_id,
            user_id=current_user.id,
            websocket_connection=websocket
        )
        
        if not success:
            await websocket.close(code=4000, reason="Failed to join session")
            return
        
        try:
            # Mantener conexión activa
            while True:
                # Recibir mensajes del cliente
                data = await websocket.receive_json()
                message_type = data.get("type")
                
                if message_type == "operation":
                    # Aplicar operación
                    operation_data = data.get("operation", {})
                    operation = DocumentOperation(
                        session_id=session_id,
                        user_id=current_user.id,
                        document_id=operation_data.get("document_id"),
                        operation_type=OperationType(operation_data.get("operation_type")),
                        position=operation_data.get("position", 0),
                        length=operation_data.get("length", 0),
                        content=operation_data.get("content", ""),
                        attributes=operation_data.get("attributes", {})
                    )
                    
                    await engine.apply_operation(session_id, current_user.id, operation)
                
                elif message_type == "presence_update":
                    # Actualizar presencia
                    await engine.update_user_presence(
                        session_id=session_id,
                        user_id=current_user.id,
                        status=data.get("status"),
                        cursor_position=data.get("cursor_position"),
                        selection_range=data.get("selection_range"),
                        typing=data.get("typing", False),
                        typing_text=data.get("typing_text", "")
                    )
                
                elif message_type == "chat_message":
                    # Enviar mensaje de chat
                    await engine.send_chat_message(
                        session_id=session_id,
                        user_id=current_user.id,
                        content=data.get("content", ""),
                        message_type=data.get("message_type", "text"),
                        reply_to=data.get("reply_to"),
                        thread_id=data.get("thread_id")
                    )
                
                elif message_type == "acquire_lock":
                    # Adquirir bloqueo
                    await engine.acquire_lock(
                        session_id=session_id,
                        user_id=current_user.id,
                        document_id=data.get("document_id"),
                        start_position=data.get("start_position", 0),
                        end_position=data.get("end_position", 0),
                        lock_type=LockType(data.get("lock_type", "write"))
                    )
                
                elif message_type == "release_lock":
                    # Liberar bloqueo
                    await engine.release_lock(
                        session_id=session_id,
                        lock_id=data.get("lock_id"),
                        user_id=current_user.id
                    )
                
                elif message_type == "ping":
                    # Responder ping
                    await websocket.send_json({"type": "pong"})
        
        except WebSocketDisconnect:
            # Usuario desconectado
            await engine.leave_collaboration_session(session_id, current_user.id)
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=4000, reason="Internal error")

@router.post("/sessions/{session_id}/leave")
async def leave_collaboration_session(
    session_id: str,
    current_user = Depends(get_current_user),
    engine: RealTimeCollaborationEngine = Depends()
):
    """
    Sale de una sesión de colaboración
    """
    try:
        # Salir de sesión
        success = await engine.leave_collaboration_session(session_id, current_user.id)
        
        return {
            "success": success,
            "message": "Left collaboration session" if success else "Failed to leave session"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/operations/apply")
async def apply_operation(
    request: OperationRequest,
    current_user = Depends(get_current_user),
    engine: RealTimeCollaborationEngine = Depends()
):
    """
    Aplica una operación en tiempo real
    """
    try:
        # Crear operación
        operation = DocumentOperation(
            session_id=request.session_id,
            user_id=current_user.id,
            document_id="",  # Se obtendrá de la sesión
            operation_type=OperationType(request.operation_type),
            position=request.position,
            length=request.length,
            content=request.content,
            attributes=request.attributes or {}
        )
        
        # Aplicar operación
        success = await engine.apply_operation(
            session_id=request.session_id,
            user_id=current_user.id,
            operation=operation
        )
        
        return {
            "success": success,
            "message": "Operation applied" if success else "Failed to apply operation"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/locks/acquire")
async def acquire_lock(
    request: LockRequest,
    current_user = Depends(get_current_user),
    engine: RealTimeCollaborationEngine = Depends()
):
    """
    Adquiere un bloqueo en el documento
    """
    try:
        # Adquirir bloqueo
        lock_id = await engine.acquire_lock(
            session_id=request.session_id,
            user_id=current_user.id,
            document_id="",  # Se obtendrá de la sesión
            start_position=request.start_position,
            end_position=request.end_position,
            lock_type=LockType(request.lock_type)
        )
        
        if lock_id:
            return {
                "success": True,
                "lock_id": lock_id,
                "message": "Lock acquired successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to acquire lock"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/locks/{lock_id}/release")
async def release_lock(
    lock_id: str,
    session_id: str = Query(...),
    current_user = Depends(get_current_user),
    engine: RealTimeCollaborationEngine = Depends()
):
    """
    Libera un bloqueo
    """
    try:
        # Liberar bloqueo
        success = await engine.release_lock(
            session_id=session_id,
            lock_id=lock_id,
            user_id=current_user.id
        )
        
        return {
            "success": success,
            "message": "Lock released" if success else "Failed to release lock"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/send")
async def send_chat_message(
    request: ChatMessageRequest,
    current_user = Depends(get_current_user),
    engine: RealTimeCollaborationEngine = Depends()
):
    """
    Envía un mensaje de chat
    """
    try:
        # Enviar mensaje
        message_id = await engine.send_chat_message(
            session_id=request.session_id,
            user_id=current_user.id,
            content=request.content,
            message_type=request.message_type,
            reply_to=request.reply_to,
            thread_id=request.thread_id
        )
        
        return {
            "success": True,
            "message_id": message_id,
            "message": "Chat message sent successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comments/add")
async def add_comment(
    request: CommentRequest,
    current_user = Depends(get_current_user),
    engine: RealTimeCollaborationEngine = Depends()
):
    """
    Agrega un comentario al documento
    """
    try:
        # Agregar comentario
        comment_id = await engine.add_comment(
            session_id=request.session_id,
            user_id=current_user.id,
            content=request.content,
            position=request.position,
            selection_range=request.selection_range,
            parent_comment_id=request.parent_comment_id
        )
        
        return {
            "success": True,
            "comment_id": comment_id,
            "message": "Comment added successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def list_collaboration_sessions(
    current_user = Depends(get_current_user),
    engine: RealTimeCollaborationEngine = Depends()
):
    """
    Lista sesiones de colaboración del usuario
    """
    try:
        # Obtener sesiones del usuario
        user_sessions = []
        
        for session_id, session_data in engine.active_sessions.items():
            session = session_data["session"]
            
            # Verificar si el usuario tiene acceso
            if (current_user.id == session.owner_id or 
                current_user.id in session.participants or
                current_user.id in session.roles):
                
                user_sessions.append({
                    "id": session.id,
                    "document_id": session.document_id,
                    "name": session.name,
                    "description": session.description,
                    "owner_id": session.owner_id,
                    "status": session.status,
                    "active_users": len(session_data["users"]),
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat()
                })
        
        return {
            "success": True,
            "sessions": user_sessions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/presence")
async def get_session_presence(
    session_id: str,
    current_user = Depends(get_current_user),
    engine: RealTimeCollaborationEngine = Depends()
):
    """
    Obtiene presencia de usuarios en la sesión
    """
    try:
        # Verificar sesión
        if session_id not in engine.active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = engine.active_sessions[session_id]
        
        # Obtener presencia de usuarios
        presence_list = []
        for user_id in session_data["users"]:
            presence_key = f"{session_id}:{user_id}"
            if presence_key in engine.user_presence:
                presence = engine.user_presence[presence_key]
                presence_list.append({
                    "user_id": presence.user_id,
                    "status": presence.status,
                    "cursor_position": presence.cursor_position,
                    "selection_range": presence.selection_range,
                    "typing": presence.typing,
                    "typing_text": presence.typing_text,
                    "last_activity": presence.last_activity.isoformat(),
                    "display_name": presence.display_name,
                    "avatar_url": presence.avatar_url,
                    "color": presence.color
                })
        
        return {
            "success": True,
            "presence": presence_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 5. Conclusión

Las **Especificaciones de Colaboración en Tiempo Real** proporcionan:

### 👥 **Colaboración Avanzada**
- **Edición simultánea** de documentos por múltiples usuarios
- **Sincronización automática** de cambios en tiempo real
- **Control de versiones** y gestión de conflictos
- **Presencia de usuarios** con indicadores visuales

### 🔒 **Gestión de Acceso**
- **Roles y permisos** granulares
- **Sistema de bloqueos** para prevenir conflictos
- **Control de acceso** basado en roles
- **Auditoría completa** de actividades

### 💬 **Comunicación Integrada**
- **Chat en tiempo real** durante la colaboración
- **Sistema de comentarios** en documentos
- **Menciones y notificaciones** automáticas
- **Historial de conversaciones** y comentarios

### 🎯 **Beneficios del Sistema**
- **Productividad mejorada** con colaboración simultánea
- **Calidad superior** con revisión en tiempo real
- **Experiencia fluida** sin conflictos de edición
- **Comunicación eficiente** integrada en el flujo de trabajo

Este sistema de colaboración transforma la generación de documentos en una **experiencia colaborativa avanzada** que permite a equipos trabajar juntos de manera eficiente y sin fricciones.


















