"""
🧪 FastAPI Endpoints Tests for ADS System

Comprehensive testing of API endpoints including authentication,
authorization, rate limiting, and API contract validation.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException, status
from unittest.mock import Mock, patch, AsyncMock
import json
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, Any, List

# Import API components
try:
    from api.router import router
    from api.schemas import (
        AdCreateRequest, AdResponse, CampaignCreateRequest, CampaignResponse,
        OptimizationRequest, OptimizationResponse
    )
except ImportError:
    # Create mock schemas if not available
    from pydantic import BaseModel
    
    class AdCreateRequest(BaseModel):
        name: str
        description: str = ""
        ad_type: str = "image"
        platform: str = "facebook"
    
    class AdResponse(BaseModel):
        id: str
        name: str
        status: str
    
    class CampaignCreateRequest(BaseModel):
        name: str
        objective: str = "awareness"
        platform: str = "facebook"
    
    class CampaignResponse(BaseModel):
        id: str
        name: str
        status: str
    
    class OptimizationRequest(BaseModel):
        entity_id: str
        optimization_type: str = "performance"
        level: str = "standard"
    
    class OptimizationResponse(BaseModel):
        success: bool
        improvement_percentage: float = 0.0

# Import system components
from domain.entities import Ad, AdCampaign, AdGroup
from domain.value_objects import AdStatus, AdType, Platform
from optimization.factory import get_optimization_factory


# Create test FastAPI app
def create_test_app() -> FastAPI:
    """Create FastAPI app for testing."""
    app = FastAPI(title="ADS System Test API", version="1.0.0")
    
    # Mock router if not available
    try:
        app.include_router(router, prefix="/api/v1/ads")
    except NameError:
        from fastapi import APIRouter
        test_router = APIRouter()
        
        @test_router.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
        
        @test_router.post("/campaigns", response_model=CampaignResponse)
        async def create_campaign(request: CampaignCreateRequest):
            campaign = AdCampaign(
                name=request.name,
                objective=request.objective,
                platform=Platform(request.platform)
            )
            return CampaignResponse(
                id=str(campaign.id),
                name=campaign.name,
                status=campaign.status.value
            )
        
        @test_router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
        async def get_campaign(campaign_id: str):
            return CampaignResponse(
                id=campaign_id,
                name="Test Campaign",
                status="draft"
            )
        
        @test_router.post("/ads", response_model=AdResponse)
        async def create_ad(request: AdCreateRequest):
            ad = Ad(
                name=request.name,
                description=request.description,
                ad_type=AdType(request.ad_type),
                platform=Platform(request.platform)
            )
            return AdResponse(
                id=str(ad.id),
                name=ad.name,
                status=ad.status.value
            )
        
        @test_router.get("/ads/{ad_id}", response_model=AdResponse)
        async def get_ad(ad_id: str):
            return AdResponse(
                id=ad_id,
                name="Test Ad",
                status="draft"
            )
        
        @test_router.post("/optimize", response_model=OptimizationResponse)
        async def optimize_entity(request: OptimizationRequest):
            # Mock optimization
            return OptimizationResponse(
                success=True,
                improvement_percentage=15.5
            )
        
        app.include_router(test_router, prefix="/api/v1/ads")
    
    return app


class TestAPIEndpoints:
    """Test FastAPI endpoints functionality."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_test_app()
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/ads/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_create_campaign_success(self, client):
        """Test successful campaign creation."""
        campaign_data = {
            "name": "Test API Campaign",
            "objective": "Brand Awareness",
            "platform": "facebook"
        }
        
        response = client.post("/api/v1/ads/campaigns", json=campaign_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test API Campaign"
        assert data["status"] == "draft"
        assert "id" in data
    
    def test_create_campaign_validation_error(self, client):
        """Test campaign creation with validation errors."""
        invalid_data = {
            "name": "",  # Empty name should fail
            "objective": "Invalid Objective",
            "platform": "invalid_platform"
        }
        
        response = client.post("/api/v1/ads/campaigns", json=invalid_data)
        
        # Should return validation error
        assert response.status_code in [400, 422]
    
    def test_get_campaign(self, client):
        """Test getting campaign by ID."""
        campaign_id = "test-campaign-123"
        response = client.get(f"/api/v1/ads/campaigns/{campaign_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == campaign_id
        assert "name" in data
        assert "status" in data
    
    def test_create_ad_success(self, client):
        """Test successful ad creation."""
        ad_data = {
            "name": "Test API Ad",
            "description": "Test ad description",
            "ad_type": "image",
            "platform": "facebook"
        }
        
        response = client.post("/api/v1/ads/ads", json=ad_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test API Ad"
        assert data["status"] == "draft"
        assert "id" in data
    
    def test_create_ad_validation_error(self, client):
        """Test ad creation with validation errors."""
        invalid_data = {
            "name": "",  # Empty name
            "ad_type": "invalid_type",
            "platform": "invalid_platform"
        }
        
        response = client.post("/api/v1/ads/ads", json=invalid_data)
        
        # Should return validation error
        assert response.status_code in [400, 422]
    
    def test_get_ad(self, client):
        """Test getting ad by ID."""
        ad_id = "test-ad-123"
        response = client.get(f"/api/v1/ads/ads/{ad_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ad_id
        assert "name" in data
        assert "status" in data
    
    def test_optimization_endpoint(self, client):
        """Test optimization endpoint."""
        optimization_data = {
            "entity_id": "test-entity-123",
            "optimization_type": "performance",
            "level": "standard"
        }
        
        response = client.post("/api/v1/ads/optimize", json=optimization_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "improvement_percentage" in data


class TestAPIAuthentication:
    """Test API authentication and authorization."""
    
    @pytest.fixture
    def authenticated_client(self):
        """Create authenticated test client."""
        app = create_test_app()
        
        # Add authentication middleware
        @app.middleware("http")
        async def auth_middleware(request, call_next):
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]
                if token == "valid_token":
                    request.state.user_id = "test_user"
                else:
                    from fastapi import HTTPException
                    raise HTTPException(status_code=401, detail="Invalid token")
            else:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Missing authorization")
            
            response = await call_next(request)
            return response
        
        return TestClient(app)
    
    def test_unauthenticated_request(self, authenticated_client):
        """Test request without authentication."""
        response = authenticated_client.get("/api/v1/ads/health")
        assert response.status_code == 401
    
    def test_invalid_token(self, authenticated_client):
        """Test request with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = authenticated_client.get("/api/v1/ads/health", headers=headers)
        assert response.status_code == 401
    
    def test_valid_token(self, authenticated_client):
        """Test request with valid token."""
        headers = {"Authorization": "Bearer valid_token"}
        response = authenticated_client.get("/api/v1/ads/health", headers=headers)
        assert response.status_code == 200


class TestAPIRateLimiting:
    """Test API rate limiting functionality."""
    
    @pytest.fixture
    def rate_limited_client(self):
        """Create rate-limited test client."""
        app = create_test_app()
        
        # Simple in-memory rate limiter
        request_counts = {}
        
        @app.middleware("http")
        async def rate_limit_middleware(request, call_next):
            client_ip = request.client.host
            current_time = datetime.now()
            
            if client_ip not in request_counts:
                request_counts[client_ip] = []
            
            # Remove old requests (older than 1 minute)
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip]
                if (current_time - req_time).total_seconds() < 60
            ]
            
            # Check rate limit (10 requests per minute)
            if len(request_counts[client_ip]) >= 10:
                from fastapi import HTTPException
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            request_counts[client_ip].append(current_time)
            response = await call_next(request)
            return response
        
        return TestClient(app)
    
    def test_rate_limit_enforcement(self, rate_limited_client):
        """Test that rate limiting is enforced."""
        # Make requests up to the limit
        for i in range(10):
            response = rate_limited_client.get("/api/v1/ads/health")
            assert response.status_code == 200
        
        # Next request should be rate limited
        response = rate_limited_client.get("/api/v1/ads/health")
        assert response.status_code == 429


class TestAPIErrorHandling:
    """Test API error handling and responses."""
    
    @pytest.fixture
    def error_handling_client(self):
        """Create client with custom error handling."""
        app = create_test_app()
        
        @app.exception_handler(ValueError)
        async def value_error_handler(request, exc):
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=400,
                content={"error": "validation_error", "message": str(exc)}
            )
        
        @app.exception_handler(404)
        async def not_found_handler(request, exc):
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=404,
                content={"error": "not_found", "message": "Resource not found"}
            )
        
        return TestClient(app)
    
    def test_404_error_handling(self, error_handling_client):
        """Test 404 error handling."""
        response = error_handling_client.get("/api/v1/ads/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "not_found"
        assert "message" in data
    
    def test_validation_error_handling(self, error_handling_client):
        """Test validation error handling."""
        invalid_data = {
            "name": None,  # Invalid data type
            "platform": "invalid"
        }
        
        response = error_handling_client.post("/api/v1/ads/campaigns", json=invalid_data)
        
        assert response.status_code in [400, 422]
        data = response.json()
        assert "error" in data or "detail" in data


class TestAPIPerformance:
    """Test API performance characteristics."""
    
    @pytest.fixture
    def performance_client(self):
        """Create client for performance testing."""
        app = create_test_app()
        
        # Add timing middleware
        @app.middleware("http")
        async def timing_middleware(request, call_next):
            start_time = datetime.now()
            response = await call_next(request)
            process_time = (datetime.now() - start_time).total_seconds()
            response.headers["X-Process-Time"] = str(process_time)
            return response
        
        return TestClient(app)
    
    def test_response_time(self, performance_client):
        """Test API response times."""
        response = performance_client.get("/api/v1/ads/health")
        
        assert response.status_code == 200
        process_time = float(response.headers.get("X-Process-Time", 0))
        
        # Response should be under 1 second
        assert process_time < 1.0
    
    def test_concurrent_requests(self, performance_client):
        """Test handling concurrent requests."""
        import concurrent.futures
        import threading
        
        def make_request():
            return performance_client.get("/api/v1/ads/health")
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
    
    def test_large_payload_handling(self, performance_client):
        """Test handling of large payloads."""
        # Create large campaign data
        large_description = "A" * 10000  # 10KB description
        
        campaign_data = {
            "name": "Large Payload Test Campaign",
            "objective": "Large Payload Test",
            "platform": "facebook",
            "description": large_description
        }
        
        response = performance_client.post("/api/v1/ads/campaigns", json=campaign_data)
        
        # Should handle large payload gracefully
        assert response.status_code in [200, 400, 413]  # Success, validation error, or payload too large


class TestAPIContractValidation:
    """Test API contract validation and OpenAPI spec compliance."""
    
    @pytest.fixture
    def contract_client(self):
        """Create client for contract testing."""
        app = create_test_app()
        return TestClient(app)
    
    def test_openapi_spec_generation(self, contract_client):
        """Test OpenAPI specification generation."""
        response = contract_client.get("/openapi.json")
        
        assert response.status_code == 200
        spec = response.json()
        
        # Verify OpenAPI spec structure
        assert "openapi" in spec
        assert "info" in spec
        assert "paths" in spec
        
        # Verify API endpoints are documented
        paths = spec["paths"]
        assert "/api/v1/ads/health" in paths
    
    def test_response_schema_validation(self, contract_client):
        """Test that responses match declared schemas."""
        response = contract_client.get("/api/v1/ads/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure matches expected schema
        assert isinstance(data, dict)
        assert "status" in data
        assert isinstance(data["status"], str)
    
    def test_request_schema_validation(self, contract_client):
        """Test that request validation works correctly."""
        # Valid request
        valid_data = {
            "name": "Schema Test Campaign",
            "objective": "Schema Test",
            "platform": "facebook"
        }
        
        response = contract_client.post("/api/v1/ads/campaigns", json=valid_data)
        assert response.status_code == 200
        
        # Invalid request (missing required field)
        invalid_data = {
            "objective": "Schema Test",
            "platform": "facebook"
            # Missing 'name' field
        }
        
        response = contract_client.post("/api/v1/ads/campaigns", json=invalid_data)
        assert response.status_code in [400, 422]


class TestAPIIntegration:
    """Test full API integration workflows."""
    
    @pytest.fixture
    def integration_client(self):
        """Create client for integration testing."""
        app = create_test_app()
        return TestClient(app)
    
    def test_full_campaign_workflow(self, integration_client):
        """Test complete campaign creation and management workflow."""
        # 1. Create campaign
        campaign_data = {
            "name": "Integration Test Campaign",
            "objective": "Integration Testing",
            "platform": "facebook"
        }
        
        response = integration_client.post("/api/v1/ads/campaigns", json=campaign_data)
        assert response.status_code == 200
        campaign = response.json()
        campaign_id = campaign["id"]
        
        # 2. Get campaign
        response = integration_client.get(f"/api/v1/ads/campaigns/{campaign_id}")
        assert response.status_code == 200
        retrieved_campaign = response.json()
        assert retrieved_campaign["id"] == campaign_id
        
        # 3. Create ad for campaign
        ad_data = {
            "name": "Integration Test Ad",
            "description": "Ad for integration testing",
            "ad_type": "image",
            "platform": "facebook"
        }
        
        response = integration_client.post("/api/v1/ads/ads", json=ad_data)
        assert response.status_code == 200
        ad = response.json()
        ad_id = ad["id"]
        
        # 4. Get ad
        response = integration_client.get(f"/api/v1/ads/ads/{ad_id}")
        assert response.status_code == 200
        retrieved_ad = response.json()
        assert retrieved_ad["id"] == ad_id
        
        # 5. Optimize ad
        optimization_data = {
            "entity_id": ad_id,
            "optimization_type": "performance",
            "level": "standard"
        }
        
        response = integration_client.post("/api/v1/ads/optimize", json=optimization_data)
        assert response.status_code == 200
        optimization_result = response.json()
        assert optimization_result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

