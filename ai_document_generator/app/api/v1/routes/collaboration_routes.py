"""
Collaboration routes following functional patterns and RORO
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import json
import asyncio
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.errors import handle_not_found_error, handle_conflict_error, handle_internal_error
from app.schemas.user import User
from app.schemas.collaboration import (
    CollaborationCreate, CollaborationResponse,
    CollaborationEventCreate, CollaborationEventResponse,
    UserPresenceResponse, ChatMessageCreate, ChatMessageResponse,
    MessageReactionCreate, MessageReactionResponse
)

router = APIRouter()


async def join_document_collaboration(
    document_id: str,
    user: User,
    role: str,
    db: AsyncSession
) -> CollaborationResponse:
    """Join a document for collaboration."""
    try:
        # Check if document exists
        from app.models.document import Document
        from sqlalchemy import select
        
        query = select(Document).where(Document.id == document_id)
        result = await db.execute(query)
        document = result.scalar_one_or_none()
        
        if not document:
            raise handle_not_found_error("Document", document_id)
        
        # Check if user already has active collaboration
        from app.models.collaboration import Collaboration
        
        collab_query = select(Collaboration).where(
            Collaboration.document_id == document_id,
            Collaboration.user_id == user.id,
            Collaboration.status == "active"
        )
        collab_result = await db.execute(collab_query)
        existing_collaboration = collab_result.scalar_one_or_none()
        
        if existing_collaboration:
            # Update existing collaboration
            existing_collaboration.role = role
            existing_collaboration.last_activity = datetime.utcnow()
            await db.commit()
            await db.refresh(existing_collaboration)
            return CollaborationResponse.from_orm(existing_collaboration)
        
        # Create new collaboration
        collaboration = Collaboration(
            document_id=document_id,
            user_id=user.id,
            role=role,
            status="active",
            joined_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        
        db.add(collaboration)
        await db.commit()
        await db.refresh(collaboration)
        
        return CollaborationResponse.from_orm(collaboration)
    
    except HTTPException:
        raise
    except Exception as e:
        raise handle_internal_error(f"Failed to join document: {str(e)}")


async def leave_document_collaboration(
    document_id: str,
    user: User,
    db: AsyncSession
) -> Dict[str, str]:
    """Leave document collaboration."""
    try:
        from app.models.collaboration import Collaboration
        from sqlalchemy import select
        
        # Get active collaboration
        query = select(Collaboration).where(
            Collaboration.document_id == document_id,
            Collaboration.user_id == user.id,
            Collaboration.status == "active"
        )
        result = await db.execute(query)
        collaboration = result.scalar_one_or_none()
        
        if not collaboration:
            raise handle_not_found_error("Active collaboration", f"{document_id}-{user.id}")
        
        # Update collaboration status
        collaboration.status = "inactive"
        collaboration.left_at = datetime.utcnow()
        await db.commit()
        
        return {"message": "Successfully left document collaboration"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise handle_internal_error(f"Failed to leave document: {str(e)}")


async def get_document_collaborators(
    document_id: str,
    user: User,
    db: AsyncSession
) -> List[CollaborationResponse]:
    """Get all collaborators for a document."""
    try:
        from app.models.collaboration import Collaboration
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        query = select(Collaboration).options(
            selectinload(Collaboration.user)
        ).where(
            Collaboration.document_id == document_id,
            Collaboration.status == "active"
        )
        
        result = await db.execute(query)
        collaborations = result.scalars().all()
        
        return [CollaborationResponse.from_orm(collab) for collab in collaborations]
    
    except Exception as e:
        raise handle_internal_error(f"Failed to get collaborators: {str(e)}")


async def get_document_presence(
    document_id: str,
    user: User,
    db: AsyncSession
) -> List[UserPresenceResponse]:
    """Get current user presence for a document."""
    try:
        from app.models.collaboration import UserPresence
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from datetime import timedelta
        
        # Get active presence (last 5 minutes)
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        
        query = select(UserPresence).options(
            selectinload(UserPresence.user)
        ).where(
            UserPresence.document_id == document_id,
            UserPresence.last_seen >= cutoff_time
        ).order_by(UserPresence.last_seen.desc())
        
        result = await db.execute(query)
        presence = result.scalars().all()
        
        return [UserPresenceResponse.from_orm(p) for p in presence]
    
    except Exception as e:
        raise handle_internal_error(f"Failed to get presence: {str(e)}")


async def create_collaboration_event(
    document_id: str,
    user: User,
    event: CollaborationEventCreate,
    db: AsyncSession
) -> CollaborationEventResponse:
    """Create a collaboration event."""
    try:
        from app.models.collaboration import CollaborationEvent
        
        collaboration_event = CollaborationEvent(
            document_id=document_id,
            user_id=user.id,
            session_id=event.session_id,
            event_type=event.event_type,
            event_data=event.event_data,
            position=event.position,
            timestamp=datetime.utcnow()
        )
        
        db.add(collaboration_event)
        await db.commit()
        await db.refresh(collaboration_event)
        
        return CollaborationEventResponse.from_orm(collaboration_event)
    
    except Exception as e:
        raise handle_internal_error(f"Failed to create event: {str(e)}")


async def create_chat_message(
    document_id: str,
    user: User,
    message: ChatMessageCreate,
    db: AsyncSession
) -> ChatMessageResponse:
    """Create a chat message."""
    try:
        from app.models.collaboration import ChatMessage
        
        chat_message = ChatMessage(
            document_id=document_id,
            author_id=user.id,
            parent_id=message.parent_id,
            content=message.content,
            message_type=message.message_type,
            metadata=message.metadata,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(chat_message)
        await db.commit()
        await db.refresh(chat_message)
        
        return ChatMessageResponse.from_orm(chat_message)
    
    except Exception as e:
        raise handle_internal_error(f"Failed to create message: {str(e)}")


async def get_chat_messages(
    document_id: str,
    user: User,
    limit: int,
    offset: int,
    db: AsyncSession
) -> List[ChatMessageResponse]:
    """Get chat messages for a document."""
    try:
        from app.models.collaboration import ChatMessage
        from sqlalchemy import select, and_, desc
        from sqlalchemy.orm import selectinload
        
        query = select(ChatMessage).options(
            selectinload(ChatMessage.author),
            selectinload(ChatMessage.replies),
            selectinload(ChatMessage.reactions)
        ).where(
            and_(
                ChatMessage.document_id == document_id,
                ChatMessage.is_deleted == False
            )
        ).order_by(desc(ChatMessage.created_at)).offset(offset).limit(limit)
        
        result = await db.execute(query)
        messages = result.scalars().all()
        
        return [ChatMessageResponse.from_orm(msg) for msg in messages]
    
    except Exception as e:
        raise handle_internal_error(f"Failed to get messages: {str(e)}")


async def add_message_reaction(
    message_id: str,
    user: User,
    reaction: MessageReactionCreate,
    db: AsyncSession
) -> MessageReactionResponse:
    """Add a reaction to a chat message."""
    try:
        from app.models.collaboration import MessageReaction
        from sqlalchemy import select, and_
        
        # Check if reaction already exists
        query = select(MessageReaction).where(
            and_(
                MessageReaction.message_id == message_id,
                MessageReaction.user_id == user.id,
                MessageReaction.emoji == reaction.emoji
            )
        )
        result = await db.execute(query)
        existing_reaction = result.scalar_one_or_none()
        
        if existing_reaction:
            # Update existing reaction
            existing_reaction.created_at = datetime.utcnow()
            await db.commit()
            await db.refresh(existing_reaction)
            return MessageReactionResponse.from_orm(existing_reaction)
        
        # Create new reaction
        message_reaction = MessageReaction(
            message_id=message_id,
            user_id=user.id,
            emoji=reaction.emoji,
            created_at=datetime.utcnow()
        )
        
        db.add(message_reaction)
        await db.commit()
        await db.refresh(message_reaction)
        
        return MessageReactionResponse.from_orm(message_reaction)
    
    except Exception as e:
        raise handle_internal_error(f"Failed to add reaction: {str(e)}")


async def handle_websocket_message(
    websocket: WebSocket,
    document_id: str,
    user_id: str,
    message: Dict[str, Any]
) -> None:
    """Handle incoming WebSocket messages."""
    message_type = message.get("type")
    
    if message_type == "cursor_move":
        # Update cursor position
        position = message.get("position")
        # In real implementation, this would update the database
        await websocket.send_text(json.dumps({
            "type": "cursor_update",
            "user_id": user_id,
            "position": position
        }))
    
    elif message_type == "typing":
        # Broadcast typing indicator
        await websocket.send_text(json.dumps({
            "type": "typing",
            "user_id": user_id,
            "is_typing": message.get("is_typing", True)
        }))
    
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


# Route definitions
@router.post("/documents/{document_id}/join", response_model=CollaborationResponse)
async def join_document(
    document_id: str,
    role: str = "viewer",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CollaborationResponse:
    """Join a document for collaboration."""
    return await join_document_collaboration(document_id, current_user, role, db)


@router.post("/documents/{document_id}/leave")
async def leave_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Leave document collaboration."""
    return await leave_document_collaboration(document_id, current_user, db)


@router.get("/documents/{document_id}/collaborators", response_model=List[CollaborationResponse])
async def get_document_collaborators_endpoint(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[CollaborationResponse]:
    """Get all collaborators for a document."""
    return await get_document_collaborators(document_id, current_user, db)


@router.get("/documents/{document_id}/presence", response_model=List[UserPresenceResponse])
async def get_document_presence_endpoint(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[UserPresenceResponse]:
    """Get current user presence for a document."""
    return await get_document_presence(document_id, current_user, db)


@router.post("/documents/{document_id}/events", response_model=CollaborationEventResponse)
async def create_collaboration_event_endpoint(
    document_id: str,
    event: CollaborationEventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CollaborationEventResponse:
    """Create a collaboration event."""
    return await create_collaboration_event(document_id, current_user, event, db)


@router.post("/documents/{document_id}/chat/messages", response_model=ChatMessageResponse)
async def create_chat_message_endpoint(
    document_id: str,
    message: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ChatMessageResponse:
    """Create a chat message."""
    return await create_chat_message(document_id, current_user, message, db)


@router.get("/documents/{document_id}/chat/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages_endpoint(
    document_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[ChatMessageResponse]:
    """Get chat messages for a document."""
    return await get_chat_messages(document_id, current_user, limit, offset, db)


@router.post("/messages/{message_id}/reactions", response_model=MessageReactionResponse)
async def add_message_reaction_endpoint(
    message_id: str,
    reaction: MessageReactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> MessageReactionResponse:
    """Add a reaction to a chat message."""
    return await add_message_reaction(message_id, current_user, reaction, db)


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
        from app.core.auth_utils import decode_token, get_user_by_id
        
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=1008, reason="Authentication failed")
            return
        
        # Get user from database
        from app.core.database import get_db
        async for db in get_db():
            user = await get_user_by_id(db, user_id)
            if not user:
                await websocket.close(code=1008, reason="User not found")
                return
            break
        
        # Send current document state
        await websocket.send_text(json.dumps({
            "type": "document_state",
            "state": {"content": "", "version": 1}
        }))
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await handle_websocket_message(
                    websocket, document_id, user_id, message
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




