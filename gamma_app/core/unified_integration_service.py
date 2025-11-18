"""
Unified Integration Service - Consolidated integration functionality
Combines all integration-related services into a single, optimized service
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum
import aiohttp
import json
import time
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import hmac
import hashlib
import base64
from collections import defaultdict
import ssl
import certifi

logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    """Integration Types"""
    API = "api"
    WEBHOOK = "webhook"
    OAUTH2 = "oauth2"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    FILE_SYSTEM = "file_system"
    EMAIL = "email"
    SMS = "sms"
    SOCIAL_MEDIA = "social_media"

class AuthenticationType(Enum):
    """Authentication Types"""
    NONE = "none"
    API_KEY = "api_key"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    OAUTH2 = "oauth2"
    HMAC = "hmac"
    CUSTOM = "custom"

class IntegrationStatus(Enum):
    """Integration Status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"
    TESTING = "testing"

@dataclass
class IntegrationConfig:
    """Integration Configuration"""
    name: str
    type: IntegrationType
    base_url: str
    authentication: AuthenticationType
    credentials: Dict[str, str]
    headers: Dict[str, str]
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 1
    rate_limit: int = 100
    rate_limit_window: int = 3600
    webhook_secret: Optional[str] = None
    oauth2_config: Optional[Dict[str, Any]] = None

@dataclass
class IntegrationRequest:
    """Integration Request"""
    integration_name: str
    endpoint: str
    method: str = "GET"
    data: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    timeout: Optional[int] = None

@dataclass
class IntegrationResponse:
    """Integration Response"""
    status_code: int
    data: Any
    headers: Dict[str, str]
    response_time: float
    success: bool
    error: Optional[str] = None

class UnifiedIntegrationService:
    """
    Unified Integration Service - Consolidated integration functionality
    Handles API integrations, webhooks, OAuth2, and external service connections
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.integrations: Dict[str, IntegrationConfig] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limits: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "requests": [],
            "window_start": time.time()
        })
        self.webhook_handlers: Dict[str, Callable] = {}
        self.oauth2_tokens: Dict[str, Dict[str, Any]] = {}
        
        # SSL context for secure connections
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        logger.info("UnifiedIntegrationService initialized")
    
    async def initialize(self):
        """Initialize the integration service"""
        try:
            # Create aiohttp session with SSL context
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            timeout = aiohttp.ClientTimeout(total=30)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={"User-Agent": "GammaApp-Integration/1.0"}
            )
            
            logger.info("Integration service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing integration service: {e}")
            raise
    
    async def register_integration(self, config: IntegrationConfig) -> bool:
        """Register a new integration"""
        try:
            self.integrations[config.name] = config
            
            # Test the integration if it's an API
            if config.type == IntegrationType.API:
                test_result = await self._test_integration(config)
                if not test_result:
                    logger.warning(f"Integration {config.name} test failed")
            
            logger.info(f"Integration {config.name} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error registering integration {config.name}: {e}")
            return False
    
    async def _test_integration(self, config: IntegrationConfig) -> bool:
        """Test integration connectivity"""
        try:
            test_request = IntegrationRequest(
                integration_name=config.name,
                endpoint="/health" if config.type == IntegrationType.API else "/",
                method="GET"
            )
            
            response = await self.make_request(test_request)
            return response.success and response.status_code < 400
            
        except Exception as e:
            logger.error(f"Error testing integration {config.name}: {e}")
            return False
    
    async def make_request(self, request: IntegrationRequest) -> IntegrationResponse:
        """Make a request to an integration"""
        start_time = time.time()
        
        try:
            if not self.session:
                await self.initialize()
            
            # Get integration config
            if request.integration_name not in self.integrations:
                raise ValueError(f"Integration {request.integration_name} not found")
            
            config = self.integrations[request.integration_name]
            
            # Check rate limit
            if not await self._check_rate_limit(request.integration_name):
                raise Exception("Rate limit exceeded")
            
            # Prepare URL
            url = urljoin(config.base_url, request.endpoint)
            
            # Prepare headers
            headers = config.headers.copy()
            if request.headers:
                headers.update(request.headers)
            
            # Add authentication
            await self._add_authentication(config, headers, request)
            
            # Prepare request data
            json_data = None
            if request.data and request.method in ["POST", "PUT", "PATCH"]:
                json_data = request.data
            
            # Make request
            async with self.session.request(
                method=request.method,
                url=url,
                json=json_data,
                params=request.params,
                headers=headers,
                timeout=request.timeout or config.timeout
            ) as response:
                
                # Read response
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                response_time = time.time() - start_time
                
                return IntegrationResponse(
                    status_code=response.status,
                    data=response_data,
                    headers=dict(response.headers),
                    response_time=response_time,
                    success=200 <= response.status < 400
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Error making request to {request.integration_name}: {e}")
            
            return IntegrationResponse(
                status_code=0,
                data=None,
                headers={},
                response_time=response_time,
                success=False,
                error=str(e)
            )
    
    async def _add_authentication(self, config: IntegrationConfig, headers: Dict[str, str], request: IntegrationRequest):
        """Add authentication to request"""
        try:
            if config.authentication == AuthenticationType.API_KEY:
                api_key = config.credentials.get("api_key")
                if api_key:
                    headers["X-API-Key"] = api_key
            
            elif config.authentication == AuthenticationType.BASIC_AUTH:
                username = config.credentials.get("username")
                password = config.credentials.get("password")
                if username and password:
                    auth_string = f"{username}:{password}"
                    auth_bytes = auth_string.encode('ascii')
                    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
                    headers["Authorization"] = f"Basic {auth_b64}"
            
            elif config.authentication == AuthenticationType.BEARER_TOKEN:
                token = config.credentials.get("token")
                if token:
                    headers["Authorization"] = f"Bearer {token}"
            
            elif config.authentication == AuthenticationType.OAUTH2:
                token = await self._get_oauth2_token(config)
                if token:
                    headers["Authorization"] = f"Bearer {token}"
            
            elif config.authentication == AuthenticationType.HMAC:
                await self._add_hmac_auth(config, headers, request)
            
            elif config.authentication == AuthenticationType.CUSTOM:
                # Custom authentication logic
                custom_auth = config.credentials.get("custom_auth")
                if custom_auth:
                    headers.update(custom_auth)
                    
        except Exception as e:
            logger.error(f"Error adding authentication: {e}")
    
    async def _get_oauth2_token(self, config: IntegrationConfig) -> Optional[str]:
        """Get OAuth2 token"""
        try:
            integration_name = config.name
            
            # Check if we have a valid token
            if integration_name in self.oauth2_tokens:
                token_data = self.oauth2_tokens[integration_name]
                if token_data["expires_at"] > datetime.now():
                    return token_data["access_token"]
            
            # Get new token
            oauth2_config = config.oauth2_config
            if not oauth2_config:
                return None
            
            token_data = await self._request_oauth2_token(oauth2_config)
            if token_data:
                self.oauth2_tokens[integration_name] = token_data
                return token_data["access_token"]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting OAuth2 token: {e}")
            return None
    
    async def _request_oauth2_token(self, oauth2_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Request OAuth2 token"""
        try:
            token_url = oauth2_config["token_url"]
            client_id = oauth2_config["client_id"]
            client_secret = oauth2_config["client_secret"]
            grant_type = oauth2_config.get("grant_type", "client_credentials")
            
            data = {
                "grant_type": grant_type,
                "client_id": client_id,
                "client_secret": client_secret
            }
            
            if grant_type == "authorization_code":
                data["code"] = oauth2_config.get("code")
                data["redirect_uri"] = oauth2_config.get("redirect_uri")
            
            async with self.session.post(token_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    token_data["expires_at"] = datetime.now() + timedelta(
                        seconds=token_data.get("expires_in", 3600)
                    )
                    return token_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error requesting OAuth2 token: {e}")
            return None
    
    async def _add_hmac_auth(self, config: IntegrationConfig, headers: Dict[str, str], request: IntegrationRequest):
        """Add HMAC authentication"""
        try:
            secret = config.credentials.get("secret")
            if not secret:
                return
            
            # Create signature
            timestamp = str(int(time.time()))
            method = request.method
            path = request.endpoint
            body = json.dumps(request.data) if request.data else ""
            
            message = f"{method}\n{path}\n{timestamp}\n{body}"
            signature = hmac.new(
                secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            headers["X-Timestamp"] = timestamp
            headers["X-Signature"] = signature
            
        except Exception as e:
            logger.error(f"Error adding HMAC auth: {e}")
    
    async def _check_rate_limit(self, integration_name: str) -> bool:
        """Check rate limit for integration"""
        try:
            config = self.integrations[integration_name]
            current_time = time.time()
            
            rate_data = self.rate_limits[integration_name]
            
            # Clean old requests
            window_start = current_time - config.rate_limit_window
            rate_data["requests"] = [
                req_time for req_time in rate_data["requests"]
                if req_time > window_start
            ]
            
            # Check if under limit
            if len(rate_data["requests"]) >= config.rate_limit:
                return False
            
            # Add current request
            rate_data["requests"].append(current_time)
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True  # Allow request if rate limit check fails
    
    async def register_webhook_handler(self, webhook_name: str, handler: Callable) -> bool:
        """Register webhook handler"""
        try:
            self.webhook_handlers[webhook_name] = handler
            logger.info(f"Webhook handler {webhook_name} registered")
            return True
            
        except Exception as e:
            logger.error(f"Error registering webhook handler: {e}")
            return False
    
    async def process_webhook(self, webhook_name: str, payload: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """Process incoming webhook"""
        try:
            if webhook_name not in self.webhook_handlers:
                logger.warning(f"No handler for webhook {webhook_name}")
                return False
            
            # Verify webhook signature if configured
            if webhook_name in self.integrations:
                config = self.integrations[webhook_name]
                if config.webhook_secret:
                    if not await self._verify_webhook_signature(payload, headers, config.webhook_secret):
                        logger.warning(f"Invalid webhook signature for {webhook_name}")
                        return False
            
            # Process webhook
            handler = self.webhook_handlers[webhook_name]
            await handler(payload, headers)
            
            logger.info(f"Webhook {webhook_name} processed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error processing webhook {webhook_name}: {e}")
            return False
    
    async def _verify_webhook_signature(self, payload: Dict[str, Any], headers: Dict[str, str], secret: str) -> bool:
        """Verify webhook signature"""
        try:
            signature = headers.get("X-Hub-Signature-256", headers.get("X-Signature"))
            if not signature:
                return False
            
            # Create expected signature
            payload_str = json.dumps(payload, separators=(',', ':'))
            expected_signature = hmac.new(
                secret.encode(),
                payload_str.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            if signature.startswith("sha256="):
                signature = signature[7:]
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False
    
    async def send_webhook(self, webhook_url: str, payload: Dict[str, Any], secret: Optional[str] = None) -> bool:
        """Send webhook to external service"""
        try:
            if not self.session:
                await self.initialize()
            
            headers = {"Content-Type": "application/json"}
            
            # Add signature if secret provided
            if secret:
                payload_str = json.dumps(payload, separators=(',', ':'))
                signature = hmac.new(
                    secret.encode(),
                    payload_str.encode(),
                    hashlib.sha256
                ).hexdigest()
                headers["X-Hub-Signature-256"] = f"sha256={signature}"
            
            async with self.session.post(webhook_url, json=payload, headers=headers) as response:
                success = 200 <= response.status < 300
                if success:
                    logger.info(f"Webhook sent successfully to {webhook_url}")
                else:
                    logger.warning(f"Webhook failed with status {response.status}")
                return success
                
        except Exception as e:
            logger.error(f"Error sending webhook: {e}")
            return False
    
    async def get_integration_status(self, integration_name: str) -> Dict[str, Any]:
        """Get integration status"""
        try:
            if integration_name not in self.integrations:
                return {"status": "not_found"}
            
            config = self.integrations[integration_name]
            
            # Test connectivity
            test_result = await self._test_integration(config)
            
            # Get rate limit info
            rate_data = self.rate_limits[integration_name]
            current_time = time.time()
            window_start = current_time - config.rate_limit_window
            recent_requests = [
                req for req in rate_data["requests"]
                if req > window_start
            ]
            
            return {
                "name": integration_name,
                "type": config.type.value,
                "status": "active" if test_result else "error",
                "base_url": config.base_url,
                "authentication": config.authentication.value,
                "rate_limit_usage": len(recent_requests),
                "rate_limit_max": config.rate_limit,
                "last_test": datetime.now().isoformat(),
                "test_result": test_result
            }
            
        except Exception as e:
            logger.error(f"Error getting integration status: {e}")
            return {"status": "error", "error": str(e)}
    
    async def list_integrations(self) -> List[Dict[str, Any]]:
        """List all integrations"""
        try:
            integrations = []
            for name, config in self.integrations.items():
                status = await self.get_integration_status(name)
                integrations.append(status)
            
            return integrations
            
        except Exception as e:
            logger.error(f"Error listing integrations: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for integration service"""
        try:
            total_integrations = len(self.integrations)
            active_integrations = 0
            
            for name in self.integrations:
                status = await self.get_integration_status(name)
                if status.get("status") == "active":
                    active_integrations += 1
            
            return {
                "status": "healthy",
                "total_integrations": total_integrations,
                "active_integrations": active_integrations,
                "webhook_handlers": len(self.webhook_handlers),
                "oauth2_tokens": len(self.oauth2_tokens),
                "session_active": self.session is not None
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def close(self):
        """Close the integration service"""
        try:
            if self.session:
                await self.session.close()
            logger.info("Integration service closed")
            
        except Exception as e:
            logger.error(f"Error closing integration service: {e}")


























