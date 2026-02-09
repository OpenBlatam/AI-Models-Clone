"""
Collaboration endpoints for real-time document collaboration
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import json
import asyncio
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.exceptions import CollaborationError, NotFoundError
from app.schemas.user import User
from app.schemas.collaboration import (
    CollaborationCreate, CollaborationUpdate, CollaborationResponse,
    CollaborationEventCreate, CollaborationEventResponse,
    UserPresenceResponse, ChatMessageCreate, ChatMessageResponse,
    MessageReactionCreate, MessageReactionResponse
)
from app.services.collaboration_service import collaboration_service
from app.services.websocket_manager import websocket_manager

router = APIRouter()


@router.post("/documents/{document_id}/join", response_model=CollaborationResponse)
async def join_document_collaboration(
    document_id: str,
    role: str = "viewer",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CollaborationResponse:
    """Join a document for collaboration."""
    try:
        collaboration = await collaboration_service.join_document(
            db, document_id, current_user.id, role
        )
        return collaboration
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CollaborationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/documents/{document_id}/leave")
async def leave_document_collaboration(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Leave document collaboration."""
    try:
        await collaboration_service.leave_document(db, document_id, current_user.id)
        return {"message": "Successfully left document collaboration"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/documents/{document_id}/collaborators", response_model=List[CollaborationResponse])
async def get_document_collaborators(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[CollaborationResponse]:
    """Get all collaborators for a document."""
    try:
        collaborators = await collaboration_service.get_document_collaborators(
            db, document_id
        )
        return collaborators
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/documents/{document_id}/presence", response_model=List[UserPresenceResponse])
async def get_document_presence(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[UserPresenceResponse]:
    """Get current user presence for a document."""
    try:
        presence = await collaboration_service.get_document_presence(
            db, document_id
        )
        return presence
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/documents/{document_id}/events", response_model=CollaborationEventResponse)
async def create_collaboration_event(
    document_id: str,
    event: CollaborationEventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CollaborationEventResponse:
    """Create a collaboration event."""
    try:
        collaboration_event = await collaboration_service.create_event(
            db, document_id, current_user.id, event
        )
        
        # Broadcast event to all connected clients
        await websocket_manager.broadcast_to_document(
            document_id, {
                "type": "collaboration_event",
                "event": collaboration_event.dict()
            }
        )
        
        return collaboration_event
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CollaborationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/documents/{document_id}/events", response_model=List[CollaborationEventResponse])
async def get_document_events(
    document_id: str,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[CollaborationEventResponse]:
    """Get collaboration events for a document."""
    try:
        events = await collaboration_service.get_document_events(
            db, document_id, limit, offset
        )
        return events
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/documents/{document_id}/chat/messages", response_model=ChatMessageResponse)
async def create_chat_message(
    document_id: str,
    message: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ChatMessageResponse:
    """Create a chat message."""
    try:
        chat_message = await collaboration_service.create_chat_message(
            db, document_id, current_user.id, message
        )
        
        # Broadcast message to all connected clients
        await websocket_manager.broadcast_to_document(
            document_id, {
                "type": "chat_message",
                "message": chat_message.dict()
            }
        )
        
        return chat_message
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CollaborationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/documents/{document_id}/chat/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    document_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[ChatMessageResponse]:
    """Get chat messages for a document."""
    try:
        messages = await collaboration_service.get_chat_messages(
            db, document_id, limit, offset
        )
        return messages
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/messages/{message_id}/reactions", response_model=MessageReactionResponse)
async def add_message_reaction(
    message_id: str,
    reaction: MessageReactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> MessageReactionResponse:
    """Add a reaction to a chat message."""
    try:
        message_reaction = await collaboration_service.add_message_reaction(
            db, message_id, current_user.id, reaction
        )
        
        # Broadcast reaction to all connected clients
        await websocket_manager.broadcast_to_document(
            message_reaction.message.document_id, {
                "type": "message_reaction",
                "reaction": message_reaction.dict()
            }
        )
        
        return message_reaction
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CollaborationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/messages/{message_id}/reactions/{reaction_id}")
async def remove_message_reaction(
    message_id: str,
    reaction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Remove a reaction from a chat message."""
    try:
        await collaboration_service.remove_message_reaction(
            db, message_id, reaction_id, current_user.id
        )
        
        return {"message": "Reaction removed successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.websocket("/ws/documents/{document_id}")
async def websocket_collaboration(
    websocket: WebSocket,
    document_id: str,
    token: str
):
    """WebSocket endpoint for real-time collaboration."""
    await websocket.accept()
    
    try:
        # Authenticate user from token
        user = await websocket_manager.authenticate_user(token)
        if not user:
            await websocket.close(code=1008, reason="Authentication failed")
            return
        
        # Join the document room
        await websocket_manager.join_document(document_id, user.id, websocket)
        
        # Send current document state
        document_state = await collaboration_service.get_document_state(
            document_id
        )
        await websocket.send_text(json.dumps({
            "type": "document_state",
            "state": document_state
        }))
        
        # Send current presence
        presence = await collaboration_service.get_document_presence(document_id)
        await websocket.send_text(json.dumps({
            "type": "presence_update",
            "presence": [p.dict() for p in presence]
        }))
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await handle_websocket_message(
                    websocket, document_id, user.id, message
                )
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
    
    except Exception as e:
        await websocket.close(code=1011, reason="Internal server error")
    finally:
        # Leave the document room
        await websocket_manager.leave_document(document_id, user.id)


async def handle_websocket_message(
    websocket: WebSocket,
    document_id: str,
    user_id: str,
    message: Dict[str, Any]
):
    """Handle incoming WebSocket messages."""
    message_type = message.get("type")
    
    if message_type == "cursor_move":
        # Update cursor position
        await collaboration_service.update_cursor_position(
            document_id, user_id, message.get("position")
        )
        
        # Broadcast cursor update
        await websocket_manager.broadcast_to_document(
            document_id, {
                "type": "cursor_update",
                "user_id": user_id,
                "position": message.get("position")
            },
            exclude_user=user_id
        )
    
    elif message_type == "text_selection":
        # Update text selection
        await collaboration_service.update_text_selection(
            document_id, user_id, message.get("selection")
        )
        
        # Broadcast selection update
        await websocket_manager.broadcast_to_document(
            document_id, {
                "type": "selection_update",
                "user_id": user_id,
                "selection": message.get("selection")
            },
            exclude_user=user_id
        )
    
    elif message_type == "typing":
        # Broadcast typing indicator
        await websocket_manager.broadcast_to_document(
            document_id, {
                "type": "typing",
                "user_id": user_id,
                "is_typing": message.get("is_typing", True)
            },
            exclude_user=user_id
        )
    
    elif message_type == "document_edit":
        # Handle document edit
        edit_result = await collaboration_service.apply_document_edit(
            document_id, user_id, message.get("edit")
        )
        
        # Broadcast edit to all clients
        await websocket_manager.broadcast_to_document(
            document_id, {
                "type": "document_edit",
                "edit": edit_result.dict()
            }
        )
    
    elif message_type == "ping":
        # Respond to ping
        await websocket.send_text(json.dumps({
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    else:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        }))


@router.get("/documents/{document_id}/conflicts")
async def get_document_conflicts(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get document conflicts that need resolution."""
    try:
        conflicts = await collaboration_service.get_document_conflicts(
            db, document_id
        )
        return conflicts
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/documents/{document_id}/conflicts/{conflict_id}/resolve")
async def resolve_document_conflict(
    document_id: str,
    conflict_id: str,
    resolution: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Resolve a document conflict."""
    try:
        await collaboration_service.resolve_conflict(
            db, document_id, conflict_id, current_user.id, resolution
        )
        
        # Broadcast conflict resolution
        await websocket_manager.broadcast_to_document(
            document_id, {
                "type": "conflict_resolved",
                "conflict_id": conflict_id,
                "resolved_by": current_user.id
            }
        )
        
        return {"message": "Conflict resolved successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CollaborationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/documents/{document_id}/history")
async def get_document_collaboration_history(
    document_id: str,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get collaboration history for a document."""
    try:
        history = await collaboration_service.get_collaboration_history(
            db, document_id, limit, offset
        )
        return history
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")




