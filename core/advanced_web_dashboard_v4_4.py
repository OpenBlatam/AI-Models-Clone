"""
Dashboard Web Avanzado con React v4.4
HeyGen AI - Sistema de Monitoreo Inteligente con IA Avanzada

Este sistema implementa:
- Dashboard web avanzado con componentes React-like
- Gráficos interactivos en tiempo real
- Gestión unificada de todos los sistemas v4.3
- Interfaz responsive y moderna
- WebSockets para actualizaciones en tiempo real
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import aiohttp
from aiohttp import web, WSMsgType
import random

class ReactLikeComponent:
    """Base class for React-like components"""
    
    def __init__(self, props: Dict[str, Any] = None):
        self.props = props or {}
        self.state = {}
        self.children = []
        self.component_id = f"component_{int(time.time() * 1000)}"
    
    def set_state(self, new_state: Dict[str, Any]):
        """Update component state"""
        self.state.update(new_state)
        return self.render()
    
    def render(self) -> str:
        """Render component to HTML"""
        raise NotImplementedError("Subclasses must implement render()")
    
    def add_child(self, child):
        """Add child component"""
        self.children.append(child)
        return self

class SystemStatusCard(ReactLikeComponent):
    """System status card component"""
    
    def render(self) -> str:
        system_name = self.props.get('name', 'Unknown System')
        status = self.state.get('status', 'unknown')
        health_score = self.state.get('health_score', 0.0)
        alerts = self.state.get('alerts', 0)
        
        status_color = {
            'running': 'success',
            'warning': 'warning', 
            'error': 'danger',
            'unknown': 'secondary'
        }.get(status, 'secondary')
        
        return f"""
        <div class="card system-status-card {status_color}" data-system="{system_name}">
            <div class="card-header">
                <h5 class="card-title">{system_name}</h5>
                <span class="badge badge-{status_color}">{status.upper()}</span>
            </div>
            <div class="card-body">
                <div class="health-indicator">
                    <div class="health-bar">
                        <div class="health-fill" style="width: {health_score * 100}%"></div>
                    </div>
                    <span class="health-score">{health_score:.1%}</span>
                </div>
                <div class="system-metrics">
                    <div class="metric">
                        <span class="metric-label">Alertas:</span>
                        <span class="metric-value">{alerts}</span>
                    </div>
                </div>
            </div>
        </div>
        """

class MetricsChart(ReactLikeComponent):
    """Interactive metrics chart component"""
    
    def render(self) -> str:
        chart_type = self.props.get('type', 'line')
        title = self.props.get('title', 'Metrics Chart')
        data = self.state.get('data', [])
        
        chart_id = f"chart_{self.component_id}"
        
        return f"""
        <div class="chart-container">
            <h4>{title}</h4>
            <canvas id="{chart_id}" width="400" height="200"></canvas>
            <div class="chart-controls">
                <button class="btn btn-sm btn-outline-primary" onclick="updateChart('{chart_id}', '1h')">1H</button>
                <button class="btn btn-sm btn-outline-primary" onclick="updateChart('{chart_id}', '6h')">6H</button>
                <button class="btn btn-sm btn-outline-primary" onclick="updateChart('{chart_id}', '24h')">24H</button>
            </div>
        </div>
        """

class AlertPanel(ReactLikeComponent):
    """Real-time alerts panel component"""
    
    def render(self) -> str:
        alerts = self.state.get('alerts', [])
        
        alerts_html = ""
        for alert in alerts[:5]:  # Show top 5 alerts
            severity = alert.get('severity', 'info')
            alerts_html += f"""
            <div class="alert alert-{severity} alert-dismissible">
                <strong>{alert.get('type', 'Alert')}:</strong> {alert.get('message', 'No message')}
                <button type="button" class="close" onclick="dismissAlert('{alert.get('id', '')}')">
                    <span>&times;</span>
                </button>
            </div>
            """
        
        return f"""
        <div class="alert-panel">
            <h4>Alertas en Tiempo Real</h4>
            <div class="alerts-container">
                {alerts_html if alerts_html else '<p class="text-muted">No hay alertas activas</p>'}
            </div>
        </div>
        """

class OptimizationPanel(ReactLikeComponent):
    """Optimization recommendations panel component"""
    
    def render(self) -> str:
        optimizations = self.state.get('optimizations', [])
        
        optimizations_html = ""
        for opt in optimizations[:3]:  # Show top 3 optimizations
            priority_color = {
                1: 'danger',
                2: 'warning',
                3: 'info'
            }.get(opt.get('priority', 3), 'info')
            
            optimizations_html += f"""
            <div class="optimization-item priority-{priority_color}">
                <div class="optimization-header">
                    <span class="priority-badge badge badge-{priority_color}">P{opt.get('priority', 3)}</span>
                    <strong>{opt.get('type', 'Optimization')}</strong>
                </div>
                <p>{opt.get('description', 'No description')}</p>
                <div class="optimization-metrics">
                    <span class="metric">Mejora: {opt.get('expected_improvement', 0):.1f}%</span>
                    <span class="metric">Esfuerzo: {opt.get('effort', 'medium')}</span>
                </div>
            </div>
            """
        
        return f"""
        <div class="optimization-panel">
            <h4>Recomendaciones de Optimización</h4>
            <div class="optimizations-container">
                {optimizations_html if optimizations_html else '<p class="text-muted">No hay optimizaciones pendientes</p>'}
            </div>
        </div>
        """

class AdvancedWebDashboard:
    """Advanced web dashboard with React-like components"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.components = {}
        self.websocket_connections = set()
        self.dashboard_data = {}
        self.is_running = False
        
        # Initialize dashboard components
        self._initialize_components()
        
        # Setup web server
        self.app = web.Application()
        self._setup_routes()
    
    def _initialize_components(self):
        """Initialize dashboard components"""
        
        # System status cards
        systems = ['prediction', 'cost_analysis', 'multicloud', 'security', 'performance', 'autoscaling']
        for system in systems:
            self.components[f"system_{system}"] = SystemStatusCard({
                'name': system.replace('_', ' ').title()
            })
        
        # Metrics charts
        self.components['cpu_chart'] = MetricsChart({
            'type': 'line',
            'title': 'Uso de CPU'
        })
        
        self.components['memory_chart'] = MetricsChart({
            'type': 'line', 
            'title': 'Uso de Memoria'
        })
        
        self.components['performance_chart'] = MetricsChart({
            'type': 'line',
            'title': 'Rendimiento del Sistema'
        })
        
        # Panels
        self.components['alert_panel'] = AlertPanel()
        self.components['optimization_panel'] = OptimizationPanel()
    
    def _setup_routes(self):
        """Setup web server routes"""
        
        # Main dashboard page
        self.app.router.add_get('/', self._dashboard_handler)
        
        # Static assets
        self.app.router.add_static('/static', 'static')
        
        # API endpoints
        self.app.router.add_get('/api/metrics', self._metrics_api_handler)
        self.app.router.add_get('/api/systems', self._systems_api_handler)
        self.app.router.add_get('/api/alerts', self._alerts_api_handler)
        self.app.router.add_get('/api/optimizations', self._optimizations_api_handler)
        
        # WebSocket endpoint
        self.app.router.add_get('/ws', self._websocket_handler)
    
    async def _dashboard_handler(self, request):
        """Main dashboard page handler"""
        
        html_content = self._generate_dashboard_html()
        return web.Response(text=html_content, content_type='text/html')
    
    async def _metrics_api_handler(self, request):
        """Metrics API endpoint"""
        
        metrics = self._generate_system_metrics()
        return web.json_response(metrics)
    
    async def _systems_api_handler(self, request):
        """Systems status API endpoint"""
        
        systems_status = {}
        for system_name, component in self.components.items():
            if system_name.startswith('system_'):
                systems_status[system_name] = component.state
        
        return web.json_response(systems_status)
    
    async def _alerts_api_handler(self, request):
        """Alerts API endpoint"""
        
        alerts = self.dashboard_data.get('alerts', [])
        return web.json_response(alerts)
    
    async def _optimizations_api_handler(self, request):
        """Optimizations API endpoint"""
        
        optimizations = self.dashboard_data.get('optimizations', [])
        return web.json_response(optimizations)
    
    async def _websocket_handler(self, request):
        """WebSocket handler for real-time updates"""
        
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websocket_connections.add(ws)
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self._handle_websocket_message(ws, data)
                elif msg.type == WSMsgType.ERROR:
                    print(f"WebSocket error: {ws.exception()}")
        finally:
            self.websocket_connections.discard(ws)
        
        return ws
    
    async def _handle_websocket_message(self, ws, data):
        """Handle WebSocket messages"""
        
        message_type = data.get('type')
        
        if message_type == 'subscribe_metrics':
            # Send initial metrics
            metrics = self._generate_system_metrics()
            await ws.send_json({
                'type': 'metrics_update',
                'data': metrics
            })
        
        elif message_type == 'get_system_status':
            # Send system status
            system_name = data.get('system')
            if system_name in self.components:
                component = self.components[system_name]
                await ws.send_json({
                    'type': 'system_status',
                    'system': system_name,
                    'data': component.state
                })
    
    def _generate_dashboard_html(self) -> str:
        """Generate complete dashboard HTML"""
        
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>HeyGen AI - Dashboard Unificado v4.4</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                {self._get_dashboard_styles()}
            </style>
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
                <div class="container-fluid">
                    <a class="navbar-brand" href="#">
                        <i class="fas fa-brain"></i> HeyGen AI Dashboard v4.4
                    </a>
                    <div class="navbar-nav ms-auto">
                        <span class="navbar-text">
                            <i class="fas fa-circle text-success"></i> Sistema Activo
                        </span>
                    </div>
                </div>
            </nav>
            
            <div class="container-fluid mt-4">
                <div class="row">
                    <div class="col-md-8">
                        <div class="row">
                            <div class="col-md-6">
                                {self.components['cpu_chart'].render()}
                            </div>
                            <div class="col-md-6">
                                {self.components['memory_chart'].render()}
                            </div>
                        </div>
                        <div class="row mt-4">
                            <div class="col-12">
                                {self.components['performance_chart'].render()}
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-4">
                        <div class="row">
                            <div class="col-12 mb-4">
                                {self.components['alert_panel'].render()}
                            </div>
                            <div class="col-12 mb-4">
                                {self.components['optimization_panel'].render()}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-12">
                        <h4>Estado de Sistemas</h4>
                        <div class="row">
                            {self._render_system_cards()}
                        </div>
                    </div>
                </div>
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script>
                {self._get_dashboard_scripts()}
            </script>
        </body>
        </html>
        """
    
    def _render_system_cards(self) -> str:
        """Render system status cards"""
        
        cards_html = ""
        for system_name, component in self.components.items():
            if system_name.startswith('system_'):
                cards_html += f"""
                <div class="col-md-4 mb-3">
                    {component.render()}
                </div>
                """
        
        return cards_html
    
    def _get_dashboard_styles(self) -> str:
        """Get dashboard CSS styles"""
        
        return """
        .system-status-card {
            transition: all 0.3s ease;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .system-status-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        
        .system-status-card.success {
            border-left: 4px solid #28a745;
        }
        
        .system-status-card.warning {
            border-left: 4px solid #ffc107;
        }
        
        .system-status-card.danger {
            border-left: 4px solid #dc3545;
        }
        
        .health-indicator {
            margin: 15px 0;
        }
        
        .health-bar {
            width: 100%;
            height: 8px;
            background-color: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .health-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }
        
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .alert-panel, .optimization-panel {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .optimization-item {
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .optimization-item.priority-danger {
            border-left-color: #dc3545;
            background-color: #f8d7da;
        }
        
        .optimization-item.priority-warning {
            border-left-color: #ffc107;
            background-color: #fff3cd;
        }
        
        .optimization-item.priority-info {
            border-left-color: #17a2b8;
            background-color: #d1ecf1;
        }
        
        .chart-controls {
            margin-top: 15px;
            text-align: center;
        }
        
        .chart-controls .btn {
            margin: 0 5px;
        }
        """
    
    def _get_dashboard_scripts(self) -> str:
        """Get dashboard JavaScript code"""
        
        return """
        // Initialize WebSocket connection
        let ws = new WebSocket('ws://' + window.location.host + '/ws');
        
        ws.onopen = function() {
            console.log('WebSocket connected');
            ws.send(JSON.stringify({type: 'subscribe_metrics'}));
        };
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };
        
        ws.onclose = function() {
            console.log('WebSocket disconnected');
            setTimeout(function() {
                location.reload();
            }, 5000);
        };
        
        function handleWebSocketMessage(data) {
            if (data.type === 'metrics_update') {
                updateDashboardMetrics(data.data);
            } else if (data.type === 'system_status') {
                updateSystemStatus(data.system, data.data);
            }
        }
        
        function updateDashboardMetrics(metrics) {
            // Update charts with new data
            updateChart('chart_cpu', metrics.cpu_usage);
            updateChart('chart_memory', metrics.memory_usage);
            updateChart('chart_performance', metrics.performance_score);
        }
        
        function updateSystemStatus(system, status) {
            // Update system status cards
            const card = document.querySelector(`[data-system="${system}"]`);
            if (card) {
                // Update card content based on new status
                console.log('Updating system status:', system, status);
            }
        }
        
        function updateChart(chartId, data) {
            // Chart update logic would go here
            console.log('Updating chart:', chartId, data);
        }
        
        function dismissAlert(alertId) {
            // Alert dismissal logic
            console.log('Dismissing alert:', alertId);
        }
        
        // Auto-refresh metrics every 30 seconds
        setInterval(function() {
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => updateDashboardMetrics(data))
                .catch(error => console.error('Error fetching metrics:', error));
        }, 30000);
        """
    
    def _generate_system_metrics(self) -> Dict[str, Any]:
        """Generate simulated system metrics for demo"""
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_usage': random.uniform(30, 90),
            'memory_usage': random.uniform(40, 95),
            'performance_score': random.uniform(0.7, 1.0),
            'active_systems': random.randint(4, 6),
            'total_alerts': random.randint(0, 5),
            'optimization_recommendations': random.randint(1, 8)
        }
    
    async def start(self, host: str = 'localhost', port: int = 8080):
        """Start the web dashboard"""
        
        if self.is_running:
            print("⚠️ El dashboard ya está ejecutándose")
            return
        
        self.is_running = True
        print(f"🚀 Iniciando Dashboard Web Avanzado v4.4 en http://{host}:{port}")
        
        # Start background tasks
        asyncio.create_task(self._update_dashboard_data())
        asyncio.create_task(self._broadcast_updates())
        
        # Start web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        print(f"✅ Dashboard iniciado en http://{host}:{port}")
        
        # Keep running
        try:
            while self.is_running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await self.stop()
    
    async def stop(self):
        """Stop the web dashboard"""
        
        print("🛑 Deteniendo Dashboard Web Avanzado v4.4...")
        self.is_running = False
        
        # Close WebSocket connections
        for ws in self.websocket_connections:
            await ws.close()
        
        print("✅ Dashboard detenido")
    
    async def _update_dashboard_data(self):
        """Update dashboard data periodically"""
        
        while self.is_running:
            try:
                # Update system status
                for system_name, component in self.components.items():
                    if system_name.startswith('system_'):
                        component.set_state({
                            'status': random.choice(['running', 'warning', 'error']),
                            'health_score': random.uniform(0.6, 1.0),
                            'alerts': random.randint(0, 3)
                        })
                
                # Update charts data
                self.components['cpu_chart'].set_state({
                    'data': [random.uniform(30, 90) for _ in range(20)]
                })
                
                self.components['memory_chart'].set_state({
                    'data': [random.uniform(40, 95) for _ in range(20)]
                })
                
                self.components['performance_chart'].set_state({
                    'data': [random.uniform(0.7, 1.0) for _ in range(20)]
                })
                
                # Update alerts
                self.dashboard_data['alerts'] = [
                    {
                        'id': f"alert_{int(time.time())}",
                        'type': 'Performance',
                        'severity': 'warning',
                        'message': 'CPU usage above threshold'
                    }
                ] if random.random() < 0.3 else []
                
                # Update optimizations
                self.dashboard_data['optimizations'] = [
                    {
                        'type': 'Cost Optimization',
                        'description': 'Reduce underutilized resources',
                        'priority': random.randint(1, 3),
                        'expected_improvement': random.uniform(10, 30),
                        'effort': random.choice(['low', 'medium', 'high'])
                    }
                ] if random.random() < 0.4 else []
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                print(f"Error actualizando datos del dashboard: {e}")
                await asyncio.sleep(15)
    
    async def _broadcast_updates(self):
        """Broadcast updates to WebSocket clients"""
        
        while self.is_running:
            try:
                if self.websocket_connections:
                    # Send metrics update
                    metrics = self._generate_system_metrics()
                    update_message = {
                        'type': 'metrics_update',
                        'data': metrics
                    }
                    
                    # Broadcast to all connected clients
                    for ws in self.websocket_connections:
                        try:
                            await ws.send_json(update_message)
                        except Exception as e:
                            print(f"Error sending to WebSocket: {e}")
                            self.websocket_connections.discard(ws)
                
                await asyncio.sleep(5)  # Broadcast every 5 seconds
                
            except Exception as e:
                print(f"Error broadcasting updates: {e}")
                await asyncio.sleep(10)

# Factory function
async def create_advanced_web_dashboard(config: Dict[str, Any]) -> AdvancedWebDashboard:
    """Create and initialize the advanced web dashboard"""
    dashboard = AdvancedWebDashboard(config)
    return dashboard

if __name__ == "__main__":
    # Demo usage
    async def main():
        config = {
            'dashboard': {
                'host': 'localhost',
                'port': 8080,
                'refresh_interval': 10
            }
        }
        
        dashboard = await create_advanced_web_dashboard(config)
        
        try:
            await dashboard.start()
        except KeyboardInterrupt:
            await dashboard.stop()
    
    asyncio.run(main())
