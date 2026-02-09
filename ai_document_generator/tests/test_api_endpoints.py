"""
Tests for API endpoints
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
import json

from app.schemas.ai import AIProvider, AIModel


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncClient):
        """Test health check endpoint."""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    @pytest.mark.asyncio
    async def test_register_user(self, async_client: AsyncClient):
        """Test user registration."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "full_name": "New User"
        }
        
        response = await async_client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_login_user(self, async_client: AsyncClient, test_user):
        """Test user login."""
        login_data = {
            "email": test_user.email,
            "password": "secret"
        }
        
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401


class TestAIEndpoints:
    """Test AI endpoints."""
    
    @pytest.mark.asyncio
    async def test_generate_content(self, async_client: AsyncClient, auth_headers):
        """Test AI content generation."""
        with patch('app.services.ai_service.ai_service.generate_content') as mock_generate:
            mock_generate.return_value = AsyncMock(
                content="Generated content",
                provider=AIProvider.OPENAI,
                model=AIModel.GPT_4,
                usage={"tokens_used": 100},
                finish_reason="stop"
            )
            
            request_data = {
                "prompt": "Write a short story",
                "provider": "openai",
                "model": "gpt-4",
                "max_tokens": 100
            }
            
            response = await async_client.post(
                "/api/v1/ai/generate",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["content"] == "Generated content"
            assert data["provider"] == "openai"
    
    @pytest.mark.asyncio
    async def test_analyze_content(self, async_client: AsyncClient, auth_headers):
        """Test content analysis."""
        with patch('app.services.ai_service.ai_service.analyze_content') as mock_analyze:
            mock_analyze.return_value = AsyncMock(
                analysis_type="sentiment",
                results={"sentiment": 0.8, "confidence": 0.9},
                confidence=0.9,
                provider=AIProvider.OPENAI,
                model=AIModel.GPT_4
            )
            
            request_data = {
                "content": "This is a positive text",
                "analysis_type": "sentiment",
                "provider": "openai",
                "model": "gpt-4"
            }
            
            response = await async_client.post(
                "/api/v1/ai/analyze",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["analysis_type"] == "sentiment"
            assert data["results"]["sentiment"] == 0.8
    
    @pytest.mark.asyncio
    async def test_translate_content(self, async_client: AsyncClient, auth_headers):
        """Test content translation."""
        with patch('app.services.ai_service.ai_service.translate_content') as mock_translate:
            mock_translate.return_value = AsyncMock(
                original_content="Hello",
                translated_content="Hola",
                source_language="en",
                target_language="es",
                confidence=0.9,
                provider=AIProvider.OPENAI,
                model=AIModel.GPT_4
            )
            
            request_data = {
                "content": "Hello",
                "source_language": "en",
                "target_language": "es",
                "provider": "openai",
                "model": "gpt-4"
            }
            
            response = await async_client.post(
                "/api/v1/ai/translate",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["original_content"] == "Hello"
            assert data["translated_content"] == "Hola"
    
    @pytest.mark.asyncio
    async def test_summarize_content(self, async_client: AsyncClient, auth_headers):
        """Test content summarization."""
        with patch('app.services.ai_service.ai_service.summarize_content') as mock_summarize:
            mock_summarize.return_value = AsyncMock(
                original_content="Long content to summarize",
                summary="Short summary",
                summary_type="abstractive",
                compression_ratio=0.3,
                provider=AIProvider.OPENAI,
                model=AIModel.GPT_4
            )
            
            request_data = {
                "content": "Long content to summarize",
                "summary_type": "abstractive",
                "max_length": 100,
                "provider": "openai",
                "model": "gpt-4"
            }
            
            response = await async_client.post(
                "/api/v1/ai/summarize",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["original_content"] == "Long content to summarize"
            assert data["summary"] == "Short summary"
    
    @pytest.mark.asyncio
    async def test_improve_content(self, async_client: AsyncClient, auth_headers):
        """Test content improvement."""
        with patch('app.services.ai_service.ai_service.improve_content') as mock_improve:
            mock_improve.return_value = AsyncMock(
                original_content="Content to improve",
                improved_content="Improved content",
                improvement_type="grammar",
                changes=[{"type": "grammar_fix", "description": "Fixed grammar"}],
                confidence=0.8,
                provider=AIProvider.OPENAI,
                model=AIModel.GPT_4
            )
            
            request_data = {
                "content": "Content to improve",
                "improvement_type": "grammar",
                "provider": "openai",
                "model": "gpt-4"
            }
            
            response = await async_client.post(
                "/api/v1/ai/improve",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["original_content"] == "Content to improve"
            assert data["improved_content"] == "Improved content"
    
    @pytest.mark.asyncio
    async def test_generate_document(self, async_client: AsyncClient, auth_headers, test_organization):
        """Test document generation."""
        with patch('app.services.ai_service.ai_service.generate_content') as mock_generate, \
             patch('app.services.document_service.document_service.create_document') as mock_create:
            
            mock_generate.return_value = AsyncMock(
                content="Generated document content",
                provider=AIProvider.OPENAI,
                model=AIModel.GPT_4,
                usage={"tokens_used": 100},
                finish_reason="stop"
            )
            
            mock_create.return_value = AsyncMock(
                id="doc-id",
                title="Generated Document",
                content="Generated document content"
            )
            
            request_data = {
                "title": "Generated Document",
                "document_type": "report",
                "organization_id": str(test_organization.id),
                "ai_settings": {
                    "prompt": "Write a report about AI",
                    "provider": "openai",
                    "model": "gpt-4"
                }
            }
            
            response = await async_client.post(
                "/api/v1/ai/documents/generate",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "document" in data
            assert "generation" in data
    
    @pytest.mark.asyncio
    async def test_get_provider_status(self, async_client: AsyncClient, auth_headers):
        """Test getting AI provider status."""
        with patch('app.services.ai_service.ai_service.get_provider_status') as mock_status:
            mock_status.return_value = AsyncMock(
                provider=AIProvider.OPENAI,
                is_available=True,
                response_time=0.5,
                error_rate=0.0,
                last_check="2023-01-01T00:00:00Z"
            )
            
            response = await async_client.get(
                "/api/v1/ai/providers/openai/status",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["provider"] == "openai"
            assert data["is_available"] == True
    
    @pytest.mark.asyncio
    async def test_get_available_models(self, async_client: AsyncClient, auth_headers):
        """Test getting available AI models."""
        response = await async_client.get(
            "/api/v1/ai/models",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "openai" in data
        assert "anthropic" in data
        assert "deepseek" in data
        assert "google" in data
    
    @pytest.mark.asyncio
    async def test_get_usage_stats(self, async_client: AsyncClient, auth_headers):
        """Test getting AI usage statistics."""
        response = await async_client.get(
            "/api/v1/ai/usage/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "total_tokens" in data
        assert "total_cost" in data
        assert "by_provider" in data


class TestCollaborationEndpoints:
    """Test collaboration endpoints."""
    
    @pytest.mark.asyncio
    async def test_join_document_collaboration(
        self, 
        async_client: AsyncClient, 
        auth_headers, 
        test_document
    ):
        """Test joining document collaboration."""
        with patch('app.services.collaboration_service.collaboration_service.join_document') as mock_join:
            mock_join.return_value = AsyncMock(
                id="collab-id",
                document_id=str(test_document.id),
                user_id="user-id",
                role="editor",
                status="active"
            )
            
            response = await async_client.post(
                f"/api/v1/collaboration/documents/{test_document.id}/join",
                params={"role": "editor"},
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["document_id"] == str(test_document.id)
            assert data["role"] == "editor"
    
    @pytest.mark.asyncio
    async def test_leave_document_collaboration(
        self, 
        async_client: AsyncClient, 
        auth_headers, 
        test_document
    ):
        """Test leaving document collaboration."""
        with patch('app.services.collaboration_service.collaboration_service.leave_document') as mock_leave:
            mock_leave.return_value = AsyncMock()
            
            response = await async_client.post(
                f"/api/v1/collaboration/documents/{test_document.id}/leave",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Successfully left document collaboration"
    
    @pytest.mark.asyncio
    async def test_get_document_collaborators(
        self, 
        async_client: AsyncClient, 
        auth_headers, 
        test_document
    ):
        """Test getting document collaborators."""
        with patch('app.services.collaboration_service.collaboration_service.get_document_collaborators') as mock_get:
            mock_collaborator = AsyncMock(
                id="collab-id",
                document_id=str(test_document.id),
                user_id="user-id",
                role="editor",
                status="active"
            )
            mock_get.return_value = [mock_collaborator]
            
            response = await async_client.get(
                f"/api/v1/collaboration/documents/{test_document.id}/collaborators",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["role"] == "editor"
    
    @pytest.mark.asyncio
    async def test_create_chat_message(
        self, 
        async_client: AsyncClient, 
        auth_headers, 
        test_document
    ):
        """Test creating chat message."""
        with patch('app.services.collaboration_service.collaboration_service.create_chat_message') as mock_create, \
             patch('app.services.websocket_manager.websocket_manager.broadcast_to_document') as mock_broadcast:
            
            mock_create.return_value = AsyncMock(
                id="msg-id",
                document_id=str(test_document.id),
                author_id="user-id",
                content="Hello everyone!",
                message_type="text"
            )
            mock_broadcast.return_value = AsyncMock()
            
            message_data = {
                "content": "Hello everyone!",
                "message_type": "text"
            }
            
            response = await async_client.post(
                f"/api/v1/collaboration/documents/{test_document.id}/chat/messages",
                json=message_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["content"] == "Hello everyone!"
            assert data["message_type"] == "text"


class TestDocumentEndpoints:
    """Test document endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_document(
        self, 
        async_client: AsyncClient, 
        auth_headers, 
        test_organization
    ):
        """Test creating a document."""
        with patch('app.services.document_service.document_service.create_document') as mock_create:
            mock_create.return_value = AsyncMock(
                id="doc-id",
                title="New Document",
                content="Document content",
                organization_id=str(test_organization.id)
            )
            
            document_data = {
                "title": "New Document",
                "description": "A new document",
                "content": "Document content",
                "document_type": "text",
                "organization_id": str(test_organization.id)
            }
            
            response = await async_client.post(
                "/api/v1/documents",
                json=document_data,
                headers=auth_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "New Document"
            assert data["content"] == "Document content"
    
    @pytest.mark.asyncio
    async def test_get_document(
        self, 
        async_client: AsyncClient, 
        auth_headers, 
        test_document
    ):
        """Test getting a document."""
        with patch('app.services.document_service.document_service.get_document') as mock_get:
            mock_get.return_value = AsyncMock(
                id=str(test_document.id),
                title=test_document.title,
                content=test_document.content
            )
            
            response = await async_client.get(
                f"/api/v1/documents/{test_document.id}",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == str(test_document.id)
            assert data["title"] == test_document.title
    
    @pytest.mark.asyncio
    async def test_update_document(
        self, 
        async_client: AsyncClient, 
        auth_headers, 
        test_document
    ):
        """Test updating a document."""
        with patch('app.services.document_service.document_service.update_document') as mock_update:
            mock_update.return_value = AsyncMock(
                id=str(test_document.id),
                title="Updated Document",
                content="Updated content"
            )
            
            update_data = {
                "title": "Updated Document",
                "content": "Updated content"
            }
            
            response = await async_client.put(
                f"/api/v1/documents/{test_document.id}",
                json=update_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Updated Document"
            assert data["content"] == "Updated content"
    
    @pytest.mark.asyncio
    async def test_delete_document(
        self, 
        async_client: AsyncClient, 
        auth_headers, 
        test_document
    ):
        """Test deleting a document."""
        with patch('app.services.document_service.document_service.delete_document') as mock_delete:
            mock_delete.return_value = AsyncMock()
            
            response = await async_client.delete(
                f"/api/v1/documents/{test_document.id}",
                headers=auth_headers
            )
            
            assert response.status_code == 204


class TestUserEndpoints:
    """Test user endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, async_client: AsyncClient, auth_headers, test_user):
        """Test getting current user."""
        response = await async_client.get(
            "/api/v1/users/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
    
    @pytest.mark.asyncio
    async def test_update_user(self, async_client: AsyncClient, auth_headers, test_user):
        """Test updating user."""
        with patch('app.services.user_service.user_service.update_user') as mock_update:
            mock_update.return_value = AsyncMock(
                id=str(test_user.id),
                email=test_user.email,
                username=test_user.username,
                full_name="Updated Name"
            )
            
            update_data = {
                "full_name": "Updated Name"
            }
            
            response = await async_client.put(
                "/api/v1/users/me",
                json=update_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["full_name"] == "Updated Name"


class TestErrorHandling:
    """Test error handling."""
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, async_client: AsyncClient):
        """Test unauthorized access to protected endpoints."""
        response = await async_client.get("/api/v1/users/me")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_invalid_token(self, async_client: AsyncClient):
        """Test access with invalid token."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = await async_client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_not_found_endpoint(self, async_client: AsyncClient, auth_headers):
        """Test accessing non-existent endpoint."""
        response = await async_client.get(
            "/api/v1/nonexistent",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_validation_error(self, async_client: AsyncClient, auth_headers):
        """Test validation error handling."""
        invalid_data = {
            "prompt": "",  # Empty prompt should fail validation
            "provider": "invalid_provider"
        }
        
        response = await async_client.post(
            "/api/v1/ai/generate",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422




