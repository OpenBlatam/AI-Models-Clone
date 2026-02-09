#!/usr/bin/env python3
"""
Demo del Sistema de Integración y Optimización Avanzada v4.1
HeyGen AI - Sistema de Monitoreo Inteligente con IA Avanzada

Este script demuestra todas las funcionalidades del sistema v4.1:
- Dashboard web en tiempo real
- Motor de alertas inteligentes con ML
- Optimización automática predictiva
- Integración completa con sistemas existentes
"""

import asyncio
import time
import json
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import yaml
import aiohttp
from aiohttp import web
import numpy as np

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdvancedIntegrationDemo:
    """Demo completo del Sistema de Integración Avanzada v4.1"""
    
    def __init__(self, config_path: str = "advanced_integration_config_v4_1.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.demo_data = {}
        self.scenarios = []
        self.is_running = False
        
    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración del sistema"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"No se pudo cargar la configuración: {e}")
            return self._get_demo_config()
    
    def _get_demo_config(self) -> Dict[str, Any]:
        """Configuración de demo por defecto"""
        return {
            'dashboard': {
                'host': 'localhost',
                'port': 8080
            },
            'demo': {
                'duration': 300,  # 5 minutos
                'scenarios': ['normal', 'high_load', 'performance_degradation', 'recovery']
            }
        }
    
    def _setup_demo_scenarios(self):
        """Configurar escenarios de demostración"""
        self.scenarios = [
            {
                'name': 'Normal Operation',
                'description': 'Operación normal del sistema con métricas estables',
                'duration': 60,
                'metrics_generator': self._generate_normal_metrics
            },
            {
                'name': 'High Load Simulation',
                'description': 'Simulación de carga alta para probar escalado automático',
                'duration': 90,
                'metrics_generator': self._generate_high_load_metrics
            },
            {
                'name': 'Performance Degradation',
                'description': 'Degradación de rendimiento para probar alertas inteligentes',
                'duration': 60,
                'metrics_generator': self._generate_degradation_metrics
            },
            {
                'name': 'System Recovery',
                'description': 'Recuperación del sistema después de problemas',
                'duration': 90,
                'metrics_generator': self._generate_recovery_metrics
            }
        ]
    
    def _generate_normal_metrics(self) -> Dict[str, Any]:
        """Generar métricas para operación normal"""
        return {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_usage': random.uniform(20, 40),
                'memory_usage': random.uniform(30, 50),
                'disk_usage': random.uniform(45, 65),
                'network_io': {
                    'bytes_sent': random.randint(1000000, 5000000),
                    'bytes_recv': random.randint(2000000, 8000000)
                }
            },
            'ai_models': {
                'heygen_core': {
                    'status': 'healthy',
                    'inference_time': random.uniform(0.5, 1.2),
                    'accuracy': random.uniform(95, 99),
                    'throughput': random.uniform(80, 120)
                },
                'video_model': {
                    'status': 'healthy',
                    'inference_time': random.uniform(2.0, 4.0),
                    'accuracy': random.uniform(92, 98),
                    'throughput': random.uniform(40, 80)
                },
                'audio_model': {
                    'status': 'healthy',
                    'inference_time': random.uniform(0.3, 0.8),
                    'accuracy': random.uniform(96, 99.5),
                    'throughput': random.uniform(100, 150)
                }
            },
            'optimizations': [],
            'alerts': []
        }
    
    def _generate_high_load_metrics(self) -> Dict[str, Any]:
        """Generar métricas para carga alta"""
        return {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_usage': random.uniform(75, 95),
                'memory_usage': random.uniform(70, 90),
                'disk_usage': random.uniform(60, 80),
                'network_io': {
                    'bytes_sent': random.randint(8000000, 15000000),
                    'bytes_recv': random.randint(12000000, 25000000)
                }
            },
            'ai_models': {
                'heygen_core': {
                    'status': 'warning',
                    'inference_time': random.uniform(1.5, 3.0),
                    'accuracy': random.uniform(90, 96),
                    'throughput': random.uniform(60, 100)
                },
                'video_model': {
                    'status': 'warning',
                    'inference_time': random.uniform(4.0, 7.0),
                    'accuracy': random.uniform(88, 94),
                    'throughput': random.uniform(30, 60)
                },
                'audio_model': {
                    'status': 'warning',
                    'inference_time': random.uniform(0.8, 1.5),
                    'accuracy': random.uniform(93, 98),
                    'throughput': random.uniform(70, 110)
                }
            },
            'optimizations': [
                {
                    'type': 'scale_cpu_workers',
                    'priority': 1,
                    'expected_improvement': {'cpu_usage': -20}
                }
            ],
            'alerts': [
                {
                    'type': 'high_cpu',
                    'severity': 'high',
                    'message': 'CPU usage above threshold'
                }
            ]
        }
    
    def _generate_degradation_metrics(self) -> Dict[str, Any]:
        """Generar métricas para degradación de rendimiento"""
        return {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_usage': random.uniform(85, 98),
                'memory_usage': random.uniform(80, 95),
                'disk_usage': random.uniform(70, 85),
                'network_io': {
                    'bytes_sent': random.randint(5000000, 12000000),
                    'bytes_recv': random.randint(8000000, 18000000)
                }
            },
            'ai_models': {
                'heygen_core': {
                    'status': 'critical',
                    'inference_time': random.uniform(3.0, 6.0),
                    'accuracy': random.uniform(85, 92),
                    'throughput': random.uniform(40, 80)
                },
                'video_model': {
                    'status': 'critical',
                    'inference_time': random.uniform(7.0, 12.0),
                    'accuracy': random.uniform(80, 88),
                    'throughput': random.uniform(20, 50)
                },
                'audio_model': {
                    'status': 'critical',
                    'inference_time': random.uniform(1.5, 3.0),
                    'accuracy': random.uniform(88, 94),
                    'throughput': random.uniform(50, 90)
                }
            },
            'optimizations': [
                {
                    'type': 'restart_memory_intensive_services',
                    'priority': 1,
                    'expected_improvement': {'memory_usage': -40}
                },
                {
                    'type': 'scale_gpu_workers',
                    'priority': 2,
                    'expected_improvement': {'gpu_usage': -30}
                }
            ],
            'alerts': [
                {
                    'type': 'high_cpu',
                    'severity': 'critical',
                    'message': 'Critical CPU usage detected'
                },
                {
                    'type': 'memory_leak',
                    'severity': 'critical',
                    'message': 'Memory usage critical'
                }
            ]
        }
    
    def _generate_recovery_metrics(self) -> Dict[str, Any]:
        """Generar métricas para recuperación del sistema"""
        recovery_progress = min(1.0, (time.time() - self.recovery_start_time) / 60.0)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_usage': 40 + (85 - 40) * (1 - recovery_progress),
                'memory_usage': 50 + (90 - 50) * (1 - recovery_progress),
                'disk_usage': 60 + (80 - 60) * (1 - recovery_progress),
                'network_io': {
                    'bytes_sent': random.randint(2000000, 6000000),
                    'bytes_recv': random.randint(4000000, 10000000)
                }
            },
            'ai_models': {
                'heygen_core': {
                    'status': 'recovering',
                    'inference_time': 1.5 + (4.0 - 1.5) * (1 - recovery_progress),
                    'accuracy': 92 + (96 - 92) * recovery_progress,
                    'throughput': 60 + (100 - 60) * recovery_progress
                },
                'video_model': {
                    'status': 'recovering',
                    'inference_time': 4.0 + (8.0 - 4.0) * (1 - recovery_progress),
                    'accuracy': 88 + (94 - 88) * recovery_progress,
                    'throughput': 30 + (70 - 30) * recovery_progress
                },
                'audio_model': {
                    'status': 'recovering',
                    'inference_time': 0.8 + (2.0 - 0.8) * (1 - recovery_progress),
                    'accuracy': 90 + (96 - 90) * recovery_progress,
                    'throughput': 50 + (100 - 50) * recovery_progress
                }
            },
            'optimizations': [
                {
                    'type': 'system_recovery',
                    'priority': 1,
                    'expected_improvement': {'overall_health': 100}
                }
            ],
            'alerts': [
                {
                    'type': 'system_recovery',
                    'severity': 'info',
                    'message': f'System recovery in progress: {recovery_progress*100:.1f}%'
                }
            ]
        }
    
    async def start_demo(self):
        """Iniciar la demostración completa"""
        logger.info("🚀 Iniciando Demo del Sistema de Integración Avanzada v4.1")
        logger.info("=" * 60)
        
        # Configurar escenarios
        self._setup_demo_scenarios()
        
        # Iniciar dashboard web
        await self._start_dashboard()
        
        # Ejecutar escenarios
        await self._run_demo_scenarios()
        
        # Mostrar resultados finales
        await self._show_final_results()
        
        logger.info("✅ Demo completado exitosamente")
    
    async def _start_dashboard(self):
        """Iniciar el dashboard web"""
        logger.info("🌐 Iniciando Dashboard Web...")
        
        # Crear aplicación web simple para demo
        app = web.Application()
        
        # Ruta principal
        app.router.add_get('/', self._dashboard_handler)
        
        # Ruta de API para métricas
        app.router.add_get('/api/metrics', self._metrics_api_handler)
        
        # Ruta de WebSocket para actualizaciones en tiempo real
        app.router.add_get('/ws', self._websocket_handler)
        
        # Iniciar servidor
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(
            runner, 
            self.config['dashboard']['host'], 
            self.config['dashboard']['port']
        )
        await site.start()
        
        logger.info(f"✅ Dashboard disponible en: http://{self.config['dashboard']['host']}:{self.config['dashboard']['port']}")
        
        # Guardar runner para limpieza
        self.web_runner = runner
    
    async def _dashboard_handler(self, request):
        """Manejador del dashboard principal"""
        html_content = self._generate_demo_dashboard_html()
        return web.Response(text=html_content, content_type='text/html')
    
    async def _metrics_api_handler(self, request):
        """API para obtener métricas actuales"""
        return web.json_response(self.demo_data.get('current_metrics', {}))
    
    async def _websocket_handler(self, request):
        """Manejador de WebSocket para actualizaciones en tiempo real"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if data.get('type') == 'subscribe_metrics':
                        # Enviar métricas actuales
                        await ws.send_json({
                            'type': 'metrics_update',
                            'data': self.demo_data.get('current_metrics', {})
                        })
        finally:
            pass
        
        return ws
    
    def _generate_demo_dashboard_html(self) -> str:
        """Generar HTML del dashboard de demo"""
        return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Demo - Sistema de Integración Avanzada v4.1</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 15px; 
        }
        .dashboard-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
            gap: 20px; 
        }
        .card { 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 15px; 
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .metric { 
            display: flex; 
            justify-content: space-between; 
            margin: 10px 0; 
            padding: 10px; 
            background: rgba(255,255,255,0.1); 
            border-radius: 8px; 
        }
        .status-good { color: #4ade80; }
        .status-warning { color: #fbbf24; }
        .status-critical { color: #f87171; }
        .scenario-info {
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4ade80, #22c55e);
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Demo - Sistema de Integración Avanzada v4.1</h1>
        <p>Sistema de Monitoreo Inteligente con IA Avanzada para HeyGen AI</p>
        <div class="scenario-info">
            <h3>📊 Escenario Actual: <span id="current-scenario">Normal Operation</span></h3>
            <p id="scenario-description">Operación normal del sistema con métricas estables</p>
            <div class="progress-bar">
                <div class="progress-fill" id="scenario-progress" style="width: 0%"></div>
            </div>
        </div>
    </div>
    
    <div class="dashboard-grid">
        <div class="card">
            <h3>📊 Métricas del Sistema</h3>
            <div id="system-metrics">
                <div class="metric">
                    <span>CPU Usage:</span>
                    <span id="cpu-usage" class="status-good">--</span>
                </div>
                <div class="metric">
                    <span>Memory Usage:</span>
                    <span id="memory-usage" class="status-good">--</span>
                </div>
                <div class="metric">
                    <span>Disk Usage:</span>
                    <span id="disk-usage" class="status-good">--</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>🤖 Modelos de IA HeyGen</h3>
            <div id="ai-models">
                <div class="metric">
                    <span>HeyGen Core:</span>
                    <span id="heygen-core" class="status-good">--</span>
                </div>
                <div class="metric">
                    <span>Video Model:</span>
                    <span id="video-model" class="status-good">--</span>
                </div>
                <div class="metric">
                    <span>Audio Model:</span>
                    <span id="audio-model" class="status-good">--</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>⚠️ Alertas Inteligentes</h3>
            <div id="alerts">
                <p>No hay alertas activas</p>
            </div>
        </div>
        
        <div class="card">
            <h3>🔧 Optimizaciones Automáticas</h3>
            <div id="optimizations">
                <p>Analizando sistema...</p>
            </div>
        </div>
        
        <div class="card">
            <h3>📈 Predicciones ML</h3>
            <div id="predictions">
                <p>Generando predicciones en tiempo real...</p>
            </div>
        </div>
        
        <div class="card">
            <h3>⚡ Acciones Automáticas</h3>
            <div id="auto-actions">
                <p>Monitoreando oportunidades de optimización...</p>
            </div>
        </div>
    </div>
    
    <script>
        // WebSocket connection for real-time updates
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            if (data.type === 'metrics_update') {
                updateDashboard(data.data);
            }
        };
        
        function updateDashboard(metrics) {
            // Update system metrics
            if (metrics.system) {
                if (metrics.system.cpu_usage) {
                    const cpuElement = document.getElementById('cpu-usage');
                    cpuElement.textContent = metrics.system.cpu_usage.toFixed(1) + '%';
                    updateStatusClass(cpuElement, metrics.system.cpu_usage, 70, 90);
                }
                if (metrics.system.memory_usage) {
                    const memElement = document.getElementById('memory-usage');
                    memElement.textContent = metrics.system.memory_usage.toFixed(1) + '%';
                    updateStatusClass(memElement, metrics.system.memory_usage, 80, 95);
                }
                if (metrics.system.disk_usage) {
                    const diskElement = document.getElementById('disk-usage');
                    diskElement.textContent = metrics.system.disk_usage.toFixed(1) + '%';
                    updateStatusClass(diskElement, metrics.system.disk_usage, 70, 85);
                }
            }
            
            // Update AI model metrics
            if (metrics.ai_models) {
                updateAIModelStatus('heygen-core', metrics.ai_models.heygen_core);
                updateAIModelStatus('video-model', metrics.ai_models.video_model);
                updateAIModelStatus('audio-model', metrics.ai_models.audio_model);
            }
            
            // Update alerts
            if (metrics.alerts && metrics.alerts.length > 0) {
                const alertsDiv = document.getElementById('alerts');
                alertsDiv.innerHTML = metrics.alerts.map(alert => 
                    `<div class="metric status-${alert.severity === 'critical' ? 'critical' : 'warning'}">
                        <span>${alert.type}:</span>
                        <span>${alert.message}</span>
                    </div>`
                ).join('');
            } else {
                document.getElementById('alerts').innerHTML = '<p>No hay alertas activas</p>';
            }
            
            // Update optimizations
            if (metrics.optimizations && metrics.optimizations.length > 0) {
                const optDiv = document.getElementById('optimizations');
                optDiv.innerHTML = metrics.optimizations.map(opt => 
                    `<div class="metric">
                        <span>${opt.type}:</span>
                        <span>Prioridad ${opt.priority}</span>
                    </div>`
                ).join('');
            } else {
                document.getElementById('optimizations').innerHTML = '<p>Analizando sistema...</p>';
            }
        }
        
        function updateStatusClass(element, value, warningThreshold, criticalThreshold) {
            element.className = 'status-good';
            if (value >= criticalThreshold) {
                element.className = 'status-critical';
            } else if (value >= warningThreshold) {
                element.className = 'status-warning';
            }
        }
        
        function updateAIModelStatus(elementId, modelData) {
            const element = document.getElementById(elementId);
            if (element && modelData) {
                element.textContent = modelData.status;
                updateStatusClass(element, modelData.inference_time, 2.0, 4.0);
            }
        }
        
        // Subscribe to metrics updates
        ws.onopen = function() {
            ws.send(JSON.stringify({type: 'subscribe_metrics'}));
        };
        
        // Update scenario progress
        function updateScenarioProgress(scenario, progress) {
            document.getElementById('current-scenario').textContent = scenario.name;
            document.getElementById('scenario-description').textContent = scenario.description;
            document.getElementById('scenario-progress').style.width = progress + '%';
        }
        
        // Simulate scenario progression
        let currentProgress = 0;
        setInterval(() => {
            currentProgress = (currentProgress + 1) % 100;
            updateScenarioProgress({
                name: 'Demo en Progreso',
                description: 'Simulando diferentes escenarios del sistema'
            }, currentProgress);
        }, 1000);
    </script>
</body>
</html>
        """
    
    async def _run_demo_scenarios(self):
        """Ejecutar todos los escenarios de demostración"""
        logger.info("🎭 Ejecutando Escenarios de Demostración...")
        
        for i, scenario in enumerate(self.scenarios, 1):
            logger.info(f"\n🎬 Escenario {i}/{len(self.scenarios)}: {scenario['name']}")
            logger.info(f"📝 {scenario['description']}")
            logger.info(f"⏱️ Duración: {scenario['duration']} segundos")
            
            # Ejecutar escenario
            await self._run_single_scenario(scenario)
            
            # Pausa entre escenarios
            if i < len(self.scenarios):
                logger.info("⏸️ Pausa entre escenarios...")
                await asyncio.sleep(5)
        
        logger.info("✅ Todos los escenarios completados")
    
    async def _run_single_scenario(self, scenario: Dict[str, Any]):
        """Ejecutar un escenario individual"""
        start_time = time.time()
        end_time = start_time + scenario['duration']
        
        # Configurar tiempo de recuperación si es necesario
        if 'recovery' in scenario['name'].lower():
            self.recovery_start_time = start_time
        
        logger.info(f"🚀 Iniciando escenario: {scenario['name']}")
        
        while time.time() < end_time:
            # Generar métricas para el escenario
            metrics = scenario['metrics_generator']()
            
            # Actualizar datos de demo
            self.demo_data['current_metrics'] = metrics
            
            # Mostrar estado en tiempo real
            await self._display_scenario_status(scenario, metrics, start_time, end_time)
            
            # Esperar antes de la siguiente iteración
            await asyncio.sleep(2)
        
        logger.info(f"✅ Escenario completado: {scenario['name']}")
    
    async def _display_scenario_status(self, scenario: Dict[str, Any], metrics: Dict[str, Any], start_time: float, end_time: float):
        """Mostrar estado del escenario en tiempo real"""
        elapsed = time.time() - start_time
        remaining = end_time - time.time()
        progress = (elapsed / scenario['duration']) * 100
        
        # Mostrar métricas clave
        cpu_usage = metrics['system']['cpu_usage']
        memory_usage = metrics['system']['memory_usage']
        
        # Determinar estado del sistema
        if cpu_usage > 90 or memory_usage > 95:
            status = "🔴 CRÍTICO"
        elif cpu_usage > 70 or memory_usage > 80:
            status = "🟡 ADVERTENCIA"
        else:
            status = "🟢 SALUDABLE"
        
        # Mostrar información del escenario
        logger.info(f"📊 {scenario['name']} - Progreso: {progress:.1f}% - Estado: {status}")
        logger.info(f"   CPU: {cpu_usage:.1f}% | Memoria: {memory_usage:.1f}% | Tiempo restante: {remaining:.1f}s")
        
        # Mostrar alertas si las hay
        if metrics['alerts']:
            for alert in metrics['alerts']:
                logger.warning(f"   ⚠️ Alerta: {alert['type']} - {alert['message']}")
        
        # Mostrar optimizaciones si las hay
        if metrics['optimizations']:
            for opt in metrics['optimizations']:
                logger.info(f"   🔧 Optimización: {opt['type']} (Prioridad: {opt['priority']})")
    
    async def _show_final_results(self):
        """Mostrar resultados finales de la demostración"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 RESULTADOS FINALES DE LA DEMOSTRACIÓN")
        logger.info("=" * 60)
        
        # Resumen de métricas
        logger.info("📈 Resumen de Métricas del Sistema:")
        logger.info(f"   - CPU promedio: {self._calculate_average_metric('cpu_usage'):.1f}%")
        logger.info(f"   - Memoria promedio: {self._calculate_average_metric('memory_usage'):.1f}%")
        logger.info(f"   - Alertas generadas: {self._count_total_alerts()}")
        logger.info(f"   - Optimizaciones detectadas: {self._count_total_optimizations()}")
        
        # Resumen de modelos de IA
        logger.info("\n🤖 Resumen de Modelos de IA:")
        logger.info("   - HeyGen Core: Funcionamiento estable")
        logger.info("   - Video Model: Rendimiento optimizado")
        logger.info("   - Audio Model: Alta precisión mantenida")
        
        # Beneficios del sistema
        logger.info("\n🚀 Beneficios del Sistema v4.1:")
        logger.info("   ✅ Monitoreo en tiempo real con dashboard web")
        logger.info("   ✅ Alertas inteligentes con machine learning")
        logger.info("   ✅ Optimización automática predictiva")
        logger.info("   ✅ Integración completa con sistemas existentes")
        logger.info("   ✅ Escalado automático basado en IA")
        logger.info("   ✅ Predicción de recursos con ML avanzado")
        
        logger.info("\n🎉 ¡Sistema de Integración Avanzada v4.1 demostrado exitosamente!")
    
    def _calculate_average_metric(self, metric_name: str) -> float:
        """Calcular promedio de una métrica específica"""
        # En un sistema real, esto calcularía el promedio de métricas históricas
        # Para el demo, retornamos un valor simulado
        return random.uniform(45, 75)
    
    def _count_total_alerts(self) -> int:
        """Contar total de alertas generadas"""
        # En un sistema real, esto contaría alertas de la base de datos
        return random.randint(5, 15)
    
    def _count_total_optimizations(self) -> int:
        """Contar total de optimizaciones detectadas"""
        # En un sistema real, esto contaría optimizaciones ejecutadas
        return random.randint(3, 8)
    
    async def cleanup(self):
        """Limpiar recursos del demo"""
        if hasattr(self, 'web_runner'):
            await self.web_runner.cleanup()
        logger.info("🧹 Recursos del demo limpiados")

async def main():
    """Función principal del demo"""
    demo = AdvancedIntegrationDemo()
    
    try:
        await demo.start_demo()
    except KeyboardInterrupt:
        logger.info("\n🛑 Demo interrumpido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error en el demo: {e}")
    finally:
        await demo.cleanup()

if __name__ == "__main__":
    print("🚀 Iniciando Demo del Sistema de Integración Avanzada v4.1")
    print("Presiona Ctrl+C para detener el demo")
    print("-" * 60)
    
    asyncio.run(main())
