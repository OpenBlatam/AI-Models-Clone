"""
🎮 Demo con Interfaz Gradio para el Sistema de Gestión de Recursos Inteligente
Interfaz interactiva para monitorear y controlar el sistema de recursos
"""

import asyncio
import gradio as gr
import time
import threading
import json
from typing import Dict, Any, List
import psutil
import numpy as np

# Importar el sistema de gestión de recursos
from intelligent_resource_manager import (
    IntelligentResourceOrchestrator,
    ResourceType, ResourceConfig, ResourceMetrics, OptimizationAction
)

class ResourceManagerDemo:
    """Demo del sistema de gestión de recursos con interfaz Gradio."""
    
    def __init__(self):
        self.orchestrator = IntelligentResourceOrchestrator()
        self.running = False
        self.monitoring_thread = None
        self.metrics_history = {
            'cpu_memory': [],
            'gpu': []
        }
        self.optimization_history = []
        self.system_status = "Detenido"
        
    async def start_system(self):
        """Iniciar el sistema de gestión de recursos."""
        try:
            await self.orchestrator.start()
            self.running = True
            self.system_status = "Ejecutando"
            
            # Iniciar monitoreo en hilo separado
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            return "✅ Sistema iniciado exitosamente", self.system_status
        except Exception as e:
            return f"❌ Error al iniciar: {str(e)}", "Error"
    
    async def stop_system(self):
        """Detener el sistema de gestión de recursos."""
        try:
            await self.orchestrator.stop()
            self.running = False
            self.system_status = "Detenido"
            return "✅ Sistema detenido exitosamente", self.system_status
        except Exception as e:
            return f"❌ Error al detener: {str(e)}", self.system_status
    
    def _monitoring_loop(self):
        """Loop de monitoreo en hilo separado."""
        while self.running:
            try:
                # Crear evento para ejecutar async en el hilo principal
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Recolectar métricas
                metrics = loop.run_until_complete(self.orchestrator.collect_all_metrics())
                
                # Actualizar historial
                for resource_name, metric in metrics.items():
                    if resource_name in self.metrics_history:
                        self.metrics_history[resource_name].append({
                            'timestamp': time.time(),
                            'current_usage': metric.current_usage,
                            'prediction': metric.prediction,
                            'trend': metric.trend
                        })
                        
                        # Mantener solo últimas 50 métricas
                        if len(self.metrics_history[resource_name]) > 50:
                            self.metrics_history[resource_name] = self.metrics_history[resource_name][-50:]
                
                # Verificar si hay optimizaciones en cola
                if self.orchestrator.optimization_queue:
                    self.system_status = f"Ejecutando ({len(self.orchestrator.optimization_queue)} optimizaciones en cola)"
                else:
                    self.system_status = "Ejecutando"
                
                time.sleep(5)  # Actualizar cada 5 segundos
                
            except Exception as e:
                print(f"Error en monitoreo: {e}")
                time.sleep(10)
    
    async def get_current_metrics(self):
        """Obtener métricas actuales del sistema."""
        if not self.running:
            return "Sistema no está ejecutándose", {}, {}
        
        try:
            # Obtener métricas actuales
            metrics = await self.orchestrator.collect_all_metrics()
            
            # Formatear métricas para display
            formatted_metrics = {}
            for resource_name, metric in metrics.items():
                formatted_metrics[resource_name] = {
                    'Uso Actual': f"{metric.current_usage:.2%}",
                    'Uso Pico': f"{metric.peak_usage:.2%}",
                    'Uso Promedio': f"{metric.average_usage:.2%}",
                    'Tendencia': f"{metric.trend:+.3f}",
                    'Predicción': f"{metric.prediction:.2%}",
                    'Timestamp': time.strftime('%H:%M:%S', time.localtime(metric.timestamp))
                }
            
            # Obtener resumen del sistema
            summary = await self.orchestrator.get_resource_summary()
            
            return "✅ Métricas actualizadas", formatted_metrics, summary
            
        except Exception as e:
            return f"❌ Error obteniendo métricas: {str(e)}", {}, {}
    
    async def run_optimization(self):
        """Ejecutar optimización de recursos."""
        if not self.running:
            return "Sistema no está ejecutándose", []
        
        try:
            # Ejecutar optimización
            optimizations = await self.orchestrator.optimize_all_resources()
            
            # Formatear resultados
            formatted_optimizations = []
            for resource_name, action in optimizations.items():
                formatted_optimizations.append({
                    'Recurso': resource_name,
                    'Acción': action.action_type,
                    'Prioridad': action.priority,
                    'Mejora Esperada': f"{action.expected_improvement:.2%}",
                    'Parámetros': json.dumps(action.parameters, indent=2)
                })
                
                # Agregar al historial
                self.optimization_history.append({
                    'timestamp': time.time(),
                    'resource': resource_name,
                    'action': action.action_type,
                    'priority': action.priority
                })
                
                # Mantener solo últimas 20 optimizaciones
                if len(self.optimization_history) > 20:
                    self.optimization_history = self.optimization_history[-20:]
            
            return f"✅ Optimización ejecutada para {len(optimizations)} recursos", formatted_optimizations
            
        except Exception as e:
            return f"❌ Error en optimización: {str(e)}", []
    
    def get_system_info(self):
        """Obtener información del sistema."""
        try:
            # Información del sistema
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            
            system_info = {
                'CPU': {
                    'Núcleos': cpu_count,
                    'Uso Actual': f"{psutil.cpu_percent(interval=1):.1f}%",
                    'Frecuencia': f"{psutil.cpu_freq().current:.0f} MHz" if psutil.cpu_freq() else "N/A"
                },
                'Memoria': {
                    'Total': f"{memory.total / (1024**3):.1f} GB",
                    'Disponible': f"{memory.available / (1024**3):.1f} GB",
                    'Uso': f"{memory.percent:.1f}%"
                },
                'Sistema': {
                    'Estado': self.system_status,
                    'Recursos Monitoreados': len(self.orchestrator.resource_managers),
                    'Optimizaciones en Cola': len(self.orchestrator.optimization_queue),
                    'Total de Optimizaciones': sum(
                        len(manager.optimization_history) 
                        for manager in self.orchestrator.resource_managers.values()
                    )
                }
            }
            
            return system_info
            
        except Exception as e:
            return {"Error": f"Error obteniendo información: {str(e)}"}
    
    def get_metrics_chart_data(self):
        """Obtener datos para gráficos de métricas."""
        try:
            # Preparar datos para gráficos
            chart_data = {}
            
            for resource_name, metrics_list in self.metrics_history.items():
                if metrics_list:
                    timestamps = [m['timestamp'] for m in metrics_list]
                    current_usage = [m['current_usage'] * 100 for m in metrics_list]
                    predictions = [m['prediction'] * 100 for m in metrics_list]
                    
                    chart_data[resource_name] = {
                        'timestamps': timestamps,
                        'current_usage': current_usage,
                        'predictions': predictions
                    }
            
            return chart_data
            
        except Exception as e:
            return {}

def create_demo_interface():
    """Crear interfaz de demostración."""
    demo = ResourceManagerDemo()
    
    with gr.Blocks(
        title="🚀 Sistema de Gestión de Recursos Inteligente",
        theme=gr.themes.Soft(),
        css="""
        .main-header { text-align: center; margin-bottom: 20px; }
        .metric-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; }
        .status-running { color: #28a745; font-weight: bold; }
        .status-stopped { color: #dc3545; font-weight: bold; }
        .status-error { color: #ffc107; font-weight: bold; }
        """
    ) as interface:
        
        # Header
        gr.HTML("""
        <div class="main-header">
            <h1>🚀 Sistema de Gestión de Recursos Inteligente</h1>
            <p>Sistema avanzado de monitoreo y optimización automática de recursos del sistema</p>
        </div>
        """)
        
        with gr.Row():
            # Panel de control
            with gr.Column(scale=1):
                gr.Markdown("### 🎮 **Panel de Control**")
                
                start_btn = gr.Button("▶️ Iniciar Sistema", variant="primary", size="lg")
                stop_btn = gr.Button("⏹️ Detener Sistema", variant="stop", size="lg")
                refresh_btn = gr.Button("🔄 Actualizar Métricas", size="lg")
                optimize_btn = gr.Button("🔧 Ejecutar Optimización", size="lg")
                
                status_output = gr.Textbox(
                    label="Estado del Sistema",
                    value="Detenido",
                    interactive=False,
                    elem_classes=["status-stopped"]
                )
                
                message_output = gr.Textbox(
                    label="Mensajes",
                    value="Sistema listo para iniciar",
                    interactive=False,
                    lines=3
                )
            
            # Información del sistema
            with gr.Column(scale=1):
                gr.Markdown("### 💻 **Información del Sistema**")
                
                system_info_output = gr.JSON(
                    label="Información del Sistema",
                    value={}
                )
        
        with gr.Row():
            # Métricas en tiempo real
            with gr.Column(scale=1):
                gr.Markdown("### 📊 **Métricas en Tiempo Real**")
                
                metrics_output = gr.JSON(
                    label="Métricas de Recursos",
                    value={}
                )
            
            # Resumen del sistema
            with gr.Column(scale=1):
                gr.Markdown("### 📋 **Resumen del Sistema**")
                
                summary_output = gr.JSON(
                    label="Resumen General",
                    value={}
                )
        
        with gr.Row():
            # Historial de optimizaciones
            with gr.Column(scale=2):
                gr.Markdown("### 🔧 **Historial de Optimizaciones**")
                
                optimization_output = gr.Dataframe(
                    headers=["Recurso", "Acción", "Prioridad", "Mejora Esperada", "Parámetros"],
                    label="Últimas Optimizaciones",
                    interactive=False
                )
        
        # Eventos
        start_btn.click(
            demo.start_system,
            outputs=[message_output, status_output]
        )
        
        stop_btn.click(
            demo.stop_system,
            outputs=[message_output, status_output]
        )
        
        refresh_btn.click(
            demo.get_current_metrics,
            outputs=[message_output, metrics_output, summary_output]
        )
        
        optimize_btn.click(
            demo.run_optimization,
            outputs=[message_output, optimization_output]
        )
        
        # Actualización automática
        interface.load(
            demo.get_system_info,
            outputs=[system_info_output]
        )
        
        # Actualizar información del sistema cada 10 segundos
        interface.load(
            demo.get_system_info,
            outputs=[system_info_output],
            every=10
        )
        
        # Actualizar métricas cada 15 segundos si está ejecutándose
        def auto_refresh_metrics():
            if demo.running:
                return asyncio.run(demo.get_current_metrics())
            return "Sistema no está ejecutándose", {}, {}
        
        interface.load(
            auto_refresh_metrics,
            outputs=[message_output, metrics_output, summary_output],
            every=15
        )
    
    return interface

def main():
    """Función principal."""
    print("🚀 Iniciando Demo del Sistema de Gestión de Recursos Inteligente")
    print("=" * 80)
    
    # Crear interfaz
    interface = create_demo_interface()
    
    # Lanzar interfaz
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()
