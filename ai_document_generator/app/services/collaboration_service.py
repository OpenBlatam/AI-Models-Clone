"""
Collaboration service for real-time document collaboration
"""
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload
import uuid

from app.core.logging import get_logger
from app.core.exceptions import CollaborationError, NotFoundError, ConflictError
from app.models import (
    Document, Collaboration, CollaborationEvent, UserPresence, 
    ChatMessage, MessageReaction, User, DocumentVersion
)
from app.schemas.collaboration import (
    CollaborationCreate, CollaborationUpdate, CollaborationResponse,
    CollaborationEventCreate, CollaborationEventResponse,
    UserPresenceResponse, ChatMessageCreate, ChatMessageResponse,
    MessageReactionCreate, MessageReactionResponse,
    DocumentEdit, DocumentEditResult, CursorPosition, TextSelection,
    DocumentConflict, ConflictResolution, CollaborationStats,
    CollaborationHistory
)

logger = get_logger(__name__)


class CollaborationService:
    """Service for managing document collaboration."""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.document_states: Dict[str, Dict[str, Any]] = {}
        self.conflict_resolver = ConflictResolver()
    
    async def join_document(
        self, 
        db: AsyncSession, 
        document_id: str, 
        user_id: str, 
        role: str = "viewer"
    ) -> CollaborationResponse:
        """Join a document for collaboration."""
        try:
            # Check if document exists
            document = await self._get_document(db, document_id)
            if not document:
                raise NotFoundError("Document not found")
            
            # Check if user already has active collaboration
            existing_collaboration = await self._get_active_collaboration(
                db, document_id, user_id
            )
            
            if existing_collaboration:
                # Update existing collaboration
                existing_collaboration.role = role
                existing_collaboration.status = "active"
                existing_collaboration.joined_at = datetime.utcnow()
                existing_collaboration.last_activity = datetime.utcnow()
                await db.commit()
                await db.refresh(existing_collaboration)
                return CollaborationResponse.from_orm(existing_collaboration)
            
            # Create new collaboration
            collaboration = Collaboration(
                document_id=document_id,
                user_id=user_id,
                role=role,
                status="active",
                joined_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            
            db.add(collaboration)
            await db.commit()
            await db.refresh(collaboration)
            
            # Create user presence
            await self._create_user_presence(db, document_id, user_id)
            
            # Log collaboration event
            await self._log_collaboration_event(
                db, document_id, user_id, "user_joined", {"role": role}
            )
            
            logger.info(f"User {user_id} joined document {document_id} with role {role}")
            
            return CollaborationResponse.from_orm(collaboration)
        
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to join document: {e}")
            raise CollaborationError(f"Failed to join document: {str(e)}")
    
    async def leave_document(
        self, 
        db: AsyncSession, 
        document_id: str, 
        user_id: str
    ) -> None:
        """Leave document collaboration."""
        try:
            # Get active collaboration
            collaboration = await self._get_active_collaboration(
                db, document_id, user_id
            )
            
            if not collaboration:
                raise NotFoundError("Active collaboration not found")
            
            # Update collaboration status
            collaboration.status = "inactive"
            collaboration.left_at = datetime.utcnow()
            
            # Remove user presence
            await self._remove_user_presence(db, document_id, user_id)
            
            # Log collaboration event
            await self._log_collaboration_event(
                db, document_id, user_id, "user_left", {}
            )
            
            await db.commit()
            
            logger.info(f"User {user_id} left document {document_id}")
        
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to leave document: {e}")
            raise CollaborationError(f"Failed to leave document: {str(e)}")
    
    async def get_document_collaborators(
        self, 
        db: AsyncSession, 
        document_id: str
    ) -> List[CollaborationResponse]:
        """Get all collaborators for a document."""
        try:
            query = select(Collaboration).options(
                selectinload(Collaboration.user)
            ).where(
                and_(
                    Collaboration.document_id == document_id,
                    Collaboration.status == "active"
                )
            )
            
            result = await db.execute(query)
            collaborations = result.scalars().all()
            
            return [CollaborationResponse.from_orm(collab) for collab in collaborations]
        
        except Exception as e:
            logger.error(f"Failed to get document collaborators: {e}")
            raise CollaborationError(f"Failed to get document collaborators: {str(e)}")
    
    async def get_document_presence(
        self, 
        db: AsyncSession, 
        document_id: str
    ) -> List[UserPresenceResponse]:
        """Get current user presence for a document."""
        try:
            # Get active presence (last 5 minutes)
            cutoff_time = datetime.utcnow() - timedelta(minutes=5)
            
            query = select(UserPresence).options(
                selectinload(UserPresence.user)
            ).where(
                and_(
                    UserPresence.document_id == document_id,
                    UserPresence.last_seen >= cutoff_time
                )
            ).order_by(desc(UserPresence.last_seen))
            
            result = await db.execute(query)
            presence = result.scalars().all()
            
            return [UserPresenceResponse.from_orm(p) for p in presence]
        
        except Exception as e:
            logger.error(f"Failed to get document presence: {e}")
            raise CollaborationError(f"Failed to get document presence: {str(e)}")
    
    async def create_event(
        self, 
        db: AsyncSession, 
        document_id: str, 
        user_id: str, 
        event: CollaborationEventCreate
    ) -> CollaborationEventResponse:
        """Create a collaboration event."""
        try:
            collaboration_event = CollaborationEvent(
                document_id=document_id,
                user_id=user_id,
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
            await db.rollback()
            logger.error(f"Failed to create collaboration event: {e}")
            raise CollaborationError(f"Failed to create collaboration event: {str(e)}")
    
    async def get_document_events(
        self, 
        db: AsyncSession, 
        document_id: str, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[CollaborationEventResponse]:
        """Get collaboration events for a document."""
        try:
            query = select(CollaborationEvent).options(
                selectinload(CollaborationEvent.user)
            ).where(
                CollaborationEvent.document_id == document_id
            ).order_by(desc(CollaborationEvent.timestamp)).offset(offset).limit(limit)
            
            result = await db.execute(query)
            events = result.scalars().all()
            
            return [CollaborationEventResponse.from_orm(event) for event in events]
        
        except Exception as e:
            logger.error(f"Failed to get document events: {e}")
            raise CollaborationError(f"Failed to get document events: {str(e)}")
    
    async def create_chat_message(
        self, 
        db: AsyncSession, 
        document_id: str, 
        user_id: str, 
        message: ChatMessageCreate
    ) -> ChatMessageResponse:
        """Create a chat message."""
        try:
            chat_message = ChatMessage(
                document_id=document_id,
                author_id=user_id,
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
            await db.rollback()
            logger.error(f"Failed to create chat message: {e}")
            raise CollaborationError(f"Failed to create chat message: {str(e)}")
    
    async def get_chat_messages(
        self, 
        db: AsyncSession, 
        document_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[ChatMessageResponse]:
        """Get chat messages for a document."""
        try:
            query = select(ChatMessage).options(
                selectinload(ChatMessage.author),
                selectinload(ChatMessage.replies),
                selectinload(ChatMessage.reactions).selectinload(MessageReaction.user)
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
            logger.error(f"Failed to get chat messages: {e}")
            raise CollaborationError(f"Failed to get chat messages: {str(e)}")
    
    async def add_message_reaction(
        self, 
        db: AsyncSession, 
        message_id: str, 
        user_id: str, 
        reaction: MessageReactionCreate
    ) -> MessageReactionResponse:
        """Add a reaction to a chat message."""
        try:
            # Check if reaction already exists
            existing_reaction = await self._get_existing_reaction(
                db, message_id, user_id, reaction.emoji
            )
            
            if existing_reaction:
                # Update existing reaction
                existing_reaction.created_at = datetime.utcnow()
                await db.commit()
                await db.refresh(existing_reaction)
                return MessageReactionResponse.from_orm(existing_reaction)
            
            # Create new reaction
            message_reaction = MessageReaction(
                message_id=message_id,
                user_id=user_id,
                emoji=reaction.emoji,
                created_at=datetime.utcnow()
            )
            
            db.add(message_reaction)
            await db.commit()
            await db.refresh(message_reaction)
            
            return MessageReactionResponse.from_orm(message_reaction)
        
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to add message reaction: {e}")
            raise CollaborationError(f"Failed to add message reaction: {str(e)}")
    
    async def remove_message_reaction(
        self, 
        db: AsyncSession, 
        message_id: str, 
        reaction_id: str, 
        user_id: str
    ) -> None:
        """Remove a reaction from a chat message."""
        try:
            query = select(MessageReaction).where(
                and_(
                    MessageReaction.id == reaction_id,
                    MessageReaction.message_id == message_id,
                    MessageReaction.user_id == user_id
                )
            )
            
            result = await db.execute(query)
            reaction = result.scalar_one_or_none()
            
            if not reaction:
                raise NotFoundError("Reaction not found")
            
            await db.delete(reaction)
            await db.commit()
        
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to remove message reaction: {e}")
            raise CollaborationError(f"Failed to remove message reaction: {str(e)}")
    
    async def update_cursor_position(
        self, 
        document_id: str, 
        user_id: str, 
        position: Dict[str, Any]
    ) -> None:
        """Update user cursor position."""
        try:
            # Update in database
            query = select(UserPresence).where(
                and_(
                    UserPresence.document_id == document_id,
                    UserPresence.user_id == user_id
                )
            )
            
            result = await db.execute(query)
            presence = result.scalar_one_or_none()
            
            if presence:
                presence.cursor_position = position
                presence.last_seen = datetime.utcnow()
                await db.commit()
            
            # Update in memory for real-time updates
            if document_id not in self.active_sessions:
                self.active_sessions[document_id] = {}
            
            self.active_sessions[document_id][user_id] = {
                "cursor_position": position,
                "last_update": datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Failed to update cursor position: {e}")
            raise CollaborationError(f"Failed to update cursor position: {str(e)}")
    
    async def update_text_selection(
        self, 
        document_id: str, 
        user_id: str, 
        selection: Dict[str, Any]
    ) -> None:
        """Update user text selection."""
        try:
            # Update in database
            query = select(UserPresence).where(
                and_(
                    UserPresence.document_id == document_id,
                    UserPresence.user_id == user_id
                )
            )
            
            result = await db.execute(query)
            presence = result.scalar_one_or_none()
            
            if presence:
                presence.selected_text = selection.get("text")
                presence.last_seen = datetime.utcnow()
                await db.commit()
            
            # Update in memory for real-time updates
            if document_id not in self.active_sessions:
                self.active_sessions[document_id] = {}
            
            if user_id not in self.active_sessions[document_id]:
                self.active_sessions[document_id][user_id] = {}
            
            self.active_sessions[document_id][user_id]["selection"] = selection
            self.active_sessions[document_id][user_id]["last_update"] = datetime.utcnow()
        
        except Exception as e:
            logger.error(f"Failed to update text selection: {e}")
            raise CollaborationError(f"Failed to update text selection: {str(e)}")
    
    async def apply_document_edit(
        self, 
        document_id: str, 
        user_id: str, 
        edit: Dict[str, Any]
    ) -> DocumentEditResult:
        """Apply a document edit with conflict resolution."""
        try:
            # Check for conflicts
            conflicts = await self._check_edit_conflicts(
                document_id, user_id, edit
            )
            
            if conflicts:
                # Handle conflicts
                resolved_edit = await self.conflict_resolver.resolve_conflicts(
                    edit, conflicts
                )
            else:
                resolved_edit = edit
            
            # Apply the edit
            success = await self._apply_edit_to_document(
                document_id, resolved_edit
            )
            
            # Create edit result
            edit_result = DocumentEditResult(
                id=uuid.uuid4(),
                document_id=document_id,
                user_id=user_id,
                edit=DocumentEdit(**resolved_edit),
                applied=success,
                timestamp=datetime.utcnow()
            )
            
            # Log the edit
            await self._log_collaboration_event(
                db, document_id, user_id, "document_edit", {
                    "edit": resolved_edit,
                    "applied": success
                }
            )
            
            return edit_result
        
        except Exception as e:
            logger.error(f"Failed to apply document edit: {e}")
            raise CollaborationError(f"Failed to apply document edit: {str(e)}")
    
    async def get_document_conflicts(
        self, 
        db: AsyncSession, 
        document_id: str
    ) -> List[Dict[str, Any]]:
        """Get document conflicts that need resolution."""
        try:
            # This would typically query a conflicts table
            # For now, returning empty list
            return []
        
        except Exception as e:
            logger.error(f"Failed to get document conflicts: {e}")
            raise CollaborationError(f"Failed to get document conflicts: {str(e)}")
    
    async def resolve_conflict(
        self, 
        db: AsyncSession, 
        document_id: str, 
        conflict_id: str, 
        user_id: str, 
        resolution: Dict[str, Any]
    ) -> None:
        """Resolve a document conflict."""
        try:
            # This would typically update a conflicts table
            # For now, just logging the resolution
            await self._log_collaboration_event(
                db, document_id, user_id, "conflict_resolved", {
                    "conflict_id": conflict_id,
                    "resolution": resolution
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to resolve conflict: {e}")
            raise CollaborationError(f"Failed to resolve conflict: {str(e)}")
    
    async def get_collaboration_history(
        self, 
        db: AsyncSession, 
        document_id: str, 
        limit: int = 100, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get collaboration history for a document."""
        try:
            # Get events
            events = await self.get_document_events(db, document_id, limit, offset)
            
            # Get messages
            messages = await self.get_chat_messages(db, document_id, limit, offset)
            
            # Get stats
            stats = await self._get_collaboration_stats(db, document_id)
            
            return {
                "events": [event.dict() for event in events],
                "messages": [message.dict() for message in messages],
                "stats": stats.dict(),
                "period_start": datetime.utcnow() - timedelta(days=30),
                "period_end": datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Failed to get collaboration history: {e}")
            raise CollaborationError(f"Failed to get collaboration history: {str(e)}")
    
    async def get_document_state(self, document_id: str) -> Dict[str, Any]:
        """Get current document state."""
        try:
            if document_id in self.document_states:
                return self.document_states[document_id]
            
            # Return default state
            return {
                "content": "",
                "version": 1,
                "last_modified": datetime.utcnow().isoformat(),
                "collaborators": []
            }
        
        except Exception as e:
            logger.error(f"Failed to get document state: {e}")
            raise CollaborationError(f"Failed to get document state: {str(e)}")
    
    # Helper methods
    async def _get_document(self, db: AsyncSession, document_id: str) -> Optional[Document]:
        """Get document by ID."""
        query = select(Document).where(Document.id == document_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_active_collaboration(
        self, 
        db: AsyncSession, 
        document_id: str, 
        user_id: str
    ) -> Optional[Collaboration]:
        """Get active collaboration for user and document."""
        query = select(Collaboration).where(
            and_(
                Collaboration.document_id == document_id,
                Collaboration.user_id == user_id,
                Collaboration.status == "active"
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def _create_user_presence(
        self, 
        db: AsyncSession, 
        document_id: str, 
        user_id: str
    ) -> None:
        """Create user presence record."""
        presence = UserPresence(
            user_id=user_id,
            document_id=document_id,
            session_id=str(uuid.uuid4()),
            status="online",
            last_seen=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db.add(presence)
        await db.commit()
    
    async def _remove_user_presence(
        self, 
        db: AsyncSession, 
        document_id: str, 
        user_id: str
    ) -> None:
        """Remove user presence record."""
        query = select(UserPresence).where(
            and_(
                UserPresence.document_id == document_id,
                UserPresence.user_id == user_id
            )
        )
        result = await db.execute(query)
        presence = result.scalar_one_or_none()
        
        if presence:
            await db.delete(presence)
            await db.commit()
    
    async def _log_collaboration_event(
        self, 
        db: AsyncSession, 
        document_id: str, 
        user_id: str, 
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> None:
        """Log a collaboration event."""
        event = CollaborationEvent(
            document_id=document_id,
            user_id=user_id,
            event_type=event_type,
            event_data=event_data,
            timestamp=datetime.utcnow()
        )
        db.add(event)
        await db.commit()
    
    async def _get_existing_reaction(
        self, 
        db: AsyncSession, 
        message_id: str, 
        user_id: str, 
        emoji: str
    ) -> Optional[MessageReaction]:
        """Get existing reaction by user and emoji."""
        query = select(MessageReaction).where(
            and_(
                MessageReaction.message_id == message_id,
                MessageReaction.user_id == user_id,
                MessageReaction.emoji == emoji
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def _check_edit_conflicts(
        self, 
        document_id: str, 
        user_id: str, 
        edit: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for edit conflicts."""
        # Simplified conflict detection
        # In production, this would be more sophisticated
        return []
    
    async def _apply_edit_to_document(
        self, 
        document_id: str, 
        edit: Dict[str, Any]
    ) -> bool:
        """Apply edit to document."""
        # Simplified edit application
        # In production, this would update the actual document
        return True
    
    async def _get_collaboration_stats(
        self, 
        db: AsyncSession, 
        document_id: str
    ) -> CollaborationStats:
        """Get collaboration statistics."""
        # Simplified stats calculation
        # In production, this would query actual data
        return CollaborationStats(
            document_id=document_id,
            total_collaborators=0,
            active_collaborators=0,
            total_edits=0,
            total_messages=0,
            total_time=0.0,
            average_session_duration=0.0
        )


class ConflictResolver:
    """Service for resolving document edit conflicts."""
    
    async def resolve_conflicts(
        self, 
        edit: Dict[str, Any], 
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Resolve edit conflicts."""
        # Simplified conflict resolution
        # In production, this would implement sophisticated conflict resolution
        return edit


# Global collaboration service instance
collaboration_service = CollaborationService()




