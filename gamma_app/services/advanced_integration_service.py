"""
Advanced Integration Service with External APIs and Services
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import httpx
from urllib.parse import urljoin, urlparse
import hashlib
import hmac
import base64

from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class IntegrationType(Enum):
    """Types of integrations"""
    API = "api"
    WEBHOOK = "webhook"
    OAUTH = "oauth"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    MESSAGE_QUEUE = "message_queue"
    EMAIL = "email"
    SMS = "sms"
    SOCIAL_MEDIA = "social_media"
    PAYMENT = "payment"
    ANALYTICS = "analytics"
    STORAGE = "storage"
    AI_SERVICE = "ai_service"
    CUSTOM = "custom"

class AuthenticationType(Enum):
    """Authentication types"""
    NONE = "none"
    API_KEY = "api_key"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    OAUTH2 = "oauth2"
    HMAC = "hmac"
    CUSTOM = "custom"

class IntegrationStatus(Enum):
    """Integration status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    CONFIGURING = "configuring"
    TESTING = "testing"

@dataclass
class IntegrationConfig:
    """Integration configuration"""
    name: str
    integration_type: IntegrationType
    base_url: str
    authentication_type: AuthenticationType
    credentials: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    rate_limit: Optional[int] = None
    rate_limit_window: int = 60
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntegrationRequest:
    """Integration request"""
    method: str
    endpoint: str
    data: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    timeout: Optional[int] = None
    retry_attempts: Optional[int] = None

@dataclass
class IntegrationResponse:
    """Integration response"""
    status_code: int
    data: Any
    headers: Dict[str, str]
    response_time: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WebhookConfig:
    """Webhook configuration"""
    name: str
    url: str
    events: List[str]
    secret: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry_attempts: int = 3
    enabled: bool = True

@dataclass
class WebhookEvent:
    """Webhook event"""
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    webhook_id: str

class AdvancedIntegrationService:
    """Advanced Integration Service with External APIs and Services"""
    
    def __init__(self):
        self.integrations = {}
        self.webhooks = {}
        self.rate_limiters = {}
        self.request_cache = {}
        self.webhook_queue = asyncio.Queue()
        self.integration_metrics = {}
        
        # Initialize default integrations
        self._initialize_default_integrations()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("Advanced Integration Service initialized")
    
    def _initialize_default_integrations(self):
        """Initialize default integrations"""
        try:
            default_integrations = [
                IntegrationConfig(
                    name="openai",
                    integration_type=IntegrationType.AI_SERVICE,
                    base_url="https://api.openai.com/v1",
                    authentication_type=AuthenticationType.BEARER_TOKEN,
                    credentials={"api_key": ""},
                    headers={"Content-Type": "application/json"},
                    rate_limit=60,
                    metadata={"service": "OpenAI API"}
                ),
                IntegrationConfig(
                    name="anthropic",
                    integration_type=IntegrationType.AI_SERVICE,
                    base_url="https://api.anthropic.com/v1",
                    authentication_type=AuthenticationType.API_KEY,
                    credentials={"api_key": ""},
                    headers={"Content-Type": "application/json"},
                    rate_limit=50,
                    metadata={"service": "Anthropic API"}
                ),
                IntegrationConfig(
                    name="huggingface",
                    integration_type=IntegrationType.AI_SERVICE,
                    base_url="https://api-inference.huggingface.co",
                    authentication_type=AuthenticationType.BEARER_TOKEN,
                    credentials={"api_key": ""},
                    headers={"Content-Type": "application/json"},
                    rate_limit=100,
                    metadata={"service": "Hugging Face API"}
                ),
                IntegrationConfig(
                    name="github",
                    integration_type=IntegrationType.API,
                    base_url="https://api.github.com",
                    authentication_type=AuthenticationType.BEARER_TOKEN,
                    credentials={"token": ""},
                    headers={"Accept": "application/vnd.github.v3+json"},
                    rate_limit=5000,
                    metadata={"service": "GitHub API"}
                ),
                IntegrationConfig(
                    name="slack",
                    integration_type=IntegrationType.API,
                    base_url="https://slack.com/api",
                    authentication_type=AuthenticationType.BEARER_TOKEN,
                    credentials={"token": ""},
                    headers={"Content-Type": "application/json"},
                    rate_limit=100,
                    metadata={"service": "Slack API"}
                )
            ]
            
            for config in default_integrations:
                self.integrations[config.name] = config
                self.integration_metrics[config.name] = {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'average_response_time': 0.0,
                    'last_request': None
                }
            
            logger.info(f"Initialized {len(default_integrations)} default integrations")
            
        except Exception as e:
            logger.error(f"Error initializing default integrations: {e}")
    
    def _start_background_tasks(self):
        """Start background tasks"""
        try:
            # Start webhook processor
            asyncio.create_task(self._process_webhooks())
            
            logger.info("Background tasks started")
            
        except Exception as e:
            logger.error(f"Error starting background tasks: {e}")
    
    async def _process_webhooks(self):
        """Process webhook events"""
        try:
            while True:
                try:
                    webhook_event = await asyncio.wait_for(self.webhook_queue.get(), timeout=1.0)
                    await self._handle_webhook_event(webhook_event)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing webhook: {e}")
                    
        except Exception as e:
            logger.error(f"Error in webhook processor: {e}")
    
    async def _handle_webhook_event(self, webhook_event: WebhookEvent):
        """Handle webhook event"""
        try:
            webhook_config = self.webhooks.get(webhook_event.webhook_id)
            if not webhook_config:
                logger.error(f"Webhook config not found: {webhook_event.webhook_id}")
                return
            
            if not webhook_config.enabled:
                logger.warning(f"Webhook disabled: {webhook_event.webhook_id}")
                return
            
            # Prepare payload
            payload = {
                'event_type': webhook_event.event_type,
                'data': webhook_event.data,
                'timestamp': webhook_event.timestamp.isoformat(),
                'source': webhook_event.source
            }
            
            # Add signature if secret is configured
            if webhook_config.secret:
                signature = self._generate_webhook_signature(payload, webhook_config.secret)
                payload['signature'] = signature
            
            # Send webhook
            await self._send_webhook(webhook_config, payload)
            
        except Exception as e:
            logger.error(f"Error handling webhook event: {e}")
    
    async def _send_webhook(self, webhook_config: WebhookConfig, payload: Dict[str, Any]):
        """Send webhook"""
        try:
            headers = webhook_config.headers.copy()
            headers['Content-Type'] = 'application/json'
            
            async with httpx.AsyncClient(timeout=webhook_config.timeout) as client:
                for attempt in range(webhook_config.retry_attempts):
                    try:
                        response = await client.post(
                            webhook_config.url,
                            json=payload,
                            headers=headers
                        )
                        
                        if response.status_code < 400:
                            logger.info(f"Webhook sent successfully: {webhook_config.name}")
                            return
                        else:
                            logger.warning(f"Webhook failed with status {response.status_code}: {webhook_config.name}")
                            
                    except Exception as e:
                        logger.error(f"Webhook attempt {attempt + 1} failed: {e}")
                        
                        if attempt < webhook_config.retry_attempts - 1:
                            await asyncio.sleep(webhook_config.retry_delay * (2 ** attempt))
                
                logger.error(f"Webhook failed after {webhook_config.retry_attempts} attempts: {webhook_config.name}")
                
        except Exception as e:
            logger.error(f"Error sending webhook: {e}")
    
    def _generate_webhook_signature(self, payload: Dict[str, Any], secret: str) -> str:
        """Generate webhook signature"""
        try:
            payload_str = json.dumps(payload, sort_keys=True)
            signature = hmac.new(
                secret.encode('utf-8'),
                payload_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return f"sha256={signature}"
            
        except Exception as e:
            logger.error(f"Error generating webhook signature: {e}")
            return ""
    
    async def make_request(self, integration_name: str, request: IntegrationRequest) -> IntegrationResponse:
        """Make request to external service"""
        try:
            if integration_name not in self.integrations:
                raise ValueError(f"Integration not found: {integration_name}")
            
            config = self.integrations[integration_name]
            
            if not config.enabled:
                raise ValueError(f"Integration disabled: {integration_name}")
            
            # Check rate limit
            if not await self._check_rate_limit(integration_name):
                raise ValueError(f"Rate limit exceeded for: {integration_name}")
            
            # Prepare request
            url = urljoin(config.base_url, request.endpoint)
            headers = config.headers.copy()
            
            if request.headers:
                headers.update(request.headers)
            
            # Add authentication
            headers = await self._add_authentication(headers, config)
            
            # Make request
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=request.timeout or config.timeout) as client:
                response = await client.request(
                    method=request.method,
                    url=url,
                    json=request.data,
                    params=request.params,
                    headers=headers
                )
            
            response_time = time.time() - start_time
            
            # Parse response
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            # Create response object
            integration_response = IntegrationResponse(
                status_code=response.status_code,
                data=response_data,
                headers=dict(response.headers),
                response_time=response_time,
                success=response.status_code < 400,
                error_message=None if response.status_code < 400 else f"HTTP {response.status_code}",
                metadata={
                    'integration': integration_name,
                    'endpoint': request.endpoint,
                    'method': request.method
                }
            )
            
            # Update metrics
            await self._update_integration_metrics(integration_name, response_time, integration_response.success)
            
            logger.info(f"Request completed: {integration_name} - {request.endpoint} ({response_time:.2f}s)")
            
            return integration_response
            
        except Exception as e:
            logger.error(f"Error making request to {integration_name}: {e}")
            
            # Update metrics
            await self._update_integration_metrics(integration_name, 0, False)
            
            return IntegrationResponse(
                status_code=0,
                data=None,
                headers={},
                response_time=0,
                success=False,
                error_message=str(e),
                metadata={'integration': integration_name}
            )
    
    async def _add_authentication(self, headers: Dict[str, str], config: IntegrationConfig) -> Dict[str, str]:
        """Add authentication to headers"""
        try:
            if config.authentication_type == AuthenticationType.API_KEY:
                api_key = config.credentials.get('api_key')
                if api_key:
                    headers['X-API-Key'] = api_key
            
            elif config.authentication_type == AuthenticationType.BEARER_TOKEN:
                token = config.credentials.get('token') or config.credentials.get('api_key')
                if token:
                    headers['Authorization'] = f'Bearer {token}'
            
            elif config.authentication_type == AuthenticationType.BASIC_AUTH:
                username = config.credentials.get('username')
                password = config.credentials.get('password')
                if username and password:
                    auth_string = base64.b64encode(f'{username}:{password}'.encode()).decode()
                    headers['Authorization'] = f'Basic {auth_string}'
            
            elif config.authentication_type == AuthenticationType.HMAC:
                # HMAC authentication would be implemented here
                pass
            
            return headers
            
        except Exception as e:
            logger.error(f"Error adding authentication: {e}")
            return headers
    
    async def _check_rate_limit(self, integration_name: str) -> bool:
        """Check rate limit for integration"""
        try:
            config = self.integrations[integration_name]
            
            if not config.rate_limit:
                return True
            
            current_time = time.time()
            window_start = current_time - config.rate_limit_window
            
            # Initialize rate limiter if not exists
            if integration_name not in self.rate_limiters:
                self.rate_limiters[integration_name] = []
            
            # Remove old requests
            self.rate_limiters[integration_name] = [
                req_time for req_time in self.rate_limiters[integration_name]
                if req_time > window_start
            ]
            
            # Check if under limit
            if len(self.rate_limiters[integration_name]) >= config.rate_limit:
                return False
            
            # Add current request
            self.rate_limiters[integration_name].append(current_time)
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True
    
    async def _update_integration_metrics(self, integration_name: str, response_time: float, success: bool):
        """Update integration metrics"""
        try:
            if integration_name not in self.integration_metrics:
                self.integration_metrics[integration_name] = {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'average_response_time': 0.0,
                    'last_request': None
                }
            
            metrics = self.integration_metrics[integration_name]
            metrics['total_requests'] += 1
            metrics['last_request'] = datetime.utcnow()
            
            if success:
                metrics['successful_requests'] += 1
                # Update average response time
                metrics['average_response_time'] = (
                    (metrics['average_response_time'] * (metrics['successful_requests'] - 1) + response_time) /
                    metrics['successful_requests']
                )
            else:
                metrics['failed_requests'] += 1
            
        except Exception as e:
            logger.error(f"Error updating integration metrics: {e}")
    
    async def add_integration(self, config: IntegrationConfig):
        """Add new integration"""
        try:
            self.integrations[config.name] = config
            self.integration_metrics[config.name] = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'average_response_time': 0.0,
                'last_request': None
            }
            
            logger.info(f"Added integration: {config.name}")
            
        except Exception as e:
            logger.error(f"Error adding integration: {e}")
    
    async def remove_integration(self, integration_name: str):
        """Remove integration"""
        try:
            if integration_name in self.integrations:
                del self.integrations[integration_name]
            
            if integration_name in self.integration_metrics:
                del self.integration_metrics[integration_name]
            
            if integration_name in self.rate_limiters:
                del self.rate_limiters[integration_name]
            
            logger.info(f"Removed integration: {integration_name}")
            
        except Exception as e:
            logger.error(f"Error removing integration: {e}")
    
    async def test_integration(self, integration_name: str) -> bool:
        """Test integration connection"""
        try:
            if integration_name not in self.integrations:
                return False
            
            config = self.integrations[integration_name]
            
            # Create test request
            test_request = IntegrationRequest(
                method="GET",
                endpoint="/",
                timeout=10
            )
            
            # Make test request
            response = await self.make_request(integration_name, test_request)
            
            return response.success
            
        except Exception as e:
            logger.error(f"Error testing integration {integration_name}: {e}")
            return False
    
    async def add_webhook(self, webhook_config: WebhookConfig):
        """Add webhook configuration"""
        try:
            self.webhooks[webhook_config.name] = webhook_config
            logger.info(f"Added webhook: {webhook_config.name}")
            
        except Exception as e:
            logger.error(f"Error adding webhook: {e}")
    
    async def remove_webhook(self, webhook_name: str):
        """Remove webhook configuration"""
        try:
            if webhook_name in self.webhooks:
                del self.webhooks[webhook_name]
                logger.info(f"Removed webhook: {webhook_name}")
            
        except Exception as e:
            logger.error(f"Error removing webhook: {e}")
    
    async def trigger_webhook(self, webhook_name: str, event_type: str, data: Dict[str, Any], source: str = "system"):
        """Trigger webhook event"""
        try:
            if webhook_name not in self.webhooks:
                logger.error(f"Webhook not found: {webhook_name}")
                return False
            
            webhook_config = self.webhooks[webhook_name]
            
            if event_type not in webhook_config.events:
                logger.warning(f"Event type not configured for webhook: {event_type}")
                return False
            
            # Create webhook event
            webhook_event = WebhookEvent(
                event_type=event_type,
                data=data,
                timestamp=datetime.utcnow(),
                source=source,
                webhook_id=webhook_name
            )
            
            # Add to queue
            await self.webhook_queue.put(webhook_event)
            
            logger.info(f"Webhook event queued: {webhook_name} - {event_type}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error triggering webhook: {e}")
            return False
    
    async def get_integration_status(self, integration_name: Optional[str] = None) -> Dict[str, Any]:
        """Get integration status"""
        try:
            if integration_name:
                if integration_name not in self.integrations:
                    return {}
                
                config = self.integrations[integration_name]
                metrics = self.integration_metrics.get(integration_name, {})
                
                return {
                    'name': integration_name,
                    'type': config.integration_type.value,
                    'status': IntegrationStatus.ACTIVE.value if config.enabled else IntegrationStatus.INACTIVE.value,
                    'base_url': config.base_url,
                    'authentication_type': config.authentication_type.value,
                    'enabled': config.enabled,
                    'metrics': metrics,
                    'rate_limit': config.rate_limit,
                    'rate_limit_window': config.rate_limit_window
                }
            else:
                status = {}
                for name in self.integrations:
                    status[name] = await self.get_integration_status(name)
                return status
            
        except Exception as e:
            logger.error(f"Error getting integration status: {e}")
            return {}
    
    async def get_webhook_status(self, webhook_name: Optional[str] = None) -> Dict[str, Any]:
        """Get webhook status"""
        try:
            if webhook_name:
                if webhook_name not in self.webhooks:
                    return {}
                
                config = self.webhooks[webhook_name]
                
                return {
                    'name': webhook_name,
                    'url': config.url,
                    'events': config.events,
                    'enabled': config.enabled,
                    'timeout': config.timeout,
                    'retry_attempts': config.retry_attempts,
                    'has_secret': bool(config.secret)
                }
            else:
                status = {}
                for name in self.webhooks:
                    status[name] = await self.get_webhook_status(name)
                return status
            
        except Exception as e:
            logger.error(f"Error getting webhook status: {e}")
            return {}
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        try:
            status = {
                'service': 'Advanced Integration Service',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'integrations': {
                    'total': len(self.integrations),
                    'active': len([i for i in self.integrations.values() if i.enabled]),
                    'inactive': len([i for i in self.integrations.values() if not i.enabled])
                },
                'webhooks': {
                    'total': len(self.webhooks),
                    'active': len([w for w in self.webhooks.values() if w.enabled]),
                    'inactive': len([w for w in self.webhooks.values() if not w.enabled])
                },
                'queues': {
                    'webhook_queue_size': self.webhook_queue.qsize()
                },
                'metrics': {
                    'total_requests': sum(m.get('total_requests', 0) for m in self.integration_metrics.values()),
                    'successful_requests': sum(m.get('successful_requests', 0) for m in self.integration_metrics.values()),
                    'failed_requests': sum(m.get('failed_requests', 0) for m in self.integration_metrics.values())
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                'service': 'Advanced Integration Service',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


























