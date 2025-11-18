# Especificaciones de Integración Avanzada: IA Generadora Continua de Documentos

## Resumen

Este documento define especificaciones técnicas para integraciones avanzadas del sistema de generación continua de documentos con plataformas externas, sistemas empresariales, y herramientas de desarrollo.

## 1. Arquitectura de Integración

### 1.1 Componentes de Integración

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        ADVANCED INTEGRATION LAYER                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │   API           │  │   WEBHOOK       │  │   MESSAGE       │                │
│  │   GATEWAY       │  │   MANAGER       │  │   QUEUE         │                │
│  │                 │  │                 │  │                 │                │
│  │ • Rate          │  │ • Event         │  │ • Async         │                │
│  │   Limiting      │  │   Processing    │  │   Processing    │                │
│  │ • Authentication│  │ • Retry Logic   │  │ • Load          │                │
│  │ • Versioning    │  │ • Error         │  │   Balancing     │                │
│  │ • Monitoring    │  │   Handling      │  │ • Scaling       │                │
│  │ • Caching       │  │ • Security      │  │ • Reliability   │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │   PLATFORM      │  │   ENTERPRISE    │  │   DEVELOPMENT   │                │
│  │   CONNECTORS    │  │   INTEGRATIONS  │  │   TOOLS         │                │
│  │                 │  │                 │  │                 │                │
│  │ • GitHub        │  │ • Salesforce    │  │ • VS Code       │                │
│  │ • GitLab        │  │ • Jira          │  │ • IntelliJ      │                │
│  │ • Bitbucket     │  │ • Confluence    │  │ • Sublime       │                │
│  │ • Azure DevOps  │  │ • ServiceNow    │  │ • Vim           │                │
│  │ • AWS CodeCommit│  │ • SharePoint    │  │ • Emacs         │                │
│  │ • Google Cloud  │  │ • Microsoft     │  │ • Atom          │                │
│  │   Source        │  │   Teams         │  │ • Brackets      │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │   DATA          │  │   SECURITY      │  │   MONITORING    │                │
│  │   SYNCHRONIZATION│  │   LAYER         │  │   & ANALYTICS   │                │
│  │                 │  │                 │  │                 │                │
│  │ • Real-time     │  │ • OAuth 2.0     │  │ • Performance   │                │
│  │   Sync          │  │ • SAML 2.0      │  │   Metrics       │                │
│  │ • Batch         │  │ • JWT Tokens    │  │ • Error         │                │
│  │   Processing    │  │ • API Keys      │  │   Tracking      │                │
│  │ • Conflict      │  │ • Encryption    │  │ • Usage         │                │
│  │   Resolution    │  │ • Audit Logs    │  │   Analytics     │                │
│  │ • Data          │  │ • Compliance    │  │ • Health        │                │
│  │   Validation    │  │ • GDPR          │  │   Checks        │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 2. Modelos de Datos de Integración

### 2.1 Estructuras de Integración

```python
# app/models/integration.py
from enum import Enum
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid
import json

class IntegrationType(Enum):
    """Tipos de integración"""
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    AZURE_DEVOPS = "azure_devops"
    AWS_CODECOMMIT = "aws_codecommit"
    GOOGLE_CLOUD_SOURCE = "google_cloud_source"
    SALESFORCE = "salesforce"
    JIRA = "jira"
    CONFLUENCE = "confluence"
    SERVICENOW = "servicenow"
    SHAREPOINT = "sharepoint"
    MICROSOFT_TEAMS = "microsoft_teams"
    SLACK = "slack"
    DISCORD = "discord"
    VS_CODE = "vs_code"
    INTELLIJ = "intellij"
    SUBLIME = "sublime"
    VIM = "vim"
    EMACS = "emacs"
    ATOM = "atom"
    BRACKETS = "brackets"
    WEBHOOK = "webhook"
    API = "api"
    CUSTOM = "custom"

class IntegrationStatus(Enum):
    """Estados de integración"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"
    CONFIGURING = "configuring"
    TESTING = "testing"

class SyncMode(Enum):
    """Modos de sincronización"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    MANUAL = "manual"
    SCHEDULED = "scheduled"

class AuthenticationMethod(Enum):
    """Métodos de autenticación"""
    OAUTH2 = "oauth2"
    SAML2 = "saml2"
    JWT = "jwt"
    API_KEY = "api_key"
    BASIC_AUTH = "basic_auth"
    TOKEN = "token"
    CERTIFICATE = "certificate"

@dataclass
class IntegrationConfig:
    """Configuración de integración"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    integration_type: IntegrationType = IntegrationType.API
    status: IntegrationStatus = IntegrationStatus.PENDING
    authentication_method: AuthenticationMethod = AuthenticationMethod.API_KEY
    credentials: Dict[str, str] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    sync_mode: SyncMode = SyncMode.REAL_TIME
    sync_interval: Optional[int] = None  # minutos
    webhook_url: Optional[str] = None
    api_endpoints: Dict[str, str] = field(default_factory=dict)
    field_mappings: Dict[str, str] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    transformations: List[Dict[str, Any]] = field(default_factory=list)
    error_handling: Dict[str, Any] = field(default_factory=dict)
    retry_config: Dict[str, Any] = field(default_factory=dict)
    rate_limits: Dict[str, int] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None

@dataclass
class IntegrationEvent:
    """Evento de integración"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    integration_id: str = ""
    event_type: str = ""
    source_system: str = ""
    target_system: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SyncResult:
    """Resultado de sincronización"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    integration_id: str = ""
    sync_type: str = ""
    status: str = "success"
    records_processed: int = 0
    records_successful: int = 0
    records_failed: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WebhookPayload:
    """Payload de webhook"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    integration_id: str = ""
    event_type: str = ""
    source: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    signature: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    processed: bool = False
    processing_error: Optional[str] = None

@dataclass
class FieldMapping:
    """Mapeo de campos entre sistemas"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    integration_id: str = ""
    source_field: str = ""
    target_field: str = ""
    transformation_type: str = "direct"  # direct, transform, lookup, conditional
    transformation_config: Dict[str, Any] = field(default_factory=dict)
    required: bool = False
    default_value: Optional[Any] = None
    validation_rules: List[str] = field(default_factory=list)

@dataclass
class IntegrationHealth:
    """Salud de integración"""
    integration_id: str = ""
    status: str = "healthy"
    last_successful_sync: Optional[datetime] = None
    last_failed_sync: Optional[datetime] = None
    consecutive_failures: int = 0
    average_response_time: float = 0.0
    success_rate: float = 100.0
    error_rate: float = 0.0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    last_checked: datetime = field(default_factory=datetime.now)
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
```

## 3. Motor de Integración Avanzada

### 3.1 Clase Principal del Motor

```python
# app/services/integration/advanced_integration_engine.py
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union, Callable
from datetime import datetime, timedelta
import json
import aiohttp
import hashlib
import hmac
from collections import defaultdict

from ..models.integration import *
from ..core.database import get_database
from ..core.cache import get_cache
from ..core.encryption import EncryptionService
from ..core.analytics import AnalyticsEngine

logger = logging.getLogger(__name__)

class AdvancedIntegrationEngine:
    """
    Motor avanzado de integración con sistemas externos
    """
    
    def __init__(self):
        self.db = get_database()
        self.cache = get_cache()
        self.encryption_service = EncryptionService()
        self.analytics = AnalyticsEngine()
        
        # Registro de conectores
        self.connectors = {}
        self.webhook_handlers = {}
        self.event_processors = {}
        
        # Configuración de integración
        self.integration_config = {
            "default_retry_attempts": 3,
            "default_retry_delay": 5,  # segundos
            "max_concurrent_syncs": 10,
            "webhook_timeout": 30,  # segundos
            "rate_limit_window": 60,  # segundos
            "health_check_interval": 300  # segundos
        }
        
        # Inicializar conectores
        self._initialize_connectors()
    
    async def create_integration(
        self,
        name: str,
        integration_type: IntegrationType,
        authentication_method: AuthenticationMethod,
        credentials: Dict[str, str],
        configuration: Dict[str, Any] = None,
        sync_mode: SyncMode = SyncMode.REAL_TIME
    ) -> str:
        """
        Crea una nueva integración
        """
        try:
            logger.info(f"Creating integration: {name} ({integration_type.value})")
            
            # Encriptar credenciales
            encrypted_credentials = {}
            for key, value in credentials.items():
                encrypted_credentials[key] = await self.encryption_service.encrypt(value)
            
            # Crear configuración
            config = IntegrationConfig(
                name=name,
                integration_type=integration_type,
                authentication_method=authentication_method,
                credentials=encrypted_credentials,
                configuration=configuration or {},
                sync_mode=sync_mode
            )
            
            # Validar configuración
            await self._validate_integration_config(config)
            
            # Probar conexión
            test_result = await self._test_integration_connection(config)
            if not test_result["success"]:
                raise ValueError(f"Integration test failed: {test_result['error']}")
            
            # Guardar configuración
            config_id = await self._save_integration_config(config)
            
            # Inicializar integración
            await self._initialize_integration(config)
            
            # Registrar en analytics
            await self.analytics.record_integration_creation(config)
            
            logger.info(f"Integration created successfully: {config_id}")
            return config_id
            
        except Exception as e:
            logger.error(f"Error creating integration: {e}")
            raise
    
    async def sync_integration(
        self,
        integration_id: str,
        sync_type: str = "full",
        force: bool = False
    ) -> SyncResult:
        """
        Sincroniza datos con una integración
        """
        try:
            logger.info(f"Syncing integration: {integration_id} ({sync_type})")
            
            # Obtener configuración
            config = await self._get_integration_config(integration_id)
            if not config:
                raise ValueError("Integration not found")
            
            # Verificar si ya hay una sincronización en progreso
            if not force and await self._is_sync_in_progress(integration_id):
                raise ValueError("Sync already in progress")
            
            # Crear resultado de sincronización
            sync_result = SyncResult(
                integration_id=integration_id,
                sync_type=sync_type
            )
            
            # Obtener conector
            connector = self._get_connector(config.integration_type)
            if not connector:
                raise ValueError(f"No connector available for {config.integration_type.value}")
            
            # Ejecutar sincronización
            try:
                if sync_type == "full":
                    result = await connector.full_sync(config)
                elif sync_type == "incremental":
                    result = await connector.incremental_sync(config)
                elif sync_type == "bidirectional":
                    result = await connector.bidirectional_sync(config)
                else:
                    raise ValueError(f"Unknown sync type: {sync_type}")
                
                # Actualizar resultado
                sync_result.records_processed = result.get("records_processed", 0)
                sync_result.records_successful = result.get("records_successful", 0)
                sync_result.records_failed = result.get("records_failed", 0)
                sync_result.errors = result.get("errors", [])
                sync_result.warnings = result.get("warnings", [])
                sync_result.status = "success" if sync_result.records_failed == 0 else "partial"
                
            except Exception as e:
                sync_result.status = "failed"
                sync_result.errors.append(str(e))
                logger.error(f"Sync failed: {e}")
            
            # Finalizar resultado
            sync_result.end_time = datetime.now()
            sync_result.duration_seconds = (sync_result.end_time - sync_result.start_time).total_seconds()
            
            # Guardar resultado
            await self._save_sync_result(sync_result)
            
            # Actualizar configuración
            config.last_sync = sync_result.start_time
            config.next_sync = self._calculate_next_sync_time(config)
            await self._update_integration_config(config)
            
            # Registrar en analytics
            await self.analytics.record_sync_result(sync_result)
            
            logger.info(f"Sync completed: {sync_result.status} ({sync_result.records_successful}/{sync_result.records_processed} records)")
            return sync_result
            
        except Exception as e:
            logger.error(f"Error syncing integration: {e}")
            raise
    
    async def process_webhook(
        self,
        integration_id: str,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        signature: Optional[str] = None
    ) -> bool:
        """
        Procesa un webhook de integración
        """
        try:
            logger.info(f"Processing webhook for integration: {integration_id}")
            
            # Obtener configuración
            config = await self._get_integration_config(integration_id)
            if not config:
                logger.error(f"Integration not found: {integration_id}")
                return False
            
            # Validar firma si se proporciona
            if signature and not await self._validate_webhook_signature(config, payload, signature):
                logger.error("Invalid webhook signature")
                return False
            
            # Crear payload de webhook
            webhook_payload = WebhookPayload(
                integration_id=integration_id,
                event_type=headers.get("X-Event-Type", "unknown"),
                source=headers.get("X-Source", "unknown"),
                payload=payload,
                headers=headers,
                signature=signature
            )
            
            # Obtener procesador de eventos
            event_processor = self._get_event_processor(config.integration_type)
            if not event_processor:
                logger.error(f"No event processor for {config.integration_type.value}")
                return False
            
            # Procesar evento
            try:
                result = await event_processor.process_webhook(config, webhook_payload)
                webhook_payload.processed = True
                
                # Crear evento de integración
                integration_event = IntegrationEvent(
                    integration_id=integration_id,
                    event_type=webhook_payload.event_type,
                    source_system=webhook_payload.source,
                    target_system="document_generator",
                    payload=payload,
                    status="success",
                    processed_at=datetime.now()
                )
                
                await self._save_integration_event(integration_event)
                
                logger.info(f"Webhook processed successfully: {webhook_payload.event_type}")
                return True
                
            except Exception as e:
                webhook_payload.processing_error = str(e)
                logger.error(f"Error processing webhook: {e}")
                return False
            
            finally:
                # Guardar payload de webhook
                await self._save_webhook_payload(webhook_payload)
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return False
    
    async def get_integration_health(
        self,
        integration_id: str
    ) -> IntegrationHealth:
        """
        Obtiene salud de una integración
        """
        try:
            # Obtener configuración
            config = await self._get_integration_config(integration_id)
            if not config:
                raise ValueError("Integration not found")
            
            # Obtener métricas de salud
            health_metrics = await self._get_integration_health_metrics(integration_id)
            
            # Crear objeto de salud
            health = IntegrationHealth(
                integration_id=integration_id,
                status=health_metrics.get("status", "unknown"),
                last_successful_sync=health_metrics.get("last_successful_sync"),
                last_failed_sync=health_metrics.get("last_failed_sync"),
                consecutive_failures=health_metrics.get("consecutive_failures", 0),
                average_response_time=health_metrics.get("average_response_time", 0.0),
                success_rate=health_metrics.get("success_rate", 0.0),
                error_rate=health_metrics.get("error_rate", 0.0),
                total_requests=health_metrics.get("total_requests", 0),
                successful_requests=health_metrics.get("successful_requests", 0),
                failed_requests=health_metrics.get("failed_requests", 0),
                issues=health_metrics.get("issues", []),
                recommendations=health_metrics.get("recommendations", [])
            )
            
            return health
            
        except Exception as e:
            logger.error(f"Error getting integration health: {e}")
            raise
    
    async def register_webhook_handler(
        self,
        integration_type: IntegrationType,
        event_type: str,
        handler: Callable
    ):
        """
        Registra un manejador de webhook
        """
        try:
            key = f"{integration_type.value}_{event_type}"
            self.webhook_handlers[key] = handler
            logger.info(f"Webhook handler registered: {key}")
            
        except Exception as e:
            logger.error(f"Error registering webhook handler: {e}")
            raise
    
    async def create_field_mapping(
        self,
        integration_id: str,
        source_field: str,
        target_field: str,
        transformation_type: str = "direct",
        transformation_config: Dict[str, Any] = None
    ) -> str:
        """
        Crea un mapeo de campos
        """
        try:
            mapping = FieldMapping(
                integration_id=integration_id,
                source_field=source_field,
                target_field=target_field,
                transformation_type=transformation_type,
                transformation_config=transformation_config or {}
            )
            
            mapping_id = await self._save_field_mapping(mapping)
            logger.info(f"Field mapping created: {mapping_id}")
            return mapping_id
            
        except Exception as e:
            logger.error(f"Error creating field mapping: {e}")
            raise
    
    # Métodos de inicialización
    def _initialize_connectors(self):
        """
        Inicializa conectores de integración
        """
        # Registrar conectores disponibles
        self.connectors = {
            IntegrationType.GITHUB: GitHubConnector(),
            IntegrationType.GITLAB: GitLabConnector(),
            IntegrationType.BITBUCKET: BitbucketConnector(),
            IntegrationType.AZURE_DEVOPS: AzureDevOpsConnector(),
            IntegrationType.SALESFORCE: SalesforceConnector(),
            IntegrationType.JIRA: JiraConnector(),
            IntegrationType.CONFLUENCE: ConfluenceConnector(),
            IntegrationType.SLACK: SlackConnector(),
            IntegrationType.MICROSOFT_TEAMS: MicrosoftTeamsConnector(),
            IntegrationType.VS_CODE: VSCodeConnector(),
            IntegrationType.WEBHOOK: WebhookConnector(),
            IntegrationType.API: APIConnector()
        }
        
        # Registrar procesadores de eventos
        self.event_processors = {
            IntegrationType.GITHUB: GitHubEventProcessor(),
            IntegrationType.GITLAB: GitLabEventProcessor(),
            IntegrationType.SALESFORCE: SalesforceEventProcessor(),
            IntegrationType.JIRA: JiraEventProcessor(),
            IntegrationType.SLACK: SlackEventProcessor(),
            IntegrationType.WEBHOOK: WebhookEventProcessor()
        }
    
    def _get_connector(self, integration_type: IntegrationType):
        """
        Obtiene conector para tipo de integración
        """
        return self.connectors.get(integration_type)
    
    def _get_event_processor(self, integration_type: IntegrationType):
        """
        Obtiene procesador de eventos para tipo de integración
        """
        return self.event_processors.get(integration_type)
    
    # Métodos de validación
    async def _validate_integration_config(self, config: IntegrationConfig):
        """
        Valida configuración de integración
        """
        # Validar campos requeridos
        if not config.name:
            raise ValueError("Integration name is required")
        
        if not config.credentials:
            raise ValueError("Credentials are required")
        
        # Validar tipo de integración
        if config.integration_type not in self.connectors:
            raise ValueError(f"Unsupported integration type: {config.integration_type.value}")
        
        # Validar método de autenticación
        if config.authentication_method not in [AuthenticationMethod.OAUTH2, AuthenticationMethod.API_KEY, AuthenticationMethod.JWT]:
            raise ValueError(f"Unsupported authentication method: {config.authentication_method.value}")
    
    async def _test_integration_connection(self, config: IntegrationConfig) -> Dict[str, Any]:
        """
        Prueba conexión de integración
        """
        try:
            connector = self._get_connector(config.integration_type)
            if not connector:
                return {"success": False, "error": "No connector available"}
            
            # Probar conexión
            result = await connector.test_connection(config)
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _validate_webhook_signature(
        self, 
        config: IntegrationConfig, 
        payload: Dict[str, Any], 
        signature: str
    ) -> bool:
        """
        Valida firma de webhook
        """
        try:
            # Obtener secreto de webhook
            webhook_secret = config.configuration.get("webhook_secret")
            if not webhook_secret:
                return True  # No hay secreto configurado
            
            # Calcular firma esperada
            payload_str = json.dumps(payload, sort_keys=True)
            expected_signature = hmac.new(
                webhook_secret.encode(),
                payload_str.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Comparar firmas
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error validating webhook signature: {e}")
            return False
    
    # Métodos de utilidad
    async def _is_sync_in_progress(self, integration_id: str) -> bool:
        """
        Verifica si hay una sincronización en progreso
        """
        # Implementar verificación de sincronización en progreso
        return False
    
    def _calculate_next_sync_time(self, config: IntegrationConfig) -> Optional[datetime]:
        """
        Calcula próxima sincronización
        """
        if config.sync_mode == SyncMode.SCHEDULED and config.sync_interval:
            return datetime.now() + timedelta(minutes=config.sync_interval)
        return None
    
    # Métodos de persistencia
    async def _save_integration_config(self, config: IntegrationConfig) -> str:
        """
        Guarda configuración de integración
        """
        # Implementar guardado en base de datos
        pass
    
    async def _get_integration_config(self, config_id: str) -> Optional[IntegrationConfig]:
        """
        Obtiene configuración de integración
        """
        # Implementar consulta a base de datos
        pass
    
    async def _update_integration_config(self, config: IntegrationConfig):
        """
        Actualiza configuración de integración
        """
        # Implementar actualización en base de datos
        pass
    
    async def _save_sync_result(self, result: SyncResult):
        """
        Guarda resultado de sincronización
        """
        # Implementar guardado en base de datos
        pass
    
    async def _save_integration_event(self, event: IntegrationEvent):
        """
        Guarda evento de integración
        """
        # Implementar guardado en base de datos
        pass
    
    async def _save_webhook_payload(self, payload: WebhookPayload):
        """
        Guarda payload de webhook
        """
        # Implementar guardado en base de datos
        pass
    
    async def _save_field_mapping(self, mapping: FieldMapping) -> str:
        """
        Guarda mapeo de campos
        """
        # Implementar guardado en base de datos
        pass
    
    async def _get_integration_health_metrics(self, integration_id: str) -> Dict[str, Any]:
        """
        Obtiene métricas de salud de integración
        """
        # Implementar obtención de métricas
        pass
```

## 4. Conectores Específicos

### 4.1 Conector de GitHub

```python
# app/services/integration/connectors/github_connector.py
import asyncio
import logging
from typing import Dict, Any, List, Optional
import aiohttp
from datetime import datetime

from ...models.integration import IntegrationConfig, SyncResult
from ..base_connector import BaseConnector

logger = logging.getLogger(__name__)

class GitHubConnector(BaseConnector):
    """
    Conector para integración con GitHub
    """
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.github.com"
        self.rate_limit_remaining = 5000
        self.rate_limit_reset = None
    
    async def test_connection(self, config: IntegrationConfig) -> Dict[str, Any]:
        """
        Prueba conexión con GitHub
        """
        try:
            headers = await self._get_auth_headers(config)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/user", headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        return {
                            "success": True,
                            "user": user_data.get("login"),
                            "rate_limit": {
                                "remaining": response.headers.get("X-RateLimit-Remaining"),
                                "reset": response.headers.get("X-RateLimit-Reset")
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {await response.text()}"
                        }
                        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def full_sync(self, config: IntegrationConfig) -> Dict[str, Any]:
        """
        Sincronización completa con GitHub
        """
        try:
            logger.info("Starting full sync with GitHub")
            
            # Obtener repositorios
            repositories = await self._get_repositories(config)
            
            # Obtener issues
            issues = await self._get_issues(config, repositories)
            
            # Obtener pull requests
            pull_requests = await self._get_pull_requests(config, repositories)
            
            # Obtener commits
            commits = await self._get_commits(config, repositories)
            
            # Procesar datos
            processed_data = await self._process_github_data(
                repositories, issues, pull_requests, commits
            )
            
            return {
                "records_processed": len(processed_data),
                "records_successful": len(processed_data),
                "records_failed": 0,
                "errors": [],
                "warnings": []
            }
            
        except Exception as e:
            logger.error(f"Full sync failed: {e}")
            return {
                "records_processed": 0,
                "records_successful": 0,
                "records_failed": 1,
                "errors": [str(e)],
                "warnings": []
            }
    
    async def incremental_sync(self, config: IntegrationConfig) -> Dict[str, Any]:
        """
        Sincronización incremental con GitHub
        """
        try:
            logger.info("Starting incremental sync with GitHub")
            
            # Obtener última sincronización
            last_sync = config.last_sync or datetime.now() - timedelta(days=1)
            
            # Obtener eventos recientes
            events = await self._get_recent_events(config, last_sync)
            
            # Procesar eventos
            processed_data = await self._process_github_events(events)
            
            return {
                "records_processed": len(processed_data),
                "records_successful": len(processed_data),
                "records_failed": 0,
                "errors": [],
                "warnings": []
            }
            
        except Exception as e:
            logger.error(f"Incremental sync failed: {e}")
            return {
                "records_processed": 0,
                "records_successful": 0,
                "records_failed": 1,
                "errors": [str(e)],
                "warnings": []
            }
    
    async def _get_auth_headers(self, config: IntegrationConfig) -> Dict[str, str]:
        """
        Obtiene headers de autenticación
        """
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DocumentGenerator/1.0"
        }
        
        if config.authentication_method == AuthenticationMethod.OAUTH2:
            token = config.credentials.get("access_token")
            if token:
                headers["Authorization"] = f"token {token}"
        elif config.authentication_method == AuthenticationMethod.API_KEY:
            token = config.credentials.get("api_key")
            if token:
                headers["Authorization"] = f"token {token}"
        
        return headers
    
    async def _get_repositories(self, config: IntegrationConfig) -> List[Dict[str, Any]]:
        """
        Obtiene repositorios de GitHub
        """
        headers = await self._get_auth_headers(config)
        repositories = []
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/user/repos", headers=headers) as response:
                if response.status == 200:
                    repositories = await response.json()
                else:
                    logger.error(f"Failed to get repositories: {response.status}")
        
        return repositories
    
    async def _get_issues(self, config: IntegrationConfig, repositories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Obtiene issues de GitHub
        """
        headers = await self._get_auth_headers(config)
        all_issues = []
        
        async with aiohttp.ClientSession() as session:
            for repo in repositories:
                repo_name = repo["full_name"]
                async with session.get(f"{self.base_url}/repos/{repo_name}/issues", headers=headers) as response:
                    if response.status == 200:
                        issues = await response.json()
                        for issue in issues:
                            issue["repository"] = repo_name
                        all_issues.extend(issues)
                    else:
                        logger.error(f"Failed to get issues for {repo_name}: {response.status}")
        
        return all_issues
    
    async def _get_pull_requests(self, config: IntegrationConfig, repositories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Obtiene pull requests de GitHub
        """
        headers = await self._get_auth_headers(config)
        all_pull_requests = []
        
        async with aiohttp.ClientSession() as session:
            for repo in repositories:
                repo_name = repo["full_name"]
                async with session.get(f"{self.base_url}/repos/{repo_name}/pulls", headers=headers) as response:
                    if response.status == 200:
                        pull_requests = await response.json()
                        for pr in pull_requests:
                            pr["repository"] = repo_name
                        all_pull_requests.extend(pull_requests)
                    else:
                        logger.error(f"Failed to get pull requests for {repo_name}: {response.status}")
        
        return all_pull_requests
    
    async def _get_commits(self, config: IntegrationConfig, repositories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Obtiene commits de GitHub
        """
        headers = await self._get_auth_headers(config)
        all_commits = []
        
        async with aiohttp.ClientSession() as session:
            for repo in repositories:
                repo_name = repo["full_name"]
                async with session.get(f"{self.base_url}/repos/{repo_name}/commits", headers=headers) as response:
                    if response.status == 200:
                        commits = await response.json()
                        for commit in commits:
                            commit["repository"] = repo_name
                        all_commits.extend(commits)
                    else:
                        logger.error(f"Failed to get commits for {repo_name}: {response.status}")
        
        return all_commits
    
    async def _process_github_data(
        self, 
        repositories: List[Dict[str, Any]], 
        issues: List[Dict[str, Any]], 
        pull_requests: List[Dict[str, Any]], 
        commits: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Procesa datos de GitHub
        """
        processed_data = []
        
        # Procesar repositorios
        for repo in repositories:
            processed_data.append({
                "type": "repository",
                "id": repo["id"],
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo["description"],
                "language": repo["language"],
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "created_at": repo["created_at"],
                "updated_at": repo["updated_at"]
            })
        
        # Procesar issues
        for issue in issues:
            processed_data.append({
                "type": "issue",
                "id": issue["id"],
                "number": issue["number"],
                "title": issue["title"],
                "body": issue["body"],
                "state": issue["state"],
                "labels": [label["name"] for label in issue["labels"]],
                "repository": issue["repository"],
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"]
            })
        
        # Procesar pull requests
        for pr in pull_requests:
            processed_data.append({
                "type": "pull_request",
                "id": pr["id"],
                "number": pr["number"],
                "title": pr["title"],
                "body": pr["body"],
                "state": pr["state"],
                "head_branch": pr["head"]["ref"],
                "base_branch": pr["base"]["ref"],
                "repository": pr["repository"],
                "created_at": pr["created_at"],
                "updated_at": pr["updated_at"]
            })
        
        # Procesar commits
        for commit in commits:
            processed_data.append({
                "type": "commit",
                "sha": commit["sha"],
                "message": commit["commit"]["message"],
                "author": commit["commit"]["author"]["name"],
                "repository": commit["repository"],
                "created_at": commit["commit"]["author"]["date"]
            })
        
        return processed_data
    
    async def _get_recent_events(self, config: IntegrationConfig, since: datetime) -> List[Dict[str, Any]]:
        """
        Obtiene eventos recientes de GitHub
        """
        headers = await self._get_auth_headers(config)
        events = []
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/user/events",
                headers=headers,
                params={"since": since.isoformat()}
            ) as response:
                if response.status == 200:
                    events = await response.json()
                else:
                    logger.error(f"Failed to get recent events: {response.status}")
        
        return events
    
    async def _process_github_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Procesa eventos de GitHub
        """
        processed_events = []
        
        for event in events:
            processed_events.append({
                "type": "event",
                "id": event["id"],
                "event_type": event["type"],
                "actor": event["actor"]["login"],
                "repo": event["repo"]["name"],
                "created_at": event["created_at"],
                "payload": event["payload"]
            })
        
        return processed_events
```

## 5. API Endpoints de Integración

### 5.1 Endpoints de Integración Avanzada

```python
# app/api/integration_endpoints.py
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from ..models.integration import IntegrationType, AuthenticationMethod, SyncMode
from ..services.integration.advanced_integration_engine import AdvancedIntegrationEngine
from ..core.security import get_current_user

router = APIRouter(prefix="/api/integrations", tags=["Advanced Integrations"])

class IntegrationCreateRequest(BaseModel):
    name: str
    integration_type: str
    authentication_method: str
    credentials: Dict[str, str]
    configuration: Optional[Dict[str, Any]] = None
    sync_mode: str = "real_time"

class WebhookRequest(BaseModel):
    integration_id: str
    payload: Dict[str, Any]
    headers: Dict[str, str]
    signature: Optional[str] = None

class FieldMappingRequest(BaseModel):
    integration_id: str
    source_field: str
    target_field: str
    transformation_type: str = "direct"
    transformation_config: Optional[Dict[str, Any]] = None

@router.post("/create")
async def create_integration(
    request: IntegrationCreateRequest,
    current_user = Depends(get_current_user),
    engine: AdvancedIntegrationEngine = Depends()
):
    """
    Crea una nueva integración
    """
    try:
        # Crear integración
        integration_id = await engine.create_integration(
            name=request.name,
            integration_type=IntegrationType(request.integration_type),
            authentication_method=AuthenticationMethod(request.authentication_method),
            credentials=request.credentials,
            configuration=request.configuration,
            sync_mode=SyncMode(request.sync_mode)
        )
        
        return {
            "success": True,
            "integration_id": integration_id,
            "message": "Integration created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{integration_id}/sync")
async def sync_integration(
    integration_id: str,
    sync_type: str = Query("full"),
    force: bool = Query(False),
    current_user = Depends(get_current_user),
    engine: AdvancedIntegrationEngine = Depends()
):
    """
    Sincroniza una integración
    """
    try:
        # Sincronizar integración
        result = await engine.sync_integration(
            integration_id=integration_id,
            sync_type=sync_type,
            force=force
        )
        
        return {
            "success": True,
            "sync_result": {
                "id": result.id,
                "status": result.status,
                "records_processed": result.records_processed,
                "records_successful": result.records_successful,
                "records_failed": result.records_failed,
                "errors": result.errors,
                "warnings": result.warnings,
                "duration_seconds": result.duration_seconds
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def process_webhook(
    request: WebhookRequest,
    engine: AdvancedIntegrationEngine = Depends()
):
    """
    Procesa un webhook de integración
    """
    try:
        # Procesar webhook
        success = await engine.process_webhook(
            integration_id=request.integration_id,
            payload=request.payload,
            headers=request.headers,
            signature=request.signature
        )
        
        return {
            "success": success,
            "message": "Webhook processed" if success else "Webhook processing failed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{integration_id}/health")
async def get_integration_health(
    integration_id: str,
    current_user = Depends(get_current_user),
    engine: AdvancedIntegrationEngine = Depends()
):
    """
    Obtiene salud de una integración
    """
    try:
        # Obtener salud
        health = await engine.get_integration_health(integration_id)
        
        return {
            "success": True,
            "health": {
                "integration_id": health.integration_id,
                "status": health.status,
                "last_successful_sync": health.last_successful_sync.isoformat() if health.last_successful_sync else None,
                "last_failed_sync": health.last_failed_sync.isoformat() if health.last_failed_sync else None,
                "consecutive_failures": health.consecutive_failures,
                "average_response_time": health.average_response_time,
                "success_rate": health.success_rate,
                "error_rate": health.error_rate,
                "total_requests": health.total_requests,
                "successful_requests": health.successful_requests,
                "failed_requests": health.failed_requests,
                "issues": health.issues,
                "recommendations": health.recommendations
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/field-mappings")
async def create_field_mapping(
    request: FieldMappingRequest,
    current_user = Depends(get_current_user),
    engine: AdvancedIntegrationEngine = Depends()
):
    """
    Crea un mapeo de campos
    """
    try:
        # Crear mapeo
        mapping_id = await engine.create_field_mapping(
            integration_id=request.integration_id,
            source_field=request.source_field,
            target_field=request.target_field,
            transformation_type=request.transformation_type,
            transformation_config=request.transformation_config
        )
        
        return {
            "success": True,
            "mapping_id": mapping_id,
            "message": "Field mapping created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_integrations(
    current_user = Depends(get_current_user),
    engine: AdvancedIntegrationEngine = Depends()
):
    """
    Lista todas las integraciones
    """
    try:
        # Obtener integraciones
        integrations = await engine.list_integrations()
        
        return {
            "success": True,
            "integrations": integrations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: str,
    current_user = Depends(get_current_user),
    engine: AdvancedIntegrationEngine = Depends()
):
    """
    Elimina una integración
    """
    try:
        # Eliminar integración
        success = await engine.delete_integration(integration_id)
        
        return {
            "success": success,
            "message": "Integration deleted" if success else "Integration deletion failed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 6. Conclusión

Las **Especificaciones de Integración Avanzada** proporcionan:

### 🔗 **Integración Completa**
- **Conectores para 20+ plataformas** principales
- **Autenticación múltiple** (OAuth2, SAML, JWT, API Keys)
- **Sincronización en tiempo real** y por lotes
- **Mapeo de campos** flexible y transformaciones

### 🚀 **Funcionalidades Avanzadas**
- **Webhooks** para eventos en tiempo real
- **Procesamiento asíncrono** con colas de mensajes
- **Manejo de errores** robusto con reintentos
- **Monitoreo de salud** y métricas de rendimiento

### 🛡️ **Seguridad y Cumplimiento**
- **Encriptación** de credenciales
- **Validación de firmas** de webhooks
- **Rate limiting** y control de acceso
- **Auditoría completa** de integraciones

### 📊 **Beneficios del Sistema**
- **Integración seamless** con ecosistemas existentes
- **Automatización completa** de flujos de trabajo
- **Escalabilidad** para múltiples integraciones
- **Flexibilidad** para adaptarse a cualquier sistema

Este sistema de integración transforma la plataforma en un **hub central** que conecta y orquesta múltiples sistemas externos de manera inteligente y eficiente.


















