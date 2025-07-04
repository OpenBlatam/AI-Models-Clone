"""
🌐 API GATEWAY INTEGRATION
=========================

Advanced API Gateway patterns:
- Kong/AWS API Gateway integration
- Rate limiting and security
- Request transformation
- Authentication/Authorization
"""

import time
import hmac
import hashlib
import jwt
from typing import Dict, Any, Optional, List
from functools import wraps

from fastapi import FastAPI, Request, HTTPException, Depends, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger(__name__)

# =============================================================================
# API GATEWAY MODELS
# =============================================================================

class APIGatewayConfig(BaseModel):
    """API Gateway configuration."""
    
    # Gateway type
    gateway_type: str = "kong"  # kong, aws, azure, gcp
    
    # Authentication
    jwt_secret: str = "your-secret-key"
    api_key_header: str = "X-API-Key"
    
    # Rate limiting
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600
    
    # Security
    require_https: bool = True
    cors_origins: List[str] = ["*"]
    
    # Transformations
    add_request_id: bool = True
    add_timestamp: bool = True

class GatewayRequest(BaseModel):
    """API Gateway request model."""
    
    path: str
    method: str
    headers: Dict[str, str]
    query_params: Dict[str, str] = Field(default_factory=dict)
    body: Optional[str] = None
    
    # Gateway-specific fields
    gateway_id: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

class GatewayResponse(BaseModel):
    """API Gateway response model."""
    
    status_code: int
    headers: Dict[str, str]
    body: Any
    
    # Gateway metadata
    request_id: Optional[str] = None
    processing_time_ms: Optional[float] = None

# =============================================================================
# AUTHENTICATION & AUTHORIZATION
# =============================================================================

class APIGatewayAuth:
    """API Gateway authentication handler."""
    
    def __init__(self, config: APIGatewayConfig):
        self.config = config
        self.bearer = HTTPBearer(auto_error=False)
    
    async def verify_api_key(self, api_key: Optional[str] = Header(None, alias="X-API-Key")):
        """Verify API key."""
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # In production, verify against database
        valid_keys = ["demo-api-key", "prod-api-key"]
        if api_key not in valid_keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        return api_key
    
    async def verify_jwt_token(self, credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))):
        """Verify JWT token."""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="JWT token required"
            )
        
        try:
            payload = jwt.decode(
                credentials.credentials,
                self.config.jwt_secret,
                algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def create_jwt_token(self, user_id: str, expires_in: int = 3600) -> str:
        """Create JWT token."""
        payload = {
            "user_id": user_id,
            "exp": time.time() + expires_in,
            "iat": time.time()
        }
        return jwt.encode(payload, self.config.jwt_secret, algorithm="HS256")

# =============================================================================
# RATE LIMITING
# =============================================================================

class APIGatewayRateLimit:
    """Advanced rate limiting for API Gateway."""
    
    def __init__(self, config: APIGatewayConfig):
        self.config = config
        self._requests: Dict[str, List[float]] = {}
    
    async def check_rate_limit(self, client_id: str, endpoint: str) -> bool:
        """Check if request is within rate limits."""
        key = f"{client_id}:{endpoint}"
        now = time.time()
        window_start = now - self.config.rate_limit_window
        
        # Clean old requests
        if key in self._requests:
            self._requests[key] = [
                req_time for req_time in self._requests[key]
                if req_time > window_start
            ]
        else:
            self._requests[key] = []
        
        # Check limit
        if len(self._requests[key]) >= self.config.rate_limit_requests:
            return False
        
        # Add current request
        self._requests[key].append(now)
        return True
    
    def get_rate_limit_headers(self, client_id: str, endpoint: str) -> Dict[str, str]:
        """Get rate limit headers."""
        key = f"{client_id}:{endpoint}"
        current_requests = len(self._requests.get(key, []))
        
        return {
            "X-RateLimit-Limit": str(self.config.rate_limit_requests),
            "X-RateLimit-Remaining": str(max(0, self.config.rate_limit_requests - current_requests)),
            "X-RateLimit-Reset": str(int(time.time() + self.config.rate_limit_window))
        }

# =============================================================================
# REQUEST TRANSFORMATION
# =============================================================================

class RequestTransformer:
    """Transform requests for microservices."""
    
    def __init__(self, config: APIGatewayConfig):
        self.config = config
    
    async def transform_request(self, request: Request) -> GatewayRequest:
        """Transform incoming request."""
        
        # Extract client information
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # Create gateway request
        gateway_request = GatewayRequest(
            path=request.url.path,
            method=request.method,
            headers=dict(request.headers),
            query_params=dict(request.query_params),
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        # Add request ID if enabled
        if self.config.add_request_id:
            import uuid
            gateway_request.gateway_id = str(uuid.uuid4())
        
        # Add body for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                gateway_request.body = body.decode() if body else None
            except Exception:
                pass
        
        return gateway_request
    
    def transform_response(self, response_data: Any, processing_time: float, request_id: str) -> GatewayResponse:
        """Transform response."""
        
        headers = {
            "Content-Type": "application/json",
            "X-Gateway": "blatam-api-gateway"
        }
        
        if self.config.add_request_id:
            headers["X-Request-ID"] = request_id
        
        if self.config.add_timestamp:
            headers["X-Timestamp"] = str(int(time.time()))
        
        return GatewayResponse(
            status_code=200,
            headers=headers,
            body=response_data,
            request_id=request_id,
            processing_time_ms=processing_time
        )

# =============================================================================
# API GATEWAY MIDDLEWARE
# =============================================================================

class APIGatewayMiddleware:
    """Comprehensive API Gateway middleware."""
    
    def __init__(self, config: APIGatewayConfig):
        self.config = config
        self.auth = APIGatewayAuth(config)
        self.rate_limiter = APIGatewayRateLimit(config)
        self.transformer = RequestTransformer(config)
    
    async def process_request(self, request: Request, call_next):
        """Process request through gateway."""
        start_time = time.time()
        
        try:
            # Transform request
            gateway_request = await self.transformer.transform_request(request)
            
            # Security checks
            if self.config.require_https and request.url.scheme != "https":
                if request.headers.get("x-forwarded-proto") != "https":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="HTTPS required"
                    )
            
            # Rate limiting
            client_id = gateway_request.client_ip or "unknown"
            endpoint = gateway_request.path
            
            if not await self.rate_limiter.check_rate_limit(client_id, endpoint):
                rate_headers = self.rate_limiter.get_rate_limit_headers(client_id, endpoint)
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"error": "Rate limit exceeded"},
                    headers=rate_headers
                )
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            rate_headers = self.rate_limiter.get_rate_limit_headers(client_id, endpoint)
            for key, value in rate_headers.items():
                response.headers[key] = value
            
            # Add gateway headers
            response.headers["X-Gateway"] = "blatam-api-gateway"
            response.headers["X-Processing-Time"] = f"{(time.time() - start_time) * 1000:.2f}ms"
            
            if gateway_request.gateway_id:
                response.headers["X-Request-ID"] = gateway_request.gateway_id
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Gateway middleware error", error=str(e))
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Gateway error"}
            )

# =============================================================================
# API GATEWAY APPLICATION
# =============================================================================

def create_api_gateway_app() -> FastAPI:
    """Create API Gateway integrated application."""
    
    config = APIGatewayConfig()
    
    app = FastAPI(
        title="API Gateway Integration",
        description="""
        🌐 **API Gateway Integration Patterns**
        
        ## 🔐 Security Features
        - **API Key** authentication
        - **JWT Token** validation
        - **Rate Limiting** with sliding window
        - **HTTPS** enforcement
        
        ## 🔄 Request Processing
        - **Request Transformation**
        - **Response Enhancement**
        - **Error Standardization**
        - **Logging & Monitoring**
        
        ## 🎯 Gateway Features
        - **Kong** integration ready
        - **AWS API Gateway** compatible
        - **Azure API Management** ready
        - **Google Cloud Endpoints** compatible
        """,
        version="1.0.0-gateway"
    )
    
    # Store config
    app.state.gateway_config = config
    
    # Create middleware
    gateway_middleware = APIGatewayMiddleware(config)
    
    # Add gateway middleware
    @app.middleware("http")
    async def api_gateway_middleware(request: Request, call_next):
        return await gateway_middleware.process_request(request, call_next)
    
    return app

# Create gateway app
gateway_app = create_api_gateway_app()

# =============================================================================
# GATEWAY ENDPOINTS
# =============================================================================

@gateway_app.get("/", tags=["Gateway"])
async def gateway_root():
    """API Gateway information."""
    return {
        "service": "API Gateway Integration",
        "version": "1.0.0",
        "features": [
            "API Key authentication",
            "JWT token validation",
            "Rate limiting",
            "Request transformation",
            "Response enhancement"
        ],
        "supported_gateways": [
            "Kong",
            "AWS API Gateway",
            "Azure API Management",
            "Google Cloud Endpoints"
        ]
    }

@gateway_app.post("/auth/token", tags=["Authentication"])
async def create_token(user_id: str):
    """Create JWT token for testing."""
    config: APIGatewayConfig = gateway_app.state.gateway_config
    auth = APIGatewayAuth(config)
    
    token = auth.create_jwt_token(user_id)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 3600
    }

@gateway_app.get("/protected/api-key", tags=["Protected"])
async def protected_api_key(
    request: Request,
    api_key: str = Depends(APIGatewayAuth(gateway_app.state.gateway_config).verify_api_key)
):
    """Protected endpoint with API key."""
    return {
        "message": "Access granted with API key",
        "api_key": api_key[:8] + "...",
        "timestamp": time.time()
    }

@gateway_app.get("/protected/jwt", tags=["Protected"])
async def protected_jwt(
    request: Request,
    token_payload: dict = Depends(APIGatewayAuth(gateway_app.state.gateway_config).verify_jwt_token)
):
    """Protected endpoint with JWT."""
    return {
        "message": "Access granted with JWT",
        "user_id": token_payload.get("user_id"),
        "timestamp": time.time()
    }

@gateway_app.get("/rate-limited", tags=["Rate Limiting"])
async def rate_limited_endpoint():
    """Rate limited endpoint for testing."""
    return {
        "message": "This endpoint is rate limited",
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(gateway_app, host="0.0.0.0", port=8000) 