"""
Microservices Infrastructure
============================

Advanced microservices infrastructure with production-ready patterns:
- Service Discovery (Consul, Eureka)
- Service Mesh Integration (Istio, Linkerd)
- Load Balancing (HAProxy, NGINX, Traefik)
- Message Queues (RabbitMQ, Apache Kafka, Redis Streams)
- API Gateway (Kong, Ambassador, Zuul)
- Configuration Management (Consul KV, etcd)
- Service Registry & Health Checks
- Distributed Tracing (Jaeger, Zipkin)
- Circuit Breakers & Bulkheads
- Retry & Timeout Policies
"""

from .service_discovery import (
    ServiceDiscoveryManager,
    ConsulServiceDiscovery,
    EurekaServiceDiscovery,
    KubernetesServiceDiscovery
)

from .service_mesh import (
    ServiceMeshManager,
    IstioServiceMesh,
    LinkerdServiceMesh,
    ConsulConnectMesh
)

from .load_balancer import (
    LoadBalancerManager,
    HAProxyLoadBalancer,
    NginxLoadBalancer,
    TraefikLoadBalancer
)

from .message_queue import (
    MessageQueueManager,
    RabbitMQService,
    KafkaService,
    RedisStreamsService
)

from .api_gateway import (
    APIGatewayManager,
    KongGateway,
    AmbassadorGateway,
    ZuulGateway
)

from .config_management import (
    ConfigurationManager,
    ConsulConfigProvider,
    EtcdConfigProvider,
    KubernetesConfigProvider
)

from .service_registry import (
    ServiceRegistry,
    ServiceInstance,
    ServiceMetadata
)

from .distributed_tracing import (
    TracingManager,
    JaegerTracing,
    ZipkinTracing,
    OpenTelemetryTracing
)

from .resilience import (
    ResilienceManager,
    BulkheadPattern,
    RetryPolicy,
    TimeoutPolicy
)

__all__ = [
    # Service Discovery
    "ServiceDiscoveryManager",
    "ConsulServiceDiscovery", 
    "EurekaServiceDiscovery",
    "KubernetesServiceDiscovery",
    
    # Service Mesh
    "ServiceMeshManager",
    "IstioServiceMesh",
    "LinkerdServiceMesh", 
    "ConsulConnectMesh",
    
    # Load Balancing
    "LoadBalancerManager",
    "HAProxyLoadBalancer",
    "NginxLoadBalancer",
    "TraefikLoadBalancer",
    
    # Message Queues
    "MessageQueueManager",
    "RabbitMQService",
    "KafkaService",
    "RedisStreamsService",
    
    # API Gateway
    "APIGatewayManager",
    "KongGateway",
    "AmbassadorGateway",
    "ZuulGateway",
    
    # Configuration
    "ConfigurationManager",
    "ConsulConfigProvider",
    "EtcdConfigProvider",
    "KubernetesConfigProvider",
    
    # Service Registry
    "ServiceRegistry",
    "ServiceInstance",
    "ServiceMetadata",
    
    # Distributed Tracing
    "TracingManager",
    "JaegerTracing",
    "ZipkinTracing",
    "OpenTelemetryTracing",
    
    # Resilience Patterns
    "ResilienceManager",
    "BulkheadPattern",
    "RetryPolicy",
    "TimeoutPolicy",
] 