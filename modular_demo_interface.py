"""
Interfaz de Demostración Interactiva para el Sistema Modular
Sistema de Acumulación de Gradientes con Arquitectura Modular Avanzada
"""

import asyncio
import gradio as gr
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List
import threading
import time

# Importar sistema modular
from modular_integration_system import (
    ModularIntegrationSystem,
    IntegrationConfig,
    create_integration_system
)

class ModularDemoInterface:
    """Interfaz de demostración para el sistema modular."""
    
    def __init__(self):
        self.system: ModularIntegrationSystem = None
        self.system_thread: threading.Thread = None
        self.running = False
        self.config_file = "integration_config.yaml"
        
        # Estado del sistema
        self.system_status = "Detenido"
        self.last_metrics = {}
        self.event_history = []
        
        # Configurar interfaz
        self._setup_interface()
    
    def _setup_interface(self):
        """Configurar la interfaz de Gradio."""
        with gr.Blocks(
            title="🏗️ Sistema Modular de Acumulación de Gradientes",
            theme=gr.themes.Soft()
        ) as self.interface:
            
            gr.Markdown("""
            # 🏗️ **SISTEMA MODULAR DE ACUMULACIÓN DE GRADIENTES**
            
            ## **Arquitectura Modular Avanzada con Patrones de Diseño**
            
            Este sistema demuestra la integración modular de:
            - **Sistema de Optimización** (Strategy Pattern)
            - **Sistema de Configuración** (Builder Pattern)
            - **Sistema de Monitoreo** (Observer Pattern)
            - **Sistema de Integración** (Event-Driven Architecture)
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 🎛️ **Control del Sistema**")
                    
                    # Botones de control
                    start_btn = gr.Button("🚀 Iniciar Sistema", variant="primary")
                    stop_btn = gr.Button("🛑 Detener Sistema", variant="stop")
                    restart_btn = gr.Button("🔄 Reiniciar Sistema")
                    
                    # Estado del sistema
                    status_display = gr.Textbox(
                        label="Estado del Sistema",
                        value="Detenido",
                        interactive=False
                    )
                    
                    # Configuración
                    gr.Markdown("### ⚙️ **Configuración**")
                    
                    enable_optimization = gr.Checkbox(
                        label="Habilitar Optimización",
                        value=True
                    )
                    enable_monitoring = gr.Checkbox(
                        label="Habilitar Monitoreo",
                        value=True
                    )
                    enable_config = gr.Checkbox(
                        label="Habilitar Gestión de Configuración",
                        value=True
                    )
                    
                    log_level = gr.Dropdown(
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        label="Nivel de Logging",
                        value="INFO"
                    )
                    
                    metrics_interval = gr.Slider(
                        minimum=0.5,
                        maximum=10.0,
                        step=0.5,
                        value=1.0,
                        label="Intervalo de Métricas (segundos)"
                    )
                    
                    optimization_interval = gr.Slider(
                        minimum=1.0,
                        maximum=30.0,
                        step=1.0,
                        value=5.0,
                        label="Intervalo de Optimización (segundos)"
                    )
                    
                    apply_config_btn = gr.Button("💾 Aplicar Configuración")
                
                with gr.Column(scale=2):
                    gr.Markdown("### 📊 **Métricas del Sistema**")
                    
                    # Métricas en tiempo real
                    metrics_display = gr.JSON(
                        label="Métricas Actuales",
                        value={},
                        interactive=False
                    )
                    
                    # Gráfico de métricas
                    metrics_chart = gr.LinePlot(
                        label="Historial de Métricas",
                        x="timestamp",
                        y="value",
                        color="metric",
                        height=300
                    )
                    
                    # Historial de eventos
                    gr.Markdown("### 📝 **Historial de Eventos**")
                    events_display = gr.Textbox(
                        label="Eventos del Sistema",
                        value="",
                        lines=10,
                        interactive=False
                    )
                    
                    # Botones de acción
                    refresh_metrics_btn = gr.Button("🔄 Actualizar Métricas")
                    clear_events_btn = gr.Button("🗑️ Limpiar Eventos")
                    export_metrics_btn = gr.Button("📤 Exportar Métricas")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 🔧 **Operaciones de Optimización**")
                    
                    # Contexto de optimización
                    memory_pressure = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        step=0.05,
                        value=0.75,
                        label="Presión de Memoria"
                    )
                    
                    cpu_usage = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        step=0.05,
                        value=0.60,
                        label="Uso de CPU"
                    )
                    
                    gpu_usage = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        step=0.05,
                        value=0.80,
                        label="Uso de GPU"
                    )
                    
                    apply_optimization_btn = gr.Button("⚡ Aplicar Optimización")
                    
                    # Resultado de optimización
                    optimization_result = gr.JSON(
                        label="Resultado de Optimización",
                        value={},
                        interactive=False
                    )
                
                with gr.Column():
                    gr.Markdown("### 📁 **Gestión de Configuración**")
                    
                    # Cargar/Guardar configuración
                    config_file_input = gr.File(
                        label="Archivo de Configuración (YAML/JSON)",
                        file_types=[".yaml", ".yml", ".json"]
                    )
                    
                    load_config_btn = gr.Button("📂 Cargar Configuración")
                    save_config_btn = gr.Button("💾 Guardar Configuración")
                    
                    # Configuración actual
                    current_config_display = gr.JSON(
                        label="Configuración Actual",
                        value={},
                        interactive=False
                    )
            
            # Eventos de la interfaz
            start_btn.click(
                fn=self._start_system,
                outputs=[status_display, start_btn, stop_btn]
            )
            
            stop_btn.click(
                fn=self._stop_system,
                outputs=[status_display, start_btn, stop_btn]
            )
            
            restart_btn.click(
                fn=self._restart_system,
                outputs=[status_display, start_btn, stop_btn]
            )
            
            apply_config_btn.click(
                fn=self._apply_configuration,
                inputs=[
                    enable_optimization, enable_monitoring, enable_config,
                    log_level, metrics_interval, optimization_interval
                ],
                outputs=[current_config_display]
            )
            
            refresh_metrics_btn.click(
                fn=self._refresh_metrics,
                outputs=[metrics_display, metrics_chart]
            )
            
            clear_events_btn.click(
                fn=self._clear_events,
                outputs=[events_display]
            )
            
            export_metrics_btn.click(
                fn=self._export_metrics,
                outputs=[]
            )
            
            apply_optimization_btn.click(
                fn=self._apply_optimization,
                inputs=[memory_pressure, cpu_usage, gpu_usage],
                outputs=[optimization_result]
            )
            
            load_config_btn.click(
                fn=self._load_configuration,
                inputs=[config_file_input],
                outputs=[current_config_display]
            )
            
            save_config_btn.click(
                fn=self._save_configuration,
                outputs=[current_config_display]
            )
            
            # Actualización automática
            self.interface.load(self._initialize_demo)
    
    def _initialize_demo(self):
        """Inicializar la demostración."""
        try:
            # Cargar configuración por defecto
            self._load_default_config()
            
            # Mostrar configuración actual
            config_display = self._get_current_config_display()
            
            return {
                current_config_display: config_display
            }
        except Exception as e:
            print(f"Error inicializando demo: {e}")
            return {}
    
    def _load_default_config(self):
        """Cargar configuración por defecto."""
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r') as f:
                    if self.config_file.endswith(('.yaml', '.yml')):
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                
                # Crear configuración
                self.config = IntegrationConfig(**config_data)
            else:
                self.config = IntegrationConfig()
                
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            self.config = IntegrationConfig()
    
    def _get_current_config_display(self) -> Dict[str, Any]:
        """Obtener configuración actual para mostrar."""
        if hasattr(self, 'config'):
            return {
                'enable_optimization': self.config.enable_optimization,
                'enable_monitoring': self.config.enable_monitoring,
                'enable_config_management': self.config.enable_config_management,
                'log_level': self.config.log_level,
                'metrics_interval': self.config.metrics_interval,
                'optimization_interval': self.config.config.optimization_interval
            }
        return {}
    
    def _start_system(self):
        """Iniciar el sistema modular."""
        if self.running:
            return "Sistema ya está ejecutándose", gr.Button(interactive=False), gr.Button(interactive=True)
        
        try:
            # Crear y configurar sistema
            self.system = ModularIntegrationSystem(self.config)
            
            # Iniciar sistema en thread separado
            self.system_thread = threading.Thread(target=self._run_system_async)
            self.system_thread.daemon = True
            self.system_thread.start()
            
            self.running = True
            self.system_status = "Ejecutándose"
            
            return "Ejecutándose", gr.Button(interactive=False), gr.Button(interactive=True)
            
        except Exception as e:
            error_msg = f"Error iniciando sistema: {e}"
            print(error_msg)
            return error_msg, gr.Button(interactive=True), gr.Button(interactive=False)
    
    def _stop_system(self):
        """Detener el sistema modular."""
        if not self.running:
            return "Sistema ya está detenido", gr.Button(interactive=True), gr.Button(interactive=False)
        
        try:
            self.running = False
            
            if self.system:
                # Detener sistema de forma asíncrona
                asyncio.run_coroutine_threadsafe(
                    self.system.stop(),
                    asyncio.new_event_loop()
                )
            
            self.system_status = "Detenido"
            
            return "Detenido", gr.Button(interactive=True), gr.Button(interactive=False)
            
        except Exception as e:
            error_msg = f"Error deteniendo sistema: {e}"
            print(error_msg)
            return error_msg, gr.Button(interactive=True), gr.Button(interactive=False)
    
    def _restart_system(self):
        """Reiniciar el sistema modular."""
        self._stop_system()
        time.sleep(1)  # Pequeña pausa
        return self._start_system()
    
    def _run_system_async(self):
        """Ejecutar sistema de forma asíncrona en thread separado."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Iniciar sistema
            loop.run_until_complete(self.system.start())
            
            # Mantener sistema ejecutándose
            while self.running:
                loop.run_until_complete(asyncio.sleep(0.1))
                
        except Exception as e:
            print(f"Error en thread del sistema: {e}")
        finally:
            if loop.is_running():
                loop.close()
    
    def _apply_configuration(self, enable_opt, enable_mon, enable_cfg, log_lvl, metrics_int, opt_int):
        """Aplicar nueva configuración."""
        try:
            # Actualizar configuración
            self.config.enable_optimization = enable_opt
            self.config.enable_monitoring = enable_mon
            self.config.enable_config_management = enable_cfg
            self.config.log_level = log_lvl
            self.config.metrics_interval = metrics_int
            self.config.optimization_interval = opt_int
            
            # Guardar configuración
            self._save_config_to_file()
            
            return self._get_current_config_display()
            
        except Exception as e:
            print(f"Error aplicando configuración: {e}")
            return {}
    
    def _save_config_to_file(self):
        """Guardar configuración actual a archivo."""
        try:
            config_data = {
                'enable_optimization': self.config.enable_optimization,
                'enable_monitoring': self.config.enable_monitoring,
                'enable_config_management': self.config.enable_config_management,
                'auto_reload_config': self.config.auto_reload_config,
                'config_file': self.config.config_file,
                'log_level': self.config.log_level,
                'metrics_interval': self.config.metrics_interval,
                'optimization_interval': self.config.optimization_interval
            }
            
            with open(self.config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
                
        except Exception as e:
            print(f"Error guardando configuración: {e}")
    
    def _refresh_metrics(self):
        """Actualizar métricas del sistema."""
        try:
            if self.system and self.running:
                # Obtener métricas del sistema
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                metrics = loop.run_until_complete(self.system.get_system_metrics())
                loop.close()
                
                self.last_metrics = metrics
                
                # Preparar datos para gráfico
                chart_data = self._prepare_chart_data(metrics)
                
                return metrics, chart_data
            else:
                return {}, []
                
        except Exception as e:
            print(f"Error actualizando métricas: {e}")
            return {}, []
    
    def _prepare_chart_data(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Preparar datos para el gráfico de métricas."""
        chart_data = []
        timestamp = metrics.get('timestamp', time.time())
        
        # Agregar métricas del sistema
        if 'system_status' in metrics:
            status = metrics['system_status']
            chart_data.extend([
                {'timestamp': timestamp, 'value': 1 if status.get('running', False) else 0, 'metric': 'System Running'},
                {'timestamp': timestamp, 'value': status.get('observers_count', 0), 'metric': 'Observers Count'}
            ])
        
        # Agregar métricas de componentes
        if 'system_status' in metrics and 'components' in metrics['system_status']:
            components = metrics['system_status']['components']
            for component, enabled in components.items():
                chart_data.append({
                    'timestamp': timestamp,
                    'value': 1 if enabled else 0,
                    'metric': f'{component.title()} Enabled'
                })
        
        return chart_data
    
    def _clear_events(self):
        """Limpiar historial de eventos."""
        self.event_history = []
        return ""
    
    def _export_metrics(self):
        """Exportar métricas del sistema."""
        try:
            if self.last_metrics:
                filename = f"system_metrics_{int(time.time())}.json"
                with open(filename, 'w') as f:
                    json.dump(self.last_metrics, f, indent=2, default=str)
                
                print(f"Métricas exportadas a: {filename}")
            
        except Exception as e:
            print(f"Error exportando métricas: {e}")
    
    def _apply_optimization(self, memory_pressure, cpu_usage, gpu_usage):
        """Aplicar optimización manual."""
        try:
            if not self.system or not self.running:
                return {"error": "Sistema no está ejecutándose"}
            
            # Crear contexto de optimización
            context = {
                'memory_pressure': memory_pressure,
                'cpu_usage': cpu_usage,
                'gpu_usage': gpu_usage,
                'needs_optimization': True
            }
            
            # Aplicar optimización
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self.system.apply_optimization(context))
            loop.close()
            
            return result
            
        except Exception as e:
            error_msg = f"Error aplicando optimización: {e}"
            print(error_msg)
            return {"error": error_msg}
    
    def _load_configuration(self, file):
        """Cargar configuración desde archivo."""
        try:
            if file is None:
                return self._get_current_config_display()
            
            # Leer archivo
            with open(file.name, 'r') as f:
                if file.name.endswith(('.yaml', '.yml')):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            # Actualizar configuración
            for key, value in config_data.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            # Guardar configuración
            self._save_config_to_file()
            
            return self._get_current_config_display()
            
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            return self._get_current_config_display()
    
    def _save_configuration(self):
        """Guardar configuración actual."""
        try:
            self._save_config_to_file()
            return self._get_current_config_display()
            
        except Exception as e:
            print(f"Error guardando configuración: {e}")
            return self._get_current_config_display()
    
    def launch(self, **kwargs):
        """Lanzar la interfaz de demostración."""
        return self.interface.launch(**kwargs)

def main():
    """Función principal para ejecutar la demostración."""
    print("🎯 Iniciando Interfaz de Demostración del Sistema Modular...")
    
    # Crear interfaz
    demo = ModularDemoInterface()
    
    # Lanzar interfaz
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()
