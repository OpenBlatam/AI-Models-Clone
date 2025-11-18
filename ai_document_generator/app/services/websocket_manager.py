"""
WebSocket manager for real-time collaboration
"""
import json
import asyncio
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime, timedelta
import uuid

from app.core.logging import get_logger
from app.core.auth import decode_access_token
from app.schemas.user import User

logger = get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time collaboration."""
    
    def __init__(self):
        # Document rooms: {document_id: {user_id: websocket}}
        self.document_rooms: Dict[str, Dict[str, WebSocket]] = {}
        
        # User sessions: {user_id: {document_id: websocket}}
        self.user_sessions: Dict[str, Dict[str, WebSocket]] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Heartbeat tracking
        self.heartbeats: Dict[str, datetime] = {}
        
        # Message queues for offline users
        self.message_queues: Dict[str, List[Dict[str, Any]]] = {}
    
    async def connect(self, websocket: WebSocket, document_id: str, user_id: str) -> None:
        """Connect a user to a document room."""
        await websocket.accept()
        
        # Add to document room
        if document_id not in self.document_rooms:
            self.document_rooms[document_id] = {}
        
        self.document_rooms[document_id][user_id] = websocket
        
        # Add to user sessions
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}
        
        self.user_sessions[user_id][document_id] = websocket
        
        # Store connection metadata
        connection_id = f"{user_id}_{document_id}_{uuid.uuid4().hex[:8]}"
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "document_id": document_id,
            "connected_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        
        # Initialize heartbeat
        self.heartbeats[connection_id] = datetime.utcnow()
        
        logger.info(f"User {user_id} connected to document {document_id}")
        
        # Send queued messages if any
        await self._send_queued_messages(user_id, document_id)
    
    async def disconnect(self, document_id: str, user_id: str) -> None:
        """Disconnect a user from a document room."""
        # Remove from document room
        if document_id in self.document_rooms and user_id in self.document_rooms[document_id]:
            del self.document_rooms[document_id][user_id]
            
            # Clean up empty document room
            if not self.document_rooms[document_id]:
                del self.document_rooms[document_id]
        
        # Remove from user sessions
        if user_id in self.user_sessions and document_id in self.user_sessions[user_id]:
            del self.user_sessions[user_id][document_id]
            
            # Clean up empty user session
            if not self.user_sessions[user_id]:
                del self.user_sessions[user_id]
        
        # Clean up connection metadata
        connection_id = self._find_connection_id(user_id, document_id)
        if connection_id:
            del self.connection_metadata[connection_id]
            if connection_id in self.heartbeats:
                del self.heartbeats[connection_id]
        
        logger.info(f"User {user_id} disconnected from document {document_id}")
    
    async def send_personal_message(
        self, 
        message: Dict[str, Any], 
        user_id: str, 
        document_id: str
    ) -> bool:
        """Send a message to a specific user in a document room."""
        try:
            if (document_id in self.document_rooms and 
                user_id in self.document_rooms[document_id]):
                
                websocket = self.document_rooms[document_id][user_id]
                await websocket.send_text(json.dumps(message))
                return True
            else:
                # Queue message for offline user
                await self._queue_message(user_id, document_id, message)
                return False
        
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            return False
    
    async def broadcast_to_document(
        self, 
        document_id: str, 
        message: Dict[str, Any], 
        exclude_user: Optional[str] = None
    ) -> int:
        """Broadcast a message to all users in a document room."""
        sent_count = 0
        
        if document_id not in self.document_rooms:
            return sent_count
        
        # Add timestamp to message
        message["timestamp"] = datetime.utcnow().isoformat()
        
        # Send to all connected users except excluded user
        for user_id, websocket in self.document_rooms[document_id].items():
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await websocket.send_text(json.dumps(message))
                sent_count += 1
                
                # Update last activity
                connection_id = self._find_connection_id(user_id, document_id)
                if connection_id and connection_id in self.connection_metadata:
                    self.connection_metadata[connection_id]["last_activity"] = datetime.utcnow()
            
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
                # Remove failed connection
                await self.disconnect(document_id, user_id)
        
        return sent_count
    
    async def broadcast_to_user(
        self, 
        user_id: str, 
        message: Dict[str, Any]
    ) -> int:
        """Broadcast a message to all documents a user is connected to."""
        sent_count = 0
        
        if user_id not in self.user_sessions:
            return sent_count
        
        # Add timestamp to message
        message["timestamp"] = datetime.utcnow().isoformat()
        
        # Send to all connected documents
        for document_id, websocket in self.user_sessions[user_id].items():
            try:
                await websocket.send_text(json.dumps(message))
                sent_count += 1
                
                # Update last activity
                connection_id = self._find_connection_id(user_id, document_id)
                if connection_id and connection_id in self.connection_metadata:
                    self.connection_metadata[connection_id]["last_activity"] = datetime.utcnow()
            
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id} in document {document_id}: {e}")
                # Remove failed connection
                await self.disconnect(document_id, user_id)
        
        return sent_count
    
    async def get_document_users(self, document_id: str) -> List[str]:
        """Get list of connected users for a document."""
        if document_id in self.document_rooms:
            return list(self.document_rooms[document_id].keys())
        return []
    
    async def get_user_documents(self, user_id: str) -> List[str]:
        """Get list of documents a user is connected to."""
        if user_id in self.user_sessions:
            return list(self.user_sessions[user_id].keys())
        return []
    
    async def is_user_connected(self, user_id: str, document_id: str) -> bool:
        """Check if a user is connected to a document."""
        return (document_id in self.document_rooms and 
                user_id in self.document_rooms[document_id])
    
    async def get_connection_count(self, document_id: str) -> int:
        """Get number of connected users for a document."""
        if document_id in self.document_rooms:
            return len(self.document_rooms[document_id])
        return 0
    
    async def get_total_connections(self) -> int:
        """Get total number of active connections."""
        total = 0
        for document_room in self.document_rooms.values():
            total += len(document_room)
        return total
    
    async def update_heartbeat(self, user_id: str, document_id: str) -> None:
        """Update heartbeat for a connection."""
        connection_id = self._find_connection_id(user_id, document_id)
        if connection_id:
            self.heartbeats[connection_id] = datetime.utcnow()
    
    async def cleanup_stale_connections(self) -> None:
        """Clean up stale connections that haven't sent heartbeats."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        stale_connections = []
        
        for connection_id, last_heartbeat in self.heartbeats.items():
            if last_heartbeat < cutoff_time:
                stale_connections.append(connection_id)
        
        for connection_id in stale_connections:
            if connection_id in self.connection_metadata:
                metadata = self.connection_metadata[connection_id]
                user_id = metadata["user_id"]
                document_id = metadata["document_id"]
                
                await self.disconnect(document_id, user_id)
                logger.info(f"Cleaned up stale connection for user {user_id} in document {document_id}")
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            "total_connections": await self.get_total_connections(),
            "document_rooms": len(self.document_rooms),
            "active_users": len(self.user_sessions),
            "queued_messages": sum(len(queue) for queue in self.message_queues.values())
        }
    
    # Helper methods
    def _find_connection_id(self, user_id: str, document_id: str) -> Optional[str]:
        """Find connection ID for user and document."""
        for connection_id, metadata in self.connection_metadata.items():
            if (metadata["user_id"] == user_id and 
                metadata["document_id"] == document_id):
                return connection_id
        return None
    
    async def _queue_message(
        self, 
        user_id: str, 
        document_id: str, 
        message: Dict[str, Any]
    ) -> None:
        """Queue a message for an offline user."""
        queue_key = f"{user_id}_{document_id}"
        if queue_key not in self.message_queues:
            self.message_queues[queue_key] = []
        
        self.message_queues[queue_key].append(message)
        
        # Limit queue size
        if len(self.message_queues[queue_key]) > 100:
            self.message_queues[queue_key] = self.message_queues[queue_key][-100:]
    
    async def _send_queued_messages(self, user_id: str, document_id: str) -> None:
        """Send queued messages to a reconnected user."""
        queue_key = f"{user_id}_{document_id}"
        if queue_key in self.message_queues:
            messages = self.message_queues[queue_key]
            del self.message_queues[queue_key]
            
            for message in messages:
                await self.send_personal_message(message, user_id, document_id)


class WebSocketManager:
    """High-level WebSocket manager with authentication and business logic."""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.authenticated_users: Dict[str, User] = {}
    
    async def authenticate_user(self, token: str) -> Optional[User]:
        """Authenticate user from JWT token."""
        try:
            # Decode JWT token
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            
            if not user_id:
                return None
            
            # Get user from database (simplified)
            # In production, this would query the database
            user = User(
                id=user_id,
                email=payload.get("email", ""),
                username=payload.get("username", ""),
                is_active=True
            )
            
            self.authenticated_users[user_id] = user
            return user
        
        except Exception as e:
            logger.error(f"Failed to authenticate user: {e}")
            return None
    
    async def join_document(
        self, 
        document_id: str, 
        user_id: str, 
        websocket: WebSocket
    ) -> None:
        """Join a document for collaboration."""
        await self.connection_manager.connect(websocket, document_id, user_id)
        
        # Notify other users about new collaborator
        await self.connection_manager.broadcast_to_document(
            document_id, {
                "type": "user_joined",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_user=user_id
        )
    
    async def leave_document(self, document_id: str, user_id: str) -> None:
        """Leave a document collaboration."""
        await self.connection_manager.disconnect(document_id, user_id)
        
        # Notify other users about user leaving
        await self.connection_manager.broadcast_to_document(
            document_id, {
                "type": "user_left",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def broadcast_to_document(
        self, 
        document_id: str, 
        message: Dict[str, Any], 
        exclude_user: Optional[str] = None
    ) -> int:
        """Broadcast message to document room."""
        return await self.connection_manager.broadcast_to_document(
            document_id, message, exclude_user
        )
    
    async def send_to_user(
        self, 
        user_id: str, 
        message: Dict[str, Any]
    ) -> int:
        """Send message to specific user."""
        return await self.connection_manager.broadcast_to_user(user_id, message)
    
    async def get_document_users(self, document_id: str) -> List[str]:
        """Get users connected to document."""
        return await self.connection_manager.get_document_users(document_id)
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return await self.connection_manager.get_connection_stats()
    
    async def start_heartbeat_monitor(self) -> None:
        """Start background task to monitor heartbeats."""
        while True:
            try:
                await self.connection_manager.cleanup_stale_connections()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(60)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()




