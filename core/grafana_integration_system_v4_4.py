"""
Sistema de Integración Nativa con Grafana v4.4
HeyGen AI - Sistema de Monitoreo Inteligente con IA Avanzada

Este sistema implementa:
- Integración nativa con Grafana
- Creación automática de dashboards
- Configuración de data sources
- Sistema de alerting integrado
- Métricas personalizadas para HeyGen AI
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import aiohttp
import requests
from dataclasses import dataclass, field

@dataclass
class GrafanaDashboard:
    """Grafana dashboard configuration"""
    dashboard_id: str
    title: str
    description: str
    panels: List[Dict[str, Any]]
    tags: List[str]
    timezone: str = "browser"
    refresh: str = "30s"
    schema_version: int = 30
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GrafanaDataSource:
    """Grafana data source configuration"""
    datasource_id: str
    name: str
    type: str  # prometheus, influxdb, elasticsearch, etc.
    url: str
    access: str = "proxy"
    is_default: bool = False
    json_data: Dict[str, Any] = field(default_factory=dict)
    secure_json_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GrafanaAlert:
    """Grafana alert configuration"""
    alert_id: str
    name: str
    condition: str
    frequency: str = "1m"
    handler: int = 1
    message: str = ""
    notifications: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class GrafanaIntegrationSystem:
    """Native Grafana integration system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.grafana_url = config.get('grafana_url', 'http://localhost:3000')
        self.api_key = config.get('api_key', '')
        self.username = config.get('username', 'admin')
        self.password = config.get('password', 'admin')
        
        # Session for API calls
        self.session = aiohttp.ClientSession()
        self.is_connected = False
        
        # Predefined dashboards and data sources
        self.dashboards = {}
        self.data_sources = {}
        self.alerts = {}
        
        # Initialize system
        self._initialize_grafana_components()
    
    def _initialize_grafana_components(self):
        """Initialize Grafana dashboards and data sources"""
        
        # Initialize data sources
        self._setup_data_sources()
        
        # Initialize dashboards
        self._setup_dashboards()
        
        # Initialize alerts
        self._setup_alerts()
    
    def _setup_data_sources(self):
        """Setup Grafana data sources"""
        
        # Prometheus data source
        self.data_sources['prometheus'] = GrafanaDataSource(
            datasource_id="prometheus",
            name="Prometheus",
            type="prometheus",
            url="http://localhost:9090",
            is_default=True,
            json_data={
                "timeInterval": "15s",
                "queryTimeout": "60s"
            }
        )
        
        # InfluxDB data source
        self.data_sources['influxdb'] = GrafanaDataSource(
            datasource_id="influxdb",
            name="InfluxDB",
            type="influxdb",
            url="http://localhost:8086",
            json_data={
                "version": "Flux",
                "organization": "heygen-ai",
                "defaultBucket": "metrics"
            }
        )
        
        # Elasticsearch data source
        self.data_sources['elasticsearch'] = GrafanaDataSource(
            datasource_id="elasticsearch",
            name="Elasticsearch",
            type="elasticsearch",
            url="http://localhost:9200",
            json_data={
                "timeField": "@timestamp",
                "esVersion": "7.0.0"
            }
        )
    
    def _setup_dashboards(self):
        """Setup predefined Grafana dashboards"""
        
        # Main System Overview Dashboard
        self.dashboards['system_overview'] = GrafanaDashboard(
            dashboard_id="system-overview",
            title="HeyGen AI - System Overview",
            description="Vista general del sistema HeyGen AI con métricas clave",
            tags=["heygen-ai", "overview", "system"],
            panels=self._create_system_overview_panels()
        )
        
        # Performance Analysis Dashboard
        self.dashboards['performance_analysis'] = GrafanaDashboard(
            dashboard_id="performance-analysis",
            title="HeyGen AI - Performance Analysis",
            description="Análisis detallado del rendimiento del sistema",
            tags=["heygen-ai", "performance", "analysis"],
            panels=self._create_performance_panels()
        )
        
        # Security Monitoring Dashboard
        self.dashboards['security_monitoring'] = GrafanaDashboard(
            dashboard_id="security-monitoring",
            title="HeyGen AI - Security Monitoring",
            description="Monitoreo de seguridad y amenazas",
            tags=["heygen-ai", "security", "monitoring"],
            panels=self._create_security_panels()
        )
        
        # Cost Analysis Dashboard
        self.dashboards['cost_analysis'] = GrafanaDashboard(
            dashboard_id="cost-analysis",
            title="HeyGen AI - Cost Analysis",
            description="Análisis de costos y optimización",
            tags=["heygen-ai", "cost", "analysis"],
            panels=self._create_cost_panels()
        )
    
    def _create_system_overview_panels(self) -> List[Dict[str, Any]]:
        """Create panels for system overview dashboard"""
        
        panels = []
        
        # CPU Usage Panel
        panels.append({
            "id": 1,
            "title": "CPU Usage",
            "type": "stat",
            "targets": [
                {
                    "expr": "avg(rate(heygen_ai_cpu_usage_total[5m])) * 100",
                    "legendFormat": "CPU Usage %"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "thresholds"},
                    "thresholds": {
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 70},
                            {"color": "red", "value": 90}
                        ]
                    }
                }
            },
            "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0}
        })
        
        # Memory Usage Panel
        panels.append({
            "id": 2,
            "title": "Memory Usage",
            "type": "stat",
            "targets": [
                {
                    "expr": "avg(rate(heygen_ai_memory_usage_bytes[5m])) / 1024 / 1024",
                    "legendFormat": "Memory Usage MB"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "thresholds"},
                    "thresholds": {
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 80},
                            {"color": "red", "value": 95}
                        ]
                    }
                }
            },
            "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0}
        })
        
        # System Health Score Panel
        panels.append({
            "id": 3,
            "title": "System Health Score",
            "type": "gauge",
            "targets": [
                {
                    "expr": "avg(heygen_ai_system_health_score)",
                    "legendFormat": "Health Score"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "min": 0,
                    "max": 1,
                    "thresholds": {
                        "steps": [
                            {"color": "red", "value": 0},
                            {"color": "yellow", "value": 0.6},
                            {"color": "green", "value": 0.8}
                        ]
                    }
                }
            },
            "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0}
        })
        
        # Active Alerts Panel
        panels.append({
            "id": 4,
            "title": "Active Alerts",
            "type": "stat",
            "targets": [
                {
                    "expr": "count(heygen_ai_alerts_total{status='active'})",
                    "legendFormat": "Active Alerts"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "thresholds"},
                    "thresholds": {
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 3},
                            {"color": "red", "value": 5}
                        ]
                    }
                }
            },
            "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0}
        })
        
        return panels
    
    def _create_performance_panels(self) -> List[Dict[str, Any]]:
        """Create panels for performance analysis dashboard"""
        
        panels = []
        
        # Response Time Trend
        panels.append({
            "id": 1,
            "title": "Response Time Trend",
            "type": "timeseries",
            "targets": [
                {
                    "expr": "rate(heygen_ai_response_time_seconds_sum[5m]) / rate(heygen_ai_response_time_seconds_count[5m])",
                    "legendFormat": "Avg Response Time"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette"},
                    "custom": {
                        "lineWidth": 2,
                        "fillOpacity": 10
                    }
                }
            },
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
        })
        
        # Throughput Panel
        panels.append({
            "id": 2,
            "title": "Request Throughput",
            "type": "timeseries",
            "targets": [
                {
                    "expr": "rate(heygen_ai_requests_total[5m])",
                    "legendFormat": "Requests/sec"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette"},
                    "custom": {
                        "lineWidth": 2,
                        "fillOpacity": 10
                    }
                }
            },
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
        })
        
        return panels
    
    def _create_security_panels(self) -> List[Dict[str, Any]]:
        """Create panels for security monitoring dashboard"""
        
        panels = []
        
        # Security Threats
        panels.append({
            "id": 1,
            "title": "Security Threats Detected",
            "type": "stat",
            "targets": [
                {
                    "expr": "count(heygen_ai_security_threats_total)",
                    "legendFormat": "Total Threats"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "thresholds"},
                    "thresholds": {
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 1},
                            {"color": "red", "value": 5}
                        ]
                    }
                }
            },
            "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0}
        })
        
        # Failed Login Attempts
        panels.append({
            "id": 2,
            "title": "Failed Login Attempts",
            "type": "timeseries",
            "targets": [
                {
                    "expr": "rate(heygen_ai_failed_logins_total[5m])",
                    "legendFormat": "Failed Logins/sec"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette"},
                    "custom": {
                        "lineWidth": 2,
                        "fillOpacity": 10
                    }
                }
            },
            "gridPos": {"h": 8, "w": 12, "x": 6, "y": 0}
        })
        
        return panels
    
    def _create_cost_panels(self) -> List[Dict[str, Any]]:
        """Create panels for cost analysis dashboard"""
        
        panels = []
        
        # Cost per Hour
        panels.append({
            "id": 1,
            "title": "Cost per Hour",
            "type": "stat",
            "targets": [
                {
                    "expr": "avg(heygen_ai_cost_per_hour_usd)",
                    "legendFormat": "USD/Hour"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "thresholds"},
                    "thresholds": {
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 10},
                            {"color": "red", "value": 50}
                        ]
                    }
                }
            },
            "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0}
        })
        
        # Cost Trend
        panels.append({
            "id": 2,
            "title": "Cost Trend (24h)",
            "type": "timeseries",
            "targets": [
                {
                    "expr": "rate(heygen_ai_cost_total_usd[1h])",
                    "legendFormat": "Cost Rate USD/Hour"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette"},
                    "custom": {
                        "lineWidth": 2,
                        "fillOpacity": 10
                    }
                }
            },
            "gridPos": {"h": 8, "w": 12, "x": 6, "y": 0}
        })
        
        return panels
    
    def _setup_alerts(self):
        """Setup Grafana alerting rules"""
        
        # High CPU Usage Alert
        self.alerts['high_cpu'] = GrafanaAlert(
            alert_id="high-cpu-usage",
            name="High CPU Usage",
            condition="avg(rate(heygen_ai_cpu_usage_total[5m])) * 100 > 90",
            message="CPU usage is above 90% for the last 5 minutes",
            notifications=[{"uid": "default"}]
        )
        
        # High Memory Usage Alert
        self.alerts['high_memory'] = GrafanaAlert(
            alert_id="high-memory-usage",
            name="High Memory Usage",
            condition="avg(rate(heygen_ai_memory_usage_bytes[5m])) / 1024 / 1024 > 95",
            message="Memory usage is above 95% for the last 5 minutes",
            notifications=[{"uid": "default"}]
        )
        
        # Security Threat Alert
        self.alerts['security_threat'] = GrafanaAlert(
            alert_id="security-threat-detected",
            name="Security Threat Detected",
            condition="increase(heygen_ai_security_threats_total[5m]) > 0",
            message="New security threat detected in the last 5 minutes",
            notifications=[{"uid": "default"}]
        )
    
    async def connect(self) -> bool:
        """Connect to Grafana instance"""
        
        try:
            # Test connection
            headers = self._get_auth_headers()
            async with self.session.get(f"{self.grafana_url}/api/health", headers=headers) as response:
                if response.status == 200:
                    self.is_connected = True
                    print("✅ Conectado a Grafana exitosamente")
                    return True
                else:
                    print(f"❌ Error conectando a Grafana: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error conectando a Grafana: {e}")
            return False
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for Grafana API"""
        
        if self.api_key:
            return {"Authorization": f"Bearer {self.api_key}"}
        else:
            # Basic auth
            import base64
            credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            return {"Authorization": f"Basic {credentials}"}
    
    async def create_data_source(self, data_source: GrafanaDataSource) -> bool:
        """Create a new data source in Grafana"""
        
        if not self.is_connected:
            print("❌ No conectado a Grafana")
            return False
        
        try:
            payload = {
                "name": data_source.name,
                "type": data_source.type,
                "url": data_source.url,
                "access": data_source.access,
                "isDefault": data_source.is_default,
                "jsonData": data_source.json_data
            }
            
            if data_source.secure_json_data:
                payload["secureJsonData"] = data_source.secure_json_data
            
            headers = self._get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            async with self.session.post(
                f"{self.grafana_url}/api/datasources",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status in [200, 409]:  # 409 = already exists
                    print(f"✅ Data source '{data_source.name}' creado/configurado")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Error creando data source: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error creando data source: {e}")
            return False
    
    async def create_dashboard(self, dashboard: GrafanaDashboard) -> bool:
        """Create a new dashboard in Grafana"""
        
        if not self.is_connected:
            print("❌ No conectado a Grafana")
            return False
        
        try:
            payload = {
                "dashboard": {
                    "id": None,  # New dashboard
                    "title": dashboard.title,
                    "description": dashboard.description,
                    "tags": dashboard.tags,
                    "timezone": dashboard.timezone,
                    "refresh": dashboard.refresh,
                    "schemaVersion": dashboard.schema_version,
                    "version": dashboard.version,
                    "panels": dashboard.panels
                },
                "folderId": 0,  # General folder
                "overwrite": True
            }
            
            headers = self._get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            async with self.session.post(
                f"{self.grafana_url}/api/dashboards/db",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    dashboard.dashboard_id = result.get('id', dashboard.dashboard_id)
                    print(f"✅ Dashboard '{dashboard.title}' creado exitosamente")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Error creando dashboard: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error creando dashboard: {e}")
            return False
    
    async def create_alert(self, alert: GrafanaAlert) -> bool:
        """Create a new alert rule in Grafana"""
        
        if not self.is_connected:
            print("❌ No conectado a Grafana")
            return False
        
        try:
            # First, get the default alert manager
            headers = self._get_auth_headers()
            
            async with self.session.get(
                f"{self.grafana_url}/api/alertmanager/grafana/config",
                headers=headers
            ) as response:
                
                if response.status != 200:
                    print("❌ No se pudo obtener configuración del alert manager")
                    return False
                
                config = await response.json()
                
                # Create alert rule
                alert_payload = {
                    "alert": {
                        "name": alert.name,
                        "condition": alert.condition,
                        "frequency": alert.frequency,
                        "handler": alert.handler,
                        "message": alert.message,
                        "notifications": alert.notifications
                    }
                }
                
                headers["Content-Type"] = "application/json"
                
                async with self.session.post(
                    f"{self.grafana_url}/api/alertmanager/grafana/config/alerts",
                    headers=headers,
                    json=alert_payload
                ) as alert_response:
                    
                    if alert_response.status == 200:
                        print(f"✅ Alert '{alert.name}' creado exitosamente")
                        return True
                    else:
                        error_text = await alert_response.text()
                        print(f"❌ Error creando alert: {alert_response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            print(f"❌ Error creando alert: {e}")
            return False
    
    async def setup_complete_grafana_integration(self) -> bool:
        """Setup complete Grafana integration with all components"""
        
        print("🚀 Configurando integración completa con Grafana...")
        
        # Connect to Grafana
        if not await self.connect():
            return False
        
        # Create data sources
        print("📊 Creando data sources...")
        for data_source in self.data_sources.values():
            await self.create_data_source(data_source)
        
        # Create dashboards
        print("📈 Creando dashboards...")
        for dashboard in self.dashboards.values():
            await self.create_dashboard(dashboard)
        
        # Create alerts
        print("🚨 Configurando alertas...")
        for alert in self.alerts.values():
            await self.create_alert(alert)
        
        print("✅ Integración con Grafana completada exitosamente")
        return True
    
    async def get_dashboard_url(self, dashboard_id: str) -> str:
        """Get URL for a specific dashboard"""
        
        return f"{self.grafana_url}/d/{dashboard_id}"
    
    async def export_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        """Export dashboard configuration"""
        
        if not self.is_connected:
            print("❌ No conectado a Grafana")
            return {}
        
        try:
            headers = self._get_auth_headers()
            
            async with self.session.get(
                f"{self.grafana_url}/api/dashboards/uid/{dashboard_id}",
                headers=headers
            ) as response:
                
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"❌ Error exportando dashboard: {response.status}")
                    return {}
                    
        except Exception as e:
            print(f"❌ Error exportando dashboard: {e}")
            return {}
    
    async def import_dashboard(self, dashboard_config: Dict[str, Any]) -> bool:
        """Import dashboard configuration"""
        
        if not self.is_connected:
            print("❌ No conectado a Grafana")
            return False
        
        try:
            payload = {
                "dashboard": dashboard_config,
                "overwrite": True
            }
            
            headers = self._get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            async with self.session.post(
                f"{self.grafana_url}/api/dashboards/db",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status == 200:
                    print("✅ Dashboard importado exitosamente")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Error importando dashboard: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error importando dashboard: {e}")
            return False
    
    async def close(self):
        """Close Grafana integration system"""
        
        if self.session:
            await self.session.close()
        
        self.is_connected = False
        print("✅ Conexión con Grafana cerrada")

# Factory function
async def create_grafana_integration_system(config: Dict[str, Any]) -> GrafanaIntegrationSystem:
    """Create and initialize the Grafana integration system"""
    system = GrafanaIntegrationSystem(config)
    return system

if __name__ == "__main__":
    # Demo usage
    async def main():
        config = {
            'grafana_url': 'http://localhost:3000',
            'username': 'admin',
            'password': 'admin'
        }
        
        system = await create_grafana_integration_system(config)
        
        try:
            # Setup complete integration
            await system.setup_complete_grafana_integration()
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            await system.close()
    
    asyncio.run(main())
