"""
Sistema de Integración con Service Mesh v4.4
HeyGen AI - Sistema de Monitoreo Inteligente con IA Avanzada

Este sistema implementa:
- Integración nativa con Istio, Linkerd y otros service meshes
- Gestión automática de tráfico y routing
- Observabilidad y telemetría avanzada
- Políticas de seguridad y mTLS
- Load balancing inteligente y circuit breaking
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import random

@dataclass
class ServiceMeshConfig:
    """Service mesh configuration"""
    mesh_id: str
    name: str
    type: str  # 'istio', 'linkerd', 'consul', 'kuma'
    version: str
    namespace: str
    enabled_features: List[str]
    configuration: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VirtualService:
    """Virtual service configuration"""
    vs_id: str
    name: str
    namespace: str
    hosts: List[str]
    gateways: List[str]
    http_routes: List[Dict[str, Any]]
    tcp_routes: List[Dict[str, Any]] = field(default_factory=list)
    tls_routes: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DestinationRule:
    """Destination rule configuration"""
    dr_id: str
    name: str
    namespace: str
    host: str
    traffic_policy: Dict[str, Any]
    subsets: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ServiceEntry:
    """Service entry configuration"""
    se_id: str
    name: str
    namespace: str
    hosts: List[str]
    addresses: List[str]
    ports: List[Dict[str, Any]]
    location: str = "MESH_EXTERNAL"
    resolution: str = "DNS"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrafficPolicy:
    """Traffic policy configuration"""
    policy_id: str
    name: str
    namespace: str
    selector: Dict[str, Any]
    policy_type: str  # 'load_balancer', 'connection_pool', 'outlier_detection', 'tls'
    configuration: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MeshMetrics:
    """Service mesh metrics"""
    timestamp: datetime
    mesh_id: str
    total_services: int
    total_pods: int
    active_connections: int
    request_count: int
    error_rate: float
    latency_p95: float
    throughput: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class ServiceMeshIntegrationSystem:
    """Service mesh integration system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.service_meshes = {}
        self.virtual_services = {}
        self.destination_rules = {}
        self.service_entries = {}
        self.traffic_policies = {}
        
        # Metrics and monitoring
        self.mesh_metrics_history = deque(maxlen=10000)
        self.traffic_flow_history = deque(maxlen=5000)
        
        # System configuration
        self.auto_traffic_management = config.get('auto_traffic_management', True)
        self.circuit_breaker_enabled = config.get('circuit_breaker_enabled', True)
        self.mtls_enabled = config.get('mtls_enabled', True)
        self.observability_enabled = config.get('observability_enabled', True)
        
        # Active connections and monitoring
        self.active_connections = {}
        self.connection_pools = {}
        
        # Initialize system
        self._initialize_service_meshes()
        self._initialize_mesh_components()
        
        # System state
        self.is_running = False
        self.mesh_monitoring_task = None
        self.traffic_management_task = None
    
    def _initialize_service_meshes(self):
        """Initialize supported service meshes"""
        
        # Istio Service Mesh
        self.service_meshes['istio'] = ServiceMeshConfig(
            mesh_id="istio-main",
            name="Istio Service Mesh",
            type="istio",
            version="1.18.0",
            namespace="istio-system",
            enabled_features=[
                "traffic_management",
                "security",
                "observability",
                "policy_enforcement"
            ],
            configuration={
                "auto_injection": True,
                "default_policy": "PERMISSIVE",
                "tracing": "jaeger",
                "metrics": "prometheus"
            }
        )
        
        # Linkerd Service Mesh
        self.service_meshes['linkerd'] = ServiceMeshConfig(
            mesh_id="linkerd-main",
            name="Linkerd Service Mesh",
            type="linkerd",
            version="2.12.0",
            namespace="linkerd",
            enabled_features=[
                "traffic_management",
                "security",
                "observability",
                "load_balancing"
            ],
            configuration={
                "auto_injection": True,
                "default_policy": "ALLOW",
                "tracing": "jaeger",
                "metrics": "prometheus"
            }
        )
        
        # Consul Service Mesh
        self.service_meshes['consul'] = ServiceMeshConfig(
            mesh_id="consul-main",
            name="Consul Service Mesh",
            type="consul",
            version="1.15.0",
            namespace="consul-system",
            enabled_features=[
                "service_discovery",
                "traffic_management",
                "security",
                "observability"
            ],
            configuration={
                "auto_injection": True,
                "default_policy": "PERMISSIVE",
                "tracing": "jaeger",
                "metrics": "prometheus"
            }
        )
    
    def _initialize_mesh_components(self):
        """Initialize service mesh components"""
        
        # Virtual Services for HeyGen AI components
        self.virtual_services['heygen_api'] = VirtualService(
            vs_id="heygen-api-vs",
            name="heygen-api",
            namespace="heygen-ai",
            hosts=["api.heygen.ai", "api.internal"],
            gateways=["heygen-gateway"],
            http_routes=[
                {
                    "match": [{"uri": {"prefix": "/api/v1"}}],
                    "route": [{"destination": {"host": "heygen-api-service", "port": {"number": 8080}}}],
                    "retries": {"attempts": 3, "perTryTimeout": "2s"},
                    "timeout": "30s"
                }
            ]
        )
        
        self.virtual_services['heygen_ml'] = VirtualService(
            vs_id="heygen-ml-vs",
            name="heygen-ml",
            namespace="heygen-ai",
            hosts=["ml.heygen.ai", "ml.internal"],
            gateways=["heygen-gateway"],
            http_routes=[
                {
                    "match": [{"uri": {"prefix": "/ml"}}],
                    "route": [{"destination": {"host": "heygen-ml-service", "port": {"number": 8080}}}],
                    "retries": {"attempts": 2, "perTryTimeout": "5s"},
                    "timeout": "60s"
                }
            ]
        )
        
        # Destination Rules
        self.destination_rules['heygen_api_dr'] = DestinationRule(
            dr_id="heygen-api-dr",
            name="heygen-api",
            namespace="heygen-ai",
            host="heygen-api-service",
            traffic_policy={
                "loadBalancer": {"simple": "ROUND_ROBIN"},
                "connectionPool": {
                    "tcp": {"maxConnections": 100},
                    "http": {"http1MaxPendingRequests": 1000, "maxRequestsPerConnection": 10}
                },
                "outlierDetection": {
                    "consecutive5xxErrors": 5,
                    "interval": "30s",
                    "baseEjectionTime": "30s"
                }
            },
            subsets=[
                {"name": "v1", "labels": {"version": "v1"}},
                {"name": "v2", "labels": {"version": "v2"}}
            ]
        )
        
        # Service Entries for external services
        self.service_entries['external_ai_service'] = ServiceEntry(
            se_id="external-ai-service",
            name="external-ai-service",
            namespace="heygen-ai",
            hosts=["ai.external.com"],
            addresses=["10.0.0.100"],
            ports=[{"number": 443, "name": "https", "protocol": "HTTPS"}],
            location="MESH_EXTERNAL",
            resolution="STATIC"
        )
        
        # Traffic Policies
        self.traffic_policies['load_balancing'] = TrafficPolicy(
            policy_id="load-balancing-policy",
            name="Load Balancing Policy",
            namespace="heygen-ai",
            selector={"app": "heygen-api"},
            policy_type="load_balancer",
            configuration={
                "algorithm": "LEAST_CONN",
                "health_check": {"enabled": True, "interval": "30s"},
                "connection_draining": {"enabled": True, "timeout": "60s"}
            }
        )
        
        self.traffic_policies['circuit_breaker'] = TrafficPolicy(
            policy_id="circuit-breaker-policy",
            name="Circuit Breaker Policy",
            namespace="heygen-ai",
            selector={"app": "heygen-ml"},
            policy_type="outlier_detection",
            configuration={
                "consecutive_errors": 5,
                "interval": "30s",
                "base_ejection_time": "60s",
                "max_ejection_percent": 10
            }
        )
    
    async def start(self):
        """Start the service mesh integration system"""
        
        if self.is_running:
            print("⚠️ El sistema de service mesh ya está ejecutándose")
            return
        
        self.is_running = True
        print("🚀 Iniciando Sistema de Integración con Service Mesh v4.4")
        
        # Start background tasks
        self.mesh_monitoring_task = asyncio.create_task(self._mesh_monitoring_loop())
        self.traffic_management_task = asyncio.create_task(self._traffic_management_loop())
        
        print("✅ Sistema de service mesh iniciado exitosamente")
    
    async def stop(self):
        """Stop the service mesh integration system"""
        
        print("🛑 Deteniendo Sistema de Service Mesh...")
        self.is_running = False
        
        # Cancel background tasks
        if self.mesh_monitoring_task:
            self.mesh_monitoring_task.cancel()
        if self.traffic_management_task:
            self.traffic_management_task.cancel()
        
        print("✅ Sistema de service mesh detenido")
    
    async def _mesh_monitoring_loop(self):
        """Continuous service mesh monitoring loop"""
        
        while self.is_running:
            try:
                # Collect mesh metrics
                await self._collect_mesh_metrics()
                
                # Monitor traffic flows
                await self._monitor_traffic_flows()
                
                # Check mesh health
                await self._check_mesh_health()
                
                await asyncio.sleep(15)  # Monitor every 15 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Error en monitoreo de service mesh: {e}")
                await asyncio.sleep(60)
    
    async def _traffic_management_loop(self):
        """Continuous traffic management loop"""
        
        while self.is_running:
            try:
                # Auto-adjust traffic policies
                if self.auto_traffic_management:
                    await self._auto_adjust_traffic_policies()
                
                # Manage circuit breakers
                if self.circuit_breaker_enabled:
                    await self._manage_circuit_breakers()
                
                # Update load balancing
                await self._update_load_balancing()
                
                await asyncio.sleep(30)  # Manage traffic every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Error en gestión de tráfico: {e}")
                await asyncio.sleep(60)
    
    async def _collect_mesh_metrics(self):
        """Collect service mesh metrics"""
        
        for mesh_id, mesh in self.service_meshes.items():
            try:
                # Simulate metrics collection
                metrics = MeshMetrics(
                    timestamp=datetime.now(),
                    mesh_id=mesh_id,
                    total_services=random.randint(50, 200),
                    total_pods=random.randint(100, 500),
                    active_connections=random.randint(1000, 10000),
                    request_count=random.randint(10000, 100000),
                    error_rate=random.uniform(0.001, 0.05),
                    latency_p95=random.uniform(50, 500),
                    throughput=random.uniform(1000, 10000)
                )
                
                self.mesh_metrics_history.append(metrics)
                
                # Log significant metrics
                if metrics.error_rate > 0.03:  # 3% error rate
                    print(f"⚠️ Error rate alto en {mesh.name}: {metrics.error_rate:.2%}")
                
                if metrics.latency_p95 > 300:  # 300ms latency
                    print(f"⚠️ Latencia alta en {mesh.name}: {metrics.latency_p95:.1f}ms")
                
            except Exception as e:
                print(f"❌ Error recolectando métricas para {mesh_id}: {e}")
    
    async def _monitor_traffic_flows(self):
        """Monitor traffic flows between services"""
        
        # Simulate traffic flow monitoring
        service_pairs = [
            ("heygen-api", "heygen-ml"),
            ("heygen-api", "heygen-database"),
            ("heygen-ml", "heygen-storage"),
            ("heygen-api", "external-ai-service")
        ]
        
        for source, destination in service_pairs:
            try:
                # Simulate traffic flow data
                flow_data = {
                    'timestamp': datetime.now(),
                    'source_service': source,
                    'destination_service': destination,
                    'request_count': random.randint(100, 1000),
                    'error_count': random.randint(0, 50),
                    'latency_avg': random.uniform(20, 200),
                    'throughput': random.uniform(100, 1000),
                    'connection_count': random.randint(10, 100)
                }
                
                self.traffic_flow_history.append(flow_data)
                
                # Check for anomalies
                if flow_data['error_count'] / flow_data['request_count'] > 0.1:  # 10% error rate
                    print(f"🚨 Alto error rate en tráfico: {source} -> {destination}")
                
            except Exception as e:
                print(f"❌ Error monitoreando tráfico {source} -> {destination}: {e}")
    
    async def _check_mesh_health(self):
        """Check overall service mesh health"""
        
        for mesh_id, mesh in self.service_meshes.items():
            try:
                # Simulate health check
                health_status = {
                    'mesh_id': mesh_id,
                    'timestamp': datetime.now(),
                    'overall_health': 'healthy',
                    'components': {}
                }
                
                # Check individual components
                components = ['control_plane', 'data_plane', 'gateway', 'sidecar_injector']
                
                for component in components:
                    # Simulate component health
                    if random.random() < 0.95:  # 95% healthy
                        health_status['components'][component] = 'healthy'
                    else:
                        health_status['components'][component] = 'unhealthy'
                        health_status['overall_health'] = 'degraded'
                
                # Log health issues
                if health_status['overall_health'] != 'healthy':
                    print(f"⚠️ Service mesh {mesh.name} en estado degradado")
                    for comp, status in health_status['components'].items():
                        if status == 'unhealthy':
                            print(f"   Componente {comp}: {status}")
                
            except Exception as e:
                print(f"❌ Error verificando salud de {mesh_id}: {e}")
    
    async def _auto_adjust_traffic_policies(self):
        """Automatically adjust traffic policies based on metrics"""
        
        try:
            # Get recent metrics
            if len(self.mesh_metrics_history) < 5:
                return
            
            recent_metrics = list(self.mesh_metrics_history)[-5:]
            
            # Calculate average error rate and latency
            avg_error_rate = sum(m.error_rate for m in recent_metrics) / len(recent_metrics)
            avg_latency = sum(m.latency_p95 for m in recent_metrics) / len(recent_metrics)
            
            # Adjust circuit breaker policies
            if avg_error_rate > 0.05:  # 5% error rate
                await self._tighten_circuit_breaker()
            elif avg_error_rate < 0.01:  # 1% error rate
                await self._loosen_circuit_breaker()
            
            # Adjust load balancing
            if avg_latency > 200:  # 200ms latency
                await self._optimize_load_balancing()
                
        except Exception as e:
            print(f"❌ Error ajustando políticas de tráfico: {e}")
    
    async def _tighten_circuit_breaker(self):
        """Tighten circuit breaker policies"""
        
        print("🔒 Ajustando circuit breaker más estricto...")
        
        for policy_id, policy in self.traffic_policies.items():
            if policy.policy_type == "outlier_detection":
                # Make circuit breaker more sensitive
                current_errors = policy.configuration.get("consecutive_errors", 5)
                new_errors = max(3, current_errors - 1)
                
                if new_errors != current_errors:
                    policy.configuration["consecutive_errors"] = new_errors
                    print(f"   Circuit breaker ajustado: {current_errors} -> {new_errors} errores consecutivos")
    
    async def _loosen_circuit_breaker(self):
        """Loosen circuit breaker policies"""
        
        print("🔓 Ajustando circuit breaker menos estricto...")
        
        for policy_id, policy in self.traffic_policies.items():
            if policy.policy_type == "outlier_detection":
                # Make circuit breaker less sensitive
                current_errors = policy.configuration.get("consecutive_errors", 5)
                new_errors = min(10, current_errors + 1)
                
                if new_errors != current_errors:
                    policy.configuration["consecutive_errors"] = new_errors
                    print(f"   Circuit breaker ajustado: {current_errors} -> {new_errors} errores consecutivos")
    
    async def _optimize_load_balancing(self):
        """Optimize load balancing policies"""
        
        print("⚖️ Optimizando load balancing...")
        
        for policy_id, policy in self.traffic_policies.items():
            if policy.policy_type == "load_balancer":
                # Switch to more aggressive load balancing
                current_algorithm = policy.configuration.get("algorithm", "ROUND_ROBIN")
                
                if current_algorithm == "ROUND_ROBIN":
                    policy.configuration["algorithm"] = "LEAST_CONN"
                    print(f"   Load balancing cambiado: ROUND_ROBIN -> LEAST_CONN")
                elif current_algorithm == "LEAST_CONN":
                    policy.configuration["algorithm"] = "RANDOM"
                    print(f"   Load balancing cambiado: LEAST_CONN -> RANDOM")
    
    async def _manage_circuit_breakers(self):
        """Manage circuit breaker states"""
        
        try:
            # Simulate circuit breaker management
            for policy_id, policy in self.traffic_policies.items():
                if policy.policy_type == "outlier_detection":
                    # Simulate circuit breaker state changes
                    if random.random() < 0.1:  # 10% chance of circuit breaker opening
                        print(f"🚨 Circuit breaker abierto para política: {policy.name}")
                        
                        # Simulate recovery
                        await asyncio.sleep(random.uniform(30, 120))
                        print(f"✅ Circuit breaker cerrado para política: {policy.name}")
                        
        except Exception as e:
            print(f"❌ Error gestionando circuit breakers: {e}")
    
    async def _update_load_balancing(self):
        """Update load balancing configurations"""
        
        try:
            # Simulate load balancing updates
            for policy_id, policy in self.traffic_policies.items():
                if policy.policy_type == "load_balancer":
                    # Update health check intervals
                    current_interval = policy.configuration.get("health_check", {}).get("interval", "30s")
                    
                    # Adjust based on traffic patterns
                    if random.random() < 0.3:  # 30% chance of update
                        new_interval = "15s" if current_interval == "30s" else "30s"
                        policy.configuration["health_check"]["interval"] = new_interval
                        print(f"   Health check actualizado: {current_interval} -> {new_interval}")
                        
        except Exception as e:
            print(f"❌ Error actualizando load balancing: {e}")
    
    async def create_virtual_service(self, virtual_service: VirtualService) -> bool:
        """Create a new virtual service"""
        
        try:
            self.virtual_services[virtual_service.vs_id] = virtual_service
            print(f"✅ Virtual Service creado: {virtual_service.name}")
            return True
            
        except Exception as e:
            print(f"❌ Error creando Virtual Service: {e}")
            return False
    
    async def create_destination_rule(self, destination_rule: DestinationRule) -> bool:
        """Create a new destination rule"""
        
        try:
            self.destination_rules[destination_rule.dr_id] = destination_rule
            print(f"✅ Destination Rule creado: {destination_rule.name}")
            return True
            
        except Exception as e:
            print(f"❌ Error creando Destination Rule: {e}")
            return False
    
    async def create_service_entry(self, service_entry: ServiceEntry) -> bool:
        """Create a new service entry"""
        
        try:
            self.service_entries[service_entry.se_id] = service_entry
            print(f"✅ Service Entry creado: {service_entry.name}")
            return True
            
        except Exception as e:
            print(f"❌ Error creando Service Entry: {e}")
            return False
    
    async def update_traffic_policy(self, policy_id: str, new_config: Dict[str, Any]) -> bool:
        """Update a traffic policy"""
        
        try:
            if policy_id in self.traffic_policies:
                policy = self.traffic_policies[policy_id]
                policy.configuration.update(new_config)
                print(f"✅ Traffic Policy actualizado: {policy.name}")
                return True
            else:
                print(f"❌ Traffic Policy no encontrado: {policy_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error actualizando Traffic Policy: {e}")
            return False
    
    def get_mesh_status(self, mesh_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific service mesh"""
        
        if mesh_id in self.service_meshes:
            mesh = self.service_meshes[mesh_id]
            return {
                'mesh_id': mesh.mesh_id,
                'name': mesh.name,
                'type': mesh.type,
                'version': mesh.version,
                'namespace': mesh.namespace,
                'enabled_features': mesh.enabled_features,
                'configuration': mesh.configuration
            }
        return None
    
    def get_recent_metrics(self, mesh_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent metrics for a specific mesh"""
        
        recent_metrics = []
        for metric in list(self.mesh_metrics_history)[-limit:]:
            if metric.mesh_id == mesh_id:
                recent_metrics.append({
                    'timestamp': metric.timestamp.isoformat(),
                    'total_services': metric.total_services,
                    'total_pods': metric.total_pods,
                    'active_connections': metric.active_connections,
                    'request_count': metric.request_count,
                    'error_rate': metric.error_rate,
                    'latency_p95': metric.latency_p95,
                    'throughput': metric.throughput
                })
        
        return recent_metrics
    
    def get_traffic_flows(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent traffic flow data"""
        
        recent_flows = []
        for flow in list(self.traffic_flow_history)[-limit:]:
            recent_flows.append({
                'timestamp': flow['timestamp'].isoformat(),
                'source_service': flow['source_service'],
                'destination_service': flow['destination_service'],
                'request_count': flow['request_count'],
                'error_count': flow['error_count'],
                'latency_avg': flow['latency_avg'],
                'throughput': flow['throughput']
            })
        
        return recent_flows
    
    async def enable_mtls(self, namespace: str) -> bool:
        """Enable mTLS for a namespace"""
        
        try:
            print(f"🔐 Habilitando mTLS para namespace: {namespace}")
            
            # Simulate mTLS enablement
            await asyncio.sleep(2)
            
            print(f"✅ mTLS habilitado para namespace: {namespace}")
            return True
            
        except Exception as e:
            print(f"❌ Error habilitando mTLS: {e}")
            return False
    
    async def disable_mtls(self, namespace: str) -> bool:
        """Disable mTLS for a namespace"""
        
        try:
            print(f"🔓 Deshabilitando mTLS para namespace: {namespace}")
            
            # Simulate mTLS disablement
            await asyncio.sleep(2)
            
            print(f"✅ mTLS deshabilitado para namespace: {namespace}")
            return True
            
        except Exception as e:
            print(f"❌ Error deshabilitando mTLS: {e}")
            return False
    
    async def inject_sidecar(self, namespace: str, deployment: str) -> bool:
        """Inject sidecar proxy into a deployment"""
        
        try:
            print(f"💉 Inyectando sidecar en deployment: {deployment} (namespace: {namespace})")
            
            # Simulate sidecar injection
            await asyncio.sleep(3)
            
            print(f"✅ Sidecar inyectado en deployment: {deployment}")
            return True
            
        except Exception as e:
            print(f"❌ Error inyectando sidecar: {e}")
            return False
    
    def export_mesh_config(self, mesh_id: str) -> Optional[Dict[str, Any]]:
        """Export service mesh configuration"""
        
        if mesh_id in self.service_meshes:
            mesh = self.service_meshes[mesh_id]
            return {
                'mesh_config': {
                    'mesh_id': mesh.mesh_id,
                    'name': mesh.name,
                    'type': mesh.type,
                    'version': mesh.version,
                    'namespace': mesh.namespace,
                    'enabled_features': mesh.enabled_features,
                    'configuration': mesh.configuration
                },
                'virtual_services': {vs_id: vs.__dict__ for vs_id, vs in self.virtual_services.items()},
                'destination_rules': {dr_id: dr.__dict__ for dr_id, dr in self.destination_rules.items()},
                'service_entries': {se_id: se.__dict__ for se_id, se in self.service_entries.items()},
                'traffic_policies': {tp_id: tp.__dict__ for tp_id, tp in self.traffic_policies.items()},
                'export_timestamp': datetime.now().isoformat()
            }
        return None

# Factory function
async def create_service_mesh_integration_system(config: Dict[str, Any]) -> ServiceMeshIntegrationSystem:
    """Create and initialize the service mesh integration system"""
    system = ServiceMeshIntegrationSystem(config)
    return system

if __name__ == "__main__":
    # Demo usage
    async def main():
        config = {
            'auto_traffic_management': True,
            'circuit_breaker_enabled': True,
            'mtls_enabled': True,
            'observability_enabled': True
        }
        
        system = await create_service_mesh_integration_system(config)
        
        try:
            await system.start()
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            await system.stop()
    
    asyncio.run(main())
