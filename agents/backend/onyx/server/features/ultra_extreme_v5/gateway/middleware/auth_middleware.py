"""
🚀 ULTRA-EXTREME V5 - AUTHENTICATION MIDDLEWARE
===============================================

Ultra-extreme authentication middleware with:
- JWT token validation
- API key authentication
- Role-based access control
- Rate limiting per user
- Security headers
- Audit logging
"""

import time
import jwt
import hashlib
import hmac
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import structlog

from ..config.settings import get_settings


class AuthMiddleware(BaseHTTPMiddleware):
    """Ultra-extreme authentication middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
        self.logger = structlog.get_logger(__name__)
        self.security = HTTPBearer(auto_error=False)
        
        # JWT secret key
        self.secret_key = self.settings.AUTH_SECRET_KEY.get_secret_value()
        self.algorithm = self.settings.AUTH_ALGORITHM
        
        # API keys cache
        self.api_keys_cache = set(self.settings.API_KEYS)
        
        # Rate limiting cache
        self.rate_limit_cache = {}
        
        # Audit log
        self.audit_log = []
    
    async def dispatch(self, request: Request, call_next):
        """Process the request through authentication middleware"""
        start_time = time.time()
        
        try:
            # Skip authentication for certain paths
            if self._should_skip_auth(request.url.path):
                return await call_next(request)
            
            # Extract authentication credentials
            auth_credentials = await self._extract_auth_credentials(request)
            
            if not auth_credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication credentials required",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Validate authentication
            user_info = await self._validate_auth(auth_credentials, request)
            
            # Check rate limiting
            await self._check_rate_limiting(user_info, request)
            
            # Add user info to request state
            request.state.user = user_info
            request.state.auth_time = start_time
            
            # Add security headers
            response = await call_next(request)
            self._add_security_headers(response)
            
            # Log audit trail
            await self._log_audit_trail(request, response, user_info, start_time)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error("Authentication error", error=str(e), exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )
    
    def _should_skip_auth(self, path: str) -> bool:
        """Check if authentication should be skipped for this path"""
        skip_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico"
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    async def _extract_auth_credentials(self, request: Request) -> Optional[Dict[str, Any]]:
        """Extract authentication credentials from request"""
        # Try JWT Bearer token
        try:
            credentials: HTTPAuthorizationCredentials = await self.security(request)
            if credentials:
                return {
                    "type": "jwt",
                    "token": credentials.credentials
                }
        except Exception:
            pass
        
        # Try API key in header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return {
                "type": "api_key",
                "key": api_key
            }
        
        # Try API key in query parameter
        api_key = request.query_params.get("api_key")
        if api_key:
            return {
                "type": "api_key",
                "key": api_key
            }
        
        # Try API key in body (for POST requests)
        if request.method == "POST":
            try:
                body = await request.body()
                if body:
                    # This is a simplified check - in production you'd parse JSON properly
                    if b"api_key" in body:
                        return {
                            "type": "api_key",
                            "key": "extracted_from_body"
                        }
            except Exception:
                pass
        
        return None
    
    async def _validate_auth(self, credentials: Dict[str, Any], request: Request) -> Dict[str, Any]:
        """Validate authentication credentials"""
        auth_type = credentials["type"]
        
        if auth_type == "jwt":
            return await self._validate_jwt(credentials["token"])
        elif auth_type == "api_key":
            return await self._validate_api_key(credentials["key"])
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication type"
            )
    
    async def _validate_jwt(self, token: str) -> Dict[str, Any]:
        """Validate JWT token"""
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "require": ["exp", "iat", "sub"]
                }
            )
            
            # Check if token is expired
            exp_timestamp = payload.get("exp")
            if exp_timestamp and datetime.utcnow().timestamp() > exp_timestamp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            # Check if token is issued in the future
            iat_timestamp = payload.get("iat")
            if iat_timestamp and datetime.utcnow().timestamp() < iat_timestamp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token issued in the future"
                )
            
            # Extract user information
            user_info = {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "roles": payload.get("roles", []),
                "permissions": payload.get("permissions", []),
                "auth_type": "jwt",
                "token_id": payload.get("jti"),
                "issued_at": datetime.fromtimestamp(iat_timestamp) if iat_timestamp else None,
                "expires_at": datetime.fromtimestamp(exp_timestamp) if exp_timestamp else None
            }
            
            self.logger.info("JWT token validated successfully", user_id=user_info["user_id"])
            return user_info
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            self.logger.warning("Invalid JWT token", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except Exception as e:
            self.logger.error("JWT validation error", error=str(e), exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token validation error"
            )
    
    async def _validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """Validate API key"""
        try:
            # Check if API key is in allowed keys
            if api_key not in self.api_keys_cache:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key"
                )
            
            # Generate user info for API key
            user_info = {
                "user_id": f"api_key_{hashlib.sha256(api_key.encode()).hexdigest()[:8]}",
                "email": None,
                "roles": ["api_user"],
                "permissions": ["api_access"],
                "auth_type": "api_key",
                "api_key_hash": hashlib.sha256(api_key.encode()).hexdigest(),
                "issued_at": datetime.utcnow(),
                "expires_at": None
            }
            
            self.logger.info("API key validated successfully", user_id=user_info["user_id"])
            return user_info
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error("API key validation error", error=str(e), exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API key validation error"
            )
    
    async def _check_rate_limiting(self, user_info: Dict[str, Any], request: Request):
        """Check rate limiting for user"""
        if not self.settings.RATE_LIMIT_ENABLED:
            return
        
        user_id = user_info["user_id"]
        current_time = time.time()
        
        # Get user's rate limit info
        if user_id not in self.rate_limit_cache:
            self.rate_limit_cache[user_id] = {
                "requests": [],
                "last_reset": current_time
            }
        
        user_limits = self.rate_limit_cache[user_id]
        
        # Reset counter if window has passed
        window_start = current_time - self.settings.RATE_LIMIT_WINDOW
        user_limits["requests"] = [
            req_time for req_time in user_limits["requests"]
            if req_time > window_start
        ]
        
        # Check if user has exceeded rate limit
        if len(user_limits["requests"]) >= self.settings.RATE_LIMIT_REQUESTS:
            self.logger.warning("Rate limit exceeded", user_id=user_id)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(self.settings.RATE_LIMIT_REQUESTS),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(window_start + self.settings.RATE_LIMIT_WINDOW))
                }
            )
        
        # Add current request to rate limit tracking
        user_limits["requests"].append(current_time)
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        if not self.settings.SECURITY_HEADERS_ENABLED:
            return
        
        for header_name, header_value in self.settings.SECURITY_HEADERS.items():
            response.headers[header_name] = header_value
    
    async def _log_audit_trail(self, request: Request, response: Response, user_info: Dict[str, Any], start_time: float):
        """Log audit trail for the request"""
        try:
            audit_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_info["user_id"],
                "auth_type": user_info["auth_type"],
                "method": request.method,
                "path": str(request.url.path),
                "query_params": dict(request.query_params),
                "status_code": response.status_code,
                "response_time": time.time() - start_time,
                "user_agent": request.headers.get("user-agent"),
                "ip_address": self._get_client_ip(request),
                "roles": user_info.get("roles", []),
                "permissions": user_info.get("permissions", [])
            }
            
            # Add to audit log (in production, this would go to a database or external service)
            self.audit_log.append(audit_entry)
            
            # Keep only last 1000 entries in memory
            if len(self.audit_log) > 1000:
                self.audit_log = self.audit_log[-1000:]
            
            # Log to structured logger
            self.logger.info(
                "Request processed",
                user_id=user_info["user_id"],
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                response_time=audit_entry["response_time"]
            )
            
        except Exception as e:
            self.logger.error("Error logging audit trail", error=str(e))
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        return self.audit_log.copy()
    
    def clear_audit_log(self):
        """Clear audit log"""
        self.audit_log.clear() 