# 🚀 **SISTEMA DE MONITOREO INTELIGENTE AVANZADO**
# Monitoreo con detección de anomalías, alertas inteligentes y análisis predictivo

import asyncio
import logging
import time
import json
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import psutil
import GPUtil
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt
import seaborn as sns
from collections import deque, defaultdict
import threading
from queue import Queue, PriorityQueue
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import websockets
import aiohttp
import asyncio_mqtt as aiomqtt
from prometheus_client import start_http_server, Gauge, Counter, Histogram
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 🎯 **CONFIGURACIÓN Y CONSTANTES**
# ============================================================================

class AlertLevel(Enum):
    """Niveles de alerta."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class MetricType(Enum):
    """Tipos de métricas."""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    DISK = "disk"
    NETWORK = "network"
    TEMPERATURE = "temperature"
    POWER = "power"
    CUSTOM = "custom"

@dataclass
class AlertConfig:
    """Configuración de alertas."""
    metric_name: str
    threshold: float
    alert_level: AlertLevel
    comparison: str = ">"  # >, <, >=, <=, ==
    duration: int = 60  # segundos
    cooldown: int = 300  # segundos
    notification_channels: List[str] = field(default_factory=lambda: ["console"])
    custom_message: str = ""

@dataclass
class MetricData:
    """Datos de métrica."""
    name: str
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Alert:
    """Alerta del sistema."""
    id: str
    metric_name: str
    current_value: float
    threshold: float
    alert_level: AlertLevel
    message: str
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False
    resolution_time: Optional[datetime] = None

@dataclass
class AnomalyDetectionConfig:
    """Configuración de detección de anomalías."""
    algorithm: str = "isolation_forest"  # isolation_forest, dbscan, autoencoder
    contamination: float = 0.1
    window_size: int = 100
    sensitivity: float = 0.8
    retrain_interval: int = 3600  # segundos

# ============================================================================
# 🧠 **MODELOS DE DETECCIÓN DE ANOMALÍAS**
# ============================================================================

class AnomalyDetector:
    """Detector de anomalías con múltiples algoritmos."""
    
    def __init__(self, config: AnomalyDetectionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Modelos de detección
        self.isolation_forest = None
        self.dbscan = None
        self.autoencoder = None
        self.scaler = StandardScaler()
        
        # Datos históricos
        self.data_buffer = deque(maxlen=config.window_size)
        self.anomaly_scores = deque(maxlen=config.window_size)
        
        # Estado del modelo
        self.is_trained = False
        self.last_training = None
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Inicializar modelos de detección."""
        try:
            # Isolation Forest
            self.isolation_forest = IsolationForest(
                contamination=self.config.contamination,
                random_state=42,
                n_estimators=100
            )
            
            # DBSCAN
            self.dbscan = DBSCAN(
                eps=0.5,
                min_samples=5
            )
            
            # Autoencoder (PyTorch)
            self.autoencoder = AnomalyAutoencoder(
                input_size=12,  # Número de características
                hidden_size=8,
                latent_size=4
            )
            
            self.logger.info("✅ Modelos de detección de anomalías inicializados")
            
        except Exception as e:
            self.logger.error(f"❌ Error al inicializar modelos: {e}")
    
    def add_data_point(self, data_point: np.ndarray) -> bool:
        """Agregar punto de datos y detectar anomalía."""
        try:
            # Agregar a buffer
            self.data_buffer.append(data_point)
            
            # Detectar anomalía si hay suficientes datos
            if len(self.data_buffer) >= self.config.window_size:
                anomaly_detected = self._detect_anomaly(data_point)
                self.anomaly_scores.append(anomaly_detected)
                return anomaly_detected
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error al procesar punto de datos: {e}")
            return False
    
    def _detect_anomaly(self, data_point: np.ndarray) -> bool:
        """Detectar anomalía usando múltiples algoritmos."""
        try:
            if not self.is_trained:
                return False
            
            # Preparar datos
            data_array = np.array(list(self.data_buffer))
            data_scaled = self.scaler.transform(data_array)
            
            # Detección con Isolation Forest
            if_anomaly = self.isolation_forest.predict(data_scaled[-1:])[0] == -1
            
            # Detección con DBSCAN
            dbscan_labels = self.dbscan.fit_predict(data_scaled)
            dbscan_anomaly = dbscan_labels[-1] == -1
            
            # Detección con Autoencoder
            ae_anomaly = self._autoencoder_detect(data_scaled[-1:])
            
            # Combinar resultados
            anomaly_score = sum([if_anomaly, dbscan_anomaly, ae_anomaly]) / 3
            is_anomaly = anomaly_score > self.config.sensitivity
            
            return is_anomaly
            
        except Exception as e:
            self.logger.error(f"❌ Error en detección de anomalía: {e}")
            return False
    
    def _autoencoder_detect(self, data: np.ndarray) -> bool:
        """Detección con autoencoder."""
        try:
            if self.autoencoder is None:
                return False
            
            # Convertir a tensor
            data_tensor = torch.FloatTensor(data)
            
            # Obtener reconstrucción
            with torch.no_grad():
                reconstructed = self.autoencoder(data_tensor)
                reconstruction_error = torch.mean((data_tensor - reconstructed) ** 2).item()
            
            # Detectar anomalía basada en error de reconstrucción
            threshold = np.mean(list(self.anomaly_scores)) + 2 * np.std(list(self.anomaly_scores))
            return reconstruction_error > threshold
            
        except Exception as e:
            self.logger.error(f"❌ Error en detección con autoencoder: {e}")
            return False
    
    def train(self, training_data: np.ndarray):
        """Entrenar modelos de detección."""
        try:
            if len(training_data) < 50:
                self.logger.warning("⚠️ Datos insuficientes para entrenamiento")
                return
            
            # Escalar datos
            training_scaled = self.scaler.fit_transform(training_data)
            
            # Entrenar Isolation Forest
            self.isolation_forest.fit(training_scaled)
            
            # Entrenar Autoencoder
            self._train_autoencoder(training_scaled)
            
            self.is_trained = True
            self.last_training = datetime.now()
            
            self.logger.info("✅ Modelos de detección entrenados")
            
        except Exception as e:
            self.logger.error(f"❌ Error al entrenar modelos: {e}")
    
    def _train_autoencoder(self, training_data: np.ndarray):
        """Entrenar autoencoder."""
        try:
            # Convertir a tensor
            data_tensor = torch.FloatTensor(training_data)
            dataset = TensorDataset(data_tensor, data_tensor)
            dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
            
            # Configurar entrenamiento
            optimizer = torch.optim.Adam(self.autoencoder.parameters(), lr=0.001)
            criterion = nn.MSELoss()
            
            # Entrenar
            self.autoencoder.train()
            for epoch in range(50):
                total_loss = 0
                for batch_x, batch_y in dataloader:
                    optimizer.zero_grad()
                    reconstructed = self.autoencoder(batch_x)
                    loss = criterion(reconstructed, batch_y)
                    loss.backward()
                    optimizer.step()
                    total_loss += loss.item()
                
                if epoch % 10 == 0:
                    self.logger.debug(f"Epoch {epoch}, Loss: {total_loss/len(dataloader):.6f}")
            
        except Exception as e:
            self.logger.error(f"❌ Error al entrenar autoencoder: {e}")
    
    def get_anomaly_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de anomalías."""
        try:
            if not self.anomaly_scores:
                return {"anomaly_rate": 0.0, "total_detections": 0}
            
            anomaly_rate = sum(self.anomaly_scores) / len(self.anomaly_scores)
            return {
                "anomaly_rate": anomaly_rate,
                "total_detections": sum(self.anomaly_scores),
                "total_samples": len(self.anomaly_scores),
                "last_training": self.last_training.isoformat() if self.last_training else None,
                "is_trained": self.is_trained
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error al obtener estadísticas: {e}")
            return {}

class AnomalyAutoencoder(nn.Module):
    """Autoencoder para detección de anomalías."""
    
    def __init__(self, input_size: int, hidden_size: int, latent_size: int):
        super().__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, latent_size),
            nn.ReLU()
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, input_size),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

# ============================================================================
# 📊 **SISTEMA DE MONITOREO INTELIGENTE**
# ============================================================================

class IntelligentMonitoringSystem:
    """Sistema de monitoreo inteligente avanzado."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Configuración
        self.monitoring_interval = self.config.get('monitoring_interval', 30)
        self.alert_configs = self.config.get('alert_configs', [])
        self.anomaly_config = AnomalyDetectionConfig(**self.config.get('anomaly_config', {}))
        
        # Componentes del sistema
        self.anomaly_detector = AnomalyDetector(self.anomaly_config)
        self.metric_collectors = {}
        self.alert_handlers = {}
        
        # Estado del sistema
        self.is_running = False
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.active_alerts = {}
        self.alert_history = []
        
        # Métricas de Prometheus
        self.prometheus_metrics = self._setup_prometheus_metrics()
        
        # Configuración de threading
        self.metric_queue = Queue()
        self.alert_queue = PriorityQueue()
        self.lock = threading.Lock()
        
        # Configurar recolectores de métricas
        self._setup_metric_collectors()
        self._setup_alert_handlers()
        
        self.logger.info("🚀 Sistema de monitoreo inteligente inicializado")
    
    def _setup_prometheus_metrics(self) -> Dict[str, Any]:
        """Configurar métricas de Prometheus."""
        try:
            # Iniciar servidor Prometheus
            start_http_server(9090)
            
            metrics = {
                'cpu_usage': Gauge('cpu_usage_percent', 'CPU usage percentage'),
                'memory_usage': Gauge('memory_usage_percent', 'Memory usage percentage'),
                'gpu_usage': Gauge('gpu_usage_percent', 'GPU usage percentage'),
                'disk_usage': Gauge('disk_usage_percent', 'Disk usage percentage'),
                'temperature': Gauge('system_temperature', 'System temperature'),
                'alert_count': Counter('alerts_total', 'Total number of alerts'),
                'anomaly_count': Counter('anomalies_total', 'Total number of anomalies detected'),
                'response_time': Histogram('response_time_seconds', 'Response time in seconds')
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Error al configurar Prometheus: {e}")
            return {}
    
    def _setup_metric_collectors(self):
        """Configurar recolectores de métricas."""
        try:
            # Recolector de CPU
            self.metric_collectors[MetricType.CPU] = self._collect_cpu_metrics
            
            # Recolector de memoria
            self.metric_collectors[MetricType.MEMORY] = self._collect_memory_metrics
            
            # Recolector de GPU
            self.metric_collectors[MetricType.GPU] = self._collect_gpu_metrics
            
            # Recolector de disco
            self.metric_collectors[MetricType.DISK] = self._collect_disk_metrics
            
            # Recolector de red
            self.metric_collectors[MetricType.NETWORK] = self._collect_network_metrics
            
            # Recolector de temperatura
            self.metric_collectors[MetricType.TEMPERATURE] = self._collect_temperature_metrics
            
            self.logger.info(f"✅ {len(self.metric_collectors)} recolectores de métricas configurados")
            
        except Exception as e:
            self.logger.error(f"❌ Error al configurar recolectores: {e}")
    
    def _setup_alert_handlers(self):
        """Configurar manejadores de alertas."""
        try:
            # Manejador de consola
            self.alert_handlers['console'] = self._console_alert_handler
            
            # Manejador de email
            if 'email' in self.config:
                self.alert_handlers['email'] = self._email_alert_handler
            
            # Manejador de webhook
            if 'webhook' in self.config:
                self.alert_handlers['webhook'] = self._webhook_alert_handler
            
            # Manejador de MQTT
            if 'mqtt' in self.config:
                self.alert_handlers['mqtt'] = self._mqtt_alert_handler
            
            self.logger.info(f"✅ {len(self.alert_handlers)} manejadores de alertas configurados")
            
        except Exception as e:
            self.logger.error(f"❌ Error al configurar manejadores: {e}")
    
    async def start(self):
        """Iniciar sistema de monitoreo."""
        self.is_running = True
        self.logger.info("🚀 Sistema de monitoreo iniciado")
        
        # Iniciar tareas asíncronas
        asyncio.create_task(self._monitoring_loop())
        asyncio.create_task(self._alert_processing_loop())
        asyncio.create_task(self._anomaly_detection_loop())
        asyncio.create_task(self._metrics_processing_loop())
    
    async def stop(self):
        """Detener sistema de monitoreo."""
        self.is_running = False
        self.logger.info("🛑 Sistema de monitoreo detenido")
    
    async def _monitoring_loop(self):
        """Loop principal de monitoreo."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Recolectar métricas
                metrics = await self._collect_all_metrics()
                
                # Procesar métricas
                await self._process_metrics(metrics)
                
                # Actualizar métricas de Prometheus
                self._update_prometheus_metrics(metrics)
                
                # Verificar alertas
                await self._check_alerts(metrics)
                
                # Medir tiempo de respuesta
                response_time = time.time() - start_time
                if 'response_time' in self.prometheus_metrics:
                    self.prometheus_metrics['response_time'].observe(response_time)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"❌ Error en loop de monitoreo: {e}")
                await asyncio.sleep(10)
    
    async def _collect_all_metrics(self) -> Dict[str, MetricData]:
        """Recolectar todas las métricas del sistema."""
        metrics = {}
        
        try:
            for metric_type, collector in self.metric_collectors.items():
                try:
                    metric_data = await collector()
                    if metric_data:
                        metrics[metric_type.value] = metric_data
                except Exception as e:
                    self.logger.error(f"❌ Error al recolectar {metric_type.value}: {e}")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Error al recolectar métricas: {e}")
            return {}
    
    async def _collect_cpu_metrics(self) -> MetricData:
        """Recolectar métricas de CPU."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count()
            
            return MetricData(
                name="cpu",
                value=cpu_percent,
                timestamp=datetime.now(),
                metadata={
                    'frequency': cpu_freq.current if cpu_freq else 0,
                    'cores': cpu_count,
                    'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
                }
            )
        except Exception as e:
            self.logger.error(f"❌ Error al recolectar métricas de CPU: {e}")
            return None
    
    async def _collect_memory_metrics(self) -> MetricData:
        """Recolectar métricas de memoria."""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return MetricData(
                name="memory",
                value=memory.percent,
                timestamp=datetime.now(),
                metadata={
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'swap_percent': swap.percent,
                    'swap_used': swap.used
                }
            )
        except Exception as e:
            self.logger.error(f"❌ Error al recolectar métricas de memoria: {e}")
            return None
    
    async def _collect_gpu_metrics(self) -> MetricData:
        """Recolectar métricas de GPU."""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Usar la primera GPU
                return MetricData(
                    name="gpu",
                    value=gpu.load * 100,
                    timestamp=datetime.now(),
                    metadata={
                        'memory_used': gpu.memoryUsed,
                        'memory_total': gpu.memoryTotal,
                        'temperature': gpu.temperature,
                        'power': getattr(gpu, 'power', 0)
                    }
                )
            return None
        except Exception as e:
            self.logger.error(f"❌ Error al recolectar métricas de GPU: {e}")
            return None
    
    async def _collect_disk_metrics(self) -> MetricData:
        """Recolectar métricas de disco."""
        try:
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            return MetricData(
                name="disk",
                value=disk.percent,
                timestamp=datetime.now(),
                metadata={
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0
                }
            )
        except Exception as e:
            self.logger.error(f"❌ Error al recolectar métricas de disco: {e}")
            return None
    
    async def _collect_network_metrics(self) -> MetricData:
        """Recolectar métricas de red."""
        try:
            network = psutil.net_io_counters()
            
            return MetricData(
                name="network",
                value=network.bytes_sent + network.bytes_recv,
                timestamp=datetime.now(),
                metadata={
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            )
        except Exception as e:
            self.logger.error(f"❌ Error al recolectar métricas de red: {e}")
            return None
    
    async def _collect_temperature_metrics(self) -> MetricData:
        """Recolectar métricas de temperatura."""
        try:
            # Intentar obtener temperatura del sistema
            temp = 0
            try:
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp = float(f.read()) / 1000
            except:
                # Fallback: usar temperatura de GPU si está disponible
                gpus = GPUtil.getGPUs()
                if gpus:
                    temp = gpus[0].temperature
            
            return MetricData(
                name="temperature",
                value=temp,
                timestamp=datetime.now(),
                metadata={'unit': 'celsius'}
            )
        except Exception as e:
            self.logger.error(f"❌ Error al recolectar métricas de temperatura: {e}")
            return None
    
    async def _process_metrics(self, metrics: Dict[str, MetricData]):
        """Procesar métricas recolectadas."""
        try:
            for metric_name, metric_data in metrics.items():
                # Agregar a historial
                self.metrics_history[metric_name].append(metric_data)
                
                # Agregar a cola para detección de anomalías
                self.metric_queue.put(metric_data)
                
                # Actualizar estadísticas
                self._update_metric_statistics(metric_name, metric_data)
                
        except Exception as e:
            self.logger.error(f"❌ Error al procesar métricas: {e}")
    
    def _update_metric_statistics(self, metric_name: str, metric_data: MetricData):
        """Actualizar estadísticas de métricas."""
        try:
            # Implementar estadísticas en tiempo real
            pass
        except Exception as e:
            self.logger.error(f"❌ Error al actualizar estadísticas: {e}")
    
    def _update_prometheus_metrics(self, metrics: Dict[str, MetricData]):
        """Actualizar métricas de Prometheus."""
        try:
            for metric_name, metric_data in metrics.items():
                if metric_name in self.prometheus_metrics:
                    self.prometheus_metrics[metric_name].set(metric_data.value)
                    
        except Exception as e:
            self.logger.error(f"❌ Error al actualizar métricas de Prometheus: {e}")
    
    async def _check_alerts(self, metrics: Dict[str, MetricData]):
        """Verificar alertas basadas en métricas."""
        try:
            for alert_config in self.alert_configs:
                metric_name = alert_config.metric_name
                
                if metric_name in metrics:
                    metric_data = metrics[metric_name]
                    
                    # Verificar umbral
                    if self._check_threshold(metric_data.value, alert_config):
                        # Crear alerta
                        alert = Alert(
                            id=f"{metric_name}_{int(time.time())}",
                            metric_name=metric_name,
                            current_value=metric_data.value,
                            threshold=alert_config.threshold,
                            alert_level=alert_config.alert_level,
                            message=alert_config.custom_message or f"{metric_name} excedió umbral",
                            timestamp=datetime.now()
                        )
                        
                        # Agregar a cola de alertas
                        self.alert_queue.put((alert_config.alert_level.value, alert))
                        
        except Exception as e:
            self.logger.error(f"❌ Error al verificar alertas: {e}")
    
    def _check_threshold(self, value: float, alert_config: AlertConfig) -> bool:
        """Verificar si un valor excede el umbral."""
        try:
            if alert_config.comparison == ">":
                return value > alert_config.threshold
            elif alert_config.comparison == "<":
                return value < alert_config.threshold
            elif alert_config.comparison == ">=":
                return value >= alert_config.threshold
            elif alert_config.comparison == "<=":
                return value <= alert_config.threshold
            elif alert_config.comparison == "==":
                return value == alert_config.threshold
            else:
                return False
        except Exception as e:
            self.logger.error(f"❌ Error al verificar umbral: {e}")
            return False
    
    async def _alert_processing_loop(self):
        """Loop de procesamiento de alertas."""
        while self.is_running:
            try:
                if not self.alert_queue.empty():
                    priority, alert = self.alert_queue.get()
                    
                    # Procesar alerta
                    await self._process_alert(alert)
                    
                    # Agregar a historial
                    self.alert_history.append(alert)
                    
                    # Mantener solo las últimas 1000 alertas
                    if len(self.alert_history) > 1000:
                        self.alert_history = self.alert_history[-1000:]
                
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"❌ Error en loop de alertas: {e}")
                await asyncio.sleep(5)
    
    async def _process_alert(self, alert: Alert):
        """Procesar una alerta."""
        try:
            # Incrementar contador de Prometheus
            if 'alert_count' in self.prometheus_metrics:
                self.prometheus_metrics['alert_count'].inc()
            
            # Enviar a manejadores
            for channel in self.config.get('notification_channels', ['console']):
                if channel in self.alert_handlers:
                    try:
                        await self.alert_handlers[channel](alert)
                    except Exception as e:
                        self.logger.error(f"❌ Error en manejador {channel}: {e}")
            
            self.logger.warning(f"🚨 Alerta: {alert.message} (Nivel: {alert.alert_level.value})")
            
        except Exception as e:
            self.logger.error(f"❌ Error al procesar alerta: {e}")
    
    async def _anomaly_detection_loop(self):
        """Loop de detección de anomalías."""
        while self.is_running:
            try:
                if not self.metric_queue.empty():
                    metric_data = self.metric_queue.get()
                    
                    # Preparar datos para detección
                    data_point = self._prepare_data_point(metric_data)
                    
                    # Detectar anomalía
                    if self.anomaly_detector.add_data_point(data_point):
                        # Incrementar contador de Prometheus
                        if 'anomaly_count' in self.prometheus_metrics:
                            self.prometheus_metrics['anomaly_count'].inc()
                        
                        self.logger.warning(f"🔍 Anomalía detectada en {metric_data.name}: {metric_data.value}")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"❌ Error en loop de anomalías: {e}")
                await asyncio.sleep(5)
    
    def _prepare_data_point(self, metric_data: MetricData) -> np.ndarray:
        """Preparar punto de datos para detección de anomalías."""
        try:
            # Crear vector de características
            features = [
                metric_data.value,
                metric_data.timestamp.hour,
                metric_data.timestamp.minute,
                metric_data.timestamp.weekday(),
                len(self.metrics_history[metric_data.name]),
                # Agregar más características según sea necesario
            ]
            
            # Rellenar hasta 12 características
            while len(features) < 12:
                features.append(0.0)
            
            return np.array(features[:12])
            
        except Exception as e:
            self.logger.error(f"❌ Error al preparar punto de datos: {e}")
            return np.zeros(12)
    
    async def _metrics_processing_loop(self):
        """Loop de procesamiento de métricas."""
        while self.is_running:
            try:
                # Entrenar modelo de anomalías si es necesario
                if (self.anomaly_detector.last_training is None or 
                    datetime.now() - self.anomaly_detector.last_training > 
                    timedelta(seconds=self.anomaly_config.retrain_interval)):
                    
                    await self._retrain_anomaly_model()
                
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"❌ Error en loop de procesamiento: {e}")
                await asyncio.sleep(10)
    
    async def _retrain_anomaly_model(self):
        """Reentrenar modelo de anomalías."""
        try:
            # Preparar datos de entrenamiento
            training_data = []
            for metric_name, history in self.metrics_history.items():
                for metric_data in history:
                    data_point = self._prepare_data_point(metric_data)
                    training_data.append(data_point)
            
            if len(training_data) >= 50:
                training_array = np.array(training_data)
                self.anomaly_detector.train(training_array)
                self.logger.info("✅ Modelo de anomalías reentrenado")
            
        except Exception as e:
            self.logger.error(f"❌ Error al reentrenar modelo: {e}")
    
    # Manejadores de alertas
    async def _console_alert_handler(self, alert: Alert):
        """Manejador de alertas para consola."""
        print(f"🚨 ALERTA [{alert.alert_level.value.upper()}]: {alert.message}")
        print(f"   Métrica: {alert.metric_name}")
        print(f"   Valor: {alert.current_value}")
        print(f"   Umbral: {alert.threshold}")
        print(f"   Timestamp: {alert.timestamp}")
    
    async def _email_alert_handler(self, alert: Alert):
        """Manejador de alertas para email."""
        # Implementar envío de email
        pass
    
    async def _webhook_alert_handler(self, alert: Alert):
        """Manejador de alertas para webhook."""
        # Implementar webhook
        pass
    
    async def _mqtt_alert_handler(self, alert: Alert):
        """Manejador de alertas para MQTT."""
        # Implementar MQTT
        pass
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema de monitoreo."""
        try:
            return {
                'is_running': self.is_running,
                'metrics_count': len(self.metrics_history),
                'active_alerts': len(self.active_alerts),
                'alert_history_count': len(self.alert_history),
                'anomaly_statistics': self.anomaly_detector.get_anomaly_statistics(),
                'last_metrics': {
                    name: list(history)[-1].value if history else None
                    for name, history in self.metrics_history.items()
                }
            }
        except Exception as e:
            self.logger.error(f"❌ Error al obtener estado: {e}")
            return {}

# ============================================================================
# 🚀 **FUNCIÓN PRINCIPAL**
# ============================================================================

async def main():
    """Función principal de demostración."""
    # Configuración del sistema
    config = {
        'monitoring_interval': 30,
        'alert_configs': [
            AlertConfig(
                metric_name='cpu',
                threshold=80.0,
                alert_level=AlertLevel.WARNING,
                comparison='>',
                duration=60,
                notification_channels=['console']
            ),
            AlertConfig(
                metric_name='memory',
                threshold=90.0,
                alert_level=AlertLevel.CRITICAL,
                comparison='>',
                duration=30,
                notification_channels=['console']
            ),
            AlertConfig(
                metric_name='temperature',
                threshold=85.0,
                alert_level=AlertLevel.EMERGENCY,
                comparison='>',
                duration=10,
                notification_channels=['console']
            )
        ],
        'anomaly_config': {
            'algorithm': 'isolation_forest',
            'contamination': 0.1,
            'window_size': 100,
            'sensitivity': 0.8
        },
        'notification_channels': ['console']
    }
    
    # Crear sistema de monitoreo
    monitoring_system = IntelligentMonitoringSystem(config)
    
    try:
        # Iniciar sistema
        await monitoring_system.start()
        
        print("🚀 Sistema de monitoreo inteligente iniciado")
        print("📊 Métricas disponibles en: http://localhost:9090")
        
        # Mantener ejecutando
        while True:
            status = monitoring_system.get_system_status()
            print(f"📈 Estado del sistema: {status}")
            await asyncio.sleep(60)
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema...")
    finally:
        await monitoring_system.stop()

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Ejecutar
    asyncio.run(main())
