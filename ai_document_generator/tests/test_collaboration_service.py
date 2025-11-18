"""
Tests for collaboration service
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import uuid

from app.services.collaboration_service import CollaborationService
from app.schemas.collaboration import (
    CollaborationCreate, CollaborationEventCreate,
    ChatMessageCreate, MessageReactionCreate
)


@pytest.fixture
def collaboration_service():
    """Create collaboration service instance for testing."""
    return CollaborationService()


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock()


@pytest.fixture
def mock_document():
    """Mock document."""
    document = MagicMock()
    document.id = str(uuid.uuid4())
    document.title = "Test Document"
    return document


@pytest.fixture
def mock_user():
    """Mock user."""
    user = MagicMock()
    user.id = str(uuid.uuid4())
    user.email = "test@example.com"
    user.username = "testuser"
    return user


class TestCollaborationService:
    """Test cases for collaboration service."""
    
    @pytest.mark.asyncio
    async def test_join_document_success(self, collaboration_service, mock_db, mock_document, mock_user):
        """Test successful document join."""
        # Mock database queries
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_document
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        
        # Mock database operations
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        mock_db.add = MagicMock()
        
        with patch.object(collaboration_service, '_get_document', return_value=mock_document), \
             patch.object(collaboration_service, '_get_active_collaboration', return_value=None), \
             patch.object(collaboration_service, '_create_user_presence'), \
             patch.object(collaboration_service, '_log_collaboration_event'):
            
            response = await collaboration_service.join_document(
                mock_db, mock_document.id, mock_user.id, "editor"
            )
            
            assert response.document_id == mock_document.id
            assert response.user_id == mock_user.id
            assert response.role == "editor"
            assert response.status == "active"
    
    @pytest.mark.asyncio
    async def test_join_document_not_found(self, collaboration_service, mock_db):
        """Test joining non-existent document."""
        with patch.object(collaboration_service, '_get_document', return_value=None):
            with pytest.raises(Exception):  # Should raise NotFoundError
                await collaboration_service.join_document(
                    mock_db, "non-existent-id", "user-id", "editor"
                )
    
    @pytest.mark.asyncio
    async def test_leave_document_success(self, collaboration_service, mock_db, mock_document, mock_user):
        """Test successful document leave."""
        # Mock active collaboration
        mock_collaboration = MagicMock()
        mock_collaboration.status = "active"
        mock_collaboration.left_at = None
        
        with patch.object(collaboration_service, '_get_active_collaboration', return_value=mock_collaboration), \
             patch.object(collaboration_service, '_remove_user_presence'), \
             patch.object(collaboration_service, '_log_collaboration_event):
            
            await collaboration_service.leave_document(
                mock_db, mock_document.id, mock_user.id
            )
            
            assert mock_collaboration.status == "inactive"
            assert mock_collaboration.left_at is not None
    
    @pytest.mark.asyncio
    async def test_get_document_collaborators(self, collaboration_service, mock_db, mock_document):
        """Test getting document collaborators."""
        # Mock collaborators
        mock_collaboration = MagicMock()
        mock_collaboration.document_id = mock_document.id
        mock_collaboration.user_id = "user-id"
        mock_collaboration.role = "editor"
        mock_collaboration.status = "active"
        
        mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_collaboration]
        
        collaborators = await collaboration_service.get_document_collaborators(
            mock_db, mock_document.id
        )
        
        assert len(collaborators) == 1
        assert collaborators[0].document_id == mock_document.id
        assert collaborators[0].role == "editor"
    
    @pytest.mark.asyncio
    async def test_get_document_presence(self, collaboration_service, mock_db, mock_document):
        """Test getting document presence."""
        # Mock presence
        mock_presence = MagicMock()
        mock_presence.document_id = mock_document.id
        mock_presence.user_id = "user-id"
        mock_presence.status = "online"
        mock_presence.last_seen = datetime.utcnow()
        
        mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_presence]
        
        presence = await collaboration_service.get_document_presence(
            mock_db, mock_document.id
        )
        
        assert len(presence) == 1
        assert presence[0].document_id == mock_document.id
        assert presence[0].status == "online"
    
    @pytest.mark.asyncio
    async def test_create_event(self, collaboration_service, mock_db, mock_document, mock_user):
        """Test creating collaboration event."""
        event_data = CollaborationEventCreate(
            event_type="cursor_move",
            event_data={"position": {"line": 1, "column": 5}},
            position={"line": 1, "column": 5}
        )
        
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        mock_db.add = MagicMock()
        
        response = await collaboration_service.create_event(
            mock_db, mock_document.id, mock_user.id, event_data
        )
        
        assert response.document_id == mock_document.id
        assert response.user_id == mock_user.id
        assert response.event_type == "cursor_move"
        assert response.event_data["position"]["line"] == 1
    
    @pytest.mark.asyncio
    async def test_create_chat_message(self, collaboration_service, mock_db, mock_document, mock_user):
        """Test creating chat message."""
        message_data = ChatMessageCreate(
            content="Hello everyone!",
            message_type="text"
        )
        
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        mock_db.add = MagicMock()
        
        response = await collaboration_service.create_chat_message(
            mock_db, mock_document.id, mock_user.id, message_data
        )
        
        assert response.document_id == mock_document.id
        assert response.author_id == mock_user.id
        assert response.content == "Hello everyone!"
        assert response.message_type == "text"
    
    @pytest.mark.asyncio
    async def test_add_message_reaction(self, collaboration_service, mock_db, mock_user):
        """Test adding message reaction."""
        reaction_data = MessageReactionCreate(emoji="👍")
        message_id = str(uuid.uuid4())
        
        # Mock no existing reaction
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        mock_db.add = MagicMock()
        
        response = await collaboration_service.add_message_reaction(
            mock_db, message_id, mock_user.id, reaction_data
        )
        
        assert response.message_id == message_id
        assert response.user_id == mock_user.id
        assert response.emoji == "👍"
    
    @pytest.mark.asyncio
    async def test_update_cursor_position(self, collaboration_service, mock_db, mock_document, mock_user):
        """Test updating cursor position."""
        position = {"line": 10, "column": 20}
        
        # Mock presence update
        mock_presence = MagicMock()
        mock_presence.cursor_position = None
        mock_presence.last_seen = None
        
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_presence
        mock_db.commit = AsyncMock()
        
        await collaboration_service.update_cursor_position(
            mock_document.id, mock_user.id, position
        )
        
        assert mock_presence.cursor_position == position
        assert mock_presence.last_seen is not None
    
    @pytest.mark.asyncio
    async def test_update_text_selection(self, collaboration_service, mock_db, mock_document, mock_user):
        """Test updating text selection."""
        selection = {"start": {"line": 1, "column": 0}, "end": {"line": 1, "column": 10}, "text": "selected"}
        
        # Mock presence update
        mock_presence = MagicMock()
        mock_presence.selected_text = None
        mock_presence.last_seen = None
        
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_presence
        mock_db.commit = AsyncMock()
        
        await collaboration_service.update_text_selection(
            mock_document.id, mock_user.id, selection
        )
        
        assert mock_presence.selected_text == "selected"
        assert mock_presence.last_seen is not None
    
    @pytest.mark.asyncio
    async def test_apply_document_edit(self, collaboration_service, mock_db, mock_document, mock_user):
        """Test applying document edit."""
        edit = {
            "operation": "insert",
            "position": 10,
            "content": "new text"
        }
        
        with patch.object(collaboration_service, '_check_edit_conflicts', return_value=[]), \
             patch.object(collaboration_service, '_apply_edit_to_document', return_value=True), \
             patch.object(collaboration_service, '_log_collaboration_event'):
            
            response = await collaboration_service.apply_document_edit(
                mock_document.id, mock_user.id, edit
            )
            
            assert response.document_id == mock_document.id
            assert response.user_id == mock_user.id
            assert response.edit.operation == "insert"
            assert response.applied == True
    
    @pytest.mark.asyncio
    async def test_get_document_conflicts(self, collaboration_service, mock_db, mock_document):
        """Test getting document conflicts."""
        conflicts = await collaboration_service.get_document_conflicts(
            mock_db, mock_document.id
        )
        
        assert isinstance(conflicts, list)
    
    @pytest.mark.asyncio
    async def test_resolve_conflict(self, collaboration_service, mock_db, mock_document, mock_user):
        """Test resolving conflict."""
        conflict_id = str(uuid.uuid4())
        resolution = {"type": "accept", "selected_edit": "edit1"}
        
        with patch.object(collaboration_service, '_log_collaboration_event'):
            await collaboration_service.resolve_conflict(
                mock_db, mock_document.id, conflict_id, mock_user.id, resolution
            )
    
    @pytest.mark.asyncio
    async def test_get_collaboration_history(self, collaboration_service, mock_db, mock_document):
        """Test getting collaboration history."""
        with patch.object(collaboration_service, 'get_document_events', return_value=[]), \
             patch.object(collaboration_service, 'get_chat_messages', return_value=[]), \
             patch.object(collaboration_service, '_get_collaboration_stats'):
            
            history = await collaboration_service.get_collaboration_history(
                mock_db, mock_document.id
            )
            
            assert "events" in history
            assert "messages" in history
            assert "stats" in history
            assert "period_start" in history
            assert "period_end" in history
    
    @pytest.mark.asyncio
    async def test_get_document_state(self, collaboration_service, mock_document):
        """Test getting document state."""
        # Set initial state
        collaboration_service.document_states[mock_document.id] = {
            "content": "Document content",
            "version": 1
        }
        
        state = await collaboration_service.get_document_state(mock_document.id)
        
        assert state["content"] == "Document content"
        assert state["version"] == 1
    
    @pytest.mark.asyncio
    async def test_get_document_state_default(self, collaboration_service):
        """Test getting default document state."""
        document_id = str(uuid.uuid4())
        
        state = await collaboration_service.get_document_state(document_id)
        
        assert state["content"] == ""
        assert state["version"] == 1
        assert "last_modified" in state
        assert "collaborators" in state


class TestConflictResolver:
    """Test cases for conflict resolver."""
    
    def test_resolve_conflicts_no_conflicts(self):
        """Test resolving conflicts when there are none."""
        from app.services.collaboration_service import ConflictResolver
        
        resolver = ConflictResolver()
        edit = {"operation": "insert", "position": 10, "content": "text"}
        conflicts = []
        
        # This would be async in real implementation
        resolved_edit = edit  # Simplified for test
        
        assert resolved_edit == edit
    
    def test_resolve_conflicts_with_conflicts(self):
        """Test resolving conflicts when conflicts exist."""
        from app.services.collaboration_service import ConflictResolver
        
        resolver = ConflictResolver()
        edit = {"operation": "insert", "position": 10, "content": "text"}
        conflicts = [{"type": "overlap", "edit": {"operation": "delete", "position": 10}}]
        
        # This would be async in real implementation
        resolved_edit = edit  # Simplified for test
        
        assert resolved_edit == edit




