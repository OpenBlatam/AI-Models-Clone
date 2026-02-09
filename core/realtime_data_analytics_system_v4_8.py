"""
Sistema de Análisis de Datos en Tiempo Real v4.8
HeyGen AI - Sistema de Monitoreo Inteligente con IA Avanzada

Este sistema implementa capacidades avanzadas de análisis de datos en tiempo real incluyendo:
- Procesamiento de streams de datos
- Análisis de patrones complejos
- Detección de anomalías avanzada
- Procesamiento de eventos en tiempo real
"""

import asyncio
import time
import json
import logging
import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import statistics

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataStreamType(Enum):
    """Tipos de streams de datos"""
    METRICS = "metrics"
    LOGS = "logs"
    EVENTS = "events"
    TRANSACTIONS = "transactions"
    SENSOR_DATA = "sensor_data"
    USER_ACTIVITY = "user_activity"

class ProcessingMode(Enum):
    """Modos de procesamiento"""
    REAL_TIME = "real_time"
    NEAR_REAL_TIME = "near_real_time"
    BATCH = "batch"
    HYBRID = "hybrid"

class AnomalyType(Enum):
    """Tipos de anomalías detectables"""
    SPIKE = "spike"
    DROP = "drop"
    TREND_CHANGE = "trend_change"
    PATTERN_BREAK = "pattern_break"
    OUTLIER = "outlier"
    SEASONAL_ANOMALY = "seasonal_anomaly"

@dataclass
class DataPoint:
    """Punto de datos individual"""
    timestamp: datetime
    value: Union[float, int, str, Dict[str, Any]]
    source: str
    data_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 1.0

@dataclass
class DataStream:
    """Stream de datos continuo"""
    stream_id: str
    stream_type: DataStreamType
    data_points: List[DataPoint] = field(default_factory=list)
    processing_mode: ProcessingMode = ProcessingMode.REAL_TIME
    buffer_size: int = 1000
    processing_delay: float = 0.001

@dataclass
class PatternAnalysis:
    """Resultado del análisis de patrones"""
    pattern_type: str
    confidence: float
    start_time: datetime
    end_time: datetime
    pattern_data: List[DataPoint]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnomalyDetection:
    """Resultado de la detección de anomalías"""
    anomaly_type: AnomalyType
    severity: float
    timestamp: datetime
    data_point: DataPoint
    confidence: float
    description: str
    recommendations: List[str] = field(default_factory=list)

class StreamDataProcessor:
    """Procesador de streams de datos en tiempo real"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_buffer_size = config.get('max_buffer_size', 10000)
        self.processing_workers = config.get('processing_workers', 4)
        self.batch_size = config.get('batch_size', 100)
        self.active_streams = {}
        self.processing_queue = asyncio.Queue()
        
    async def start(self):
        """Iniciar el procesador de streams"""
        logger.info("🚀 Iniciando Procesador de Streams de Datos")
        
        # Iniciar workers de procesamiento
        self.workers = [
            asyncio.create_task(self._processing_worker(f"worker_{i}"))
            for i in range(self.processing_workers)
        ]
        
        logger.info(f"✅ {self.processing_workers} workers iniciados")
    
    async def create_stream(self, stream_id: str, stream_type: DataStreamType, 
                           processing_mode: ProcessingMode = ProcessingMode.REAL_TIME) -> DataStream:
        """Crear un nuevo stream de datos"""
        stream = DataStream(
            stream_id=stream_id,
            stream_type=stream_type,
            processing_mode=processing_mode
        )
        
        self.active_streams[stream_id] = stream
        logger.info(f"📊 Stream creado: {stream_id} ({stream_type.value})")
        
        return stream
    
    async def add_data_point(self, stream_id: str, data_point: DataPoint):
        """Agregar punto de datos al stream"""
        if stream_id not in self.active_streams:
            raise ValueError(f"Stream {stream_id} no encontrado")
        
        stream = self.active_streams[stream_id]
        stream.data_points.append(data_point)
        
        # Mantener tamaño del buffer
        if len(stream.data_points) > stream.buffer_size:
            stream.data_points = stream.data_points[-stream.buffer_size:]
        
        # Agregar a la cola de procesamiento
        await self.processing_queue.put((stream_id, data_point))
        
        logger.debug(f"📈 Datos agregados a {stream_id}: {data_point.value}")
    
    async def _processing_worker(self, worker_name: str):
        """Worker para procesar datos en background"""
        logger.info(f"👷 Worker {worker_name} iniciado")
        
        while True:
            try:
                stream_id, data_point = await self.processing_queue.get()
                
                # Procesar punto de datos
                await self._process_data_point(stream_id, data_point)
                
                # Simular tiempo de procesamiento
                await asyncio.sleep(random.uniform(0.001, 0.01))
                
                self.processing_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en worker {worker_name}: {e}")
    
    async def _process_data_point(self, stream_id: str, data_point: DataPoint):
        """Procesar un punto de datos individual"""
        # Validar calidad de datos
        if data_point.quality_score < 0.5:
            logger.warning(f"⚠️ Datos de baja calidad en {stream_id}: {data_point.quality_score}")
        
        # Aplicar transformaciones según el tipo de stream
        stream = self.active_streams[stream_id]
        
        if stream.stream_type == DataStreamType.METRICS:
            await self._process_metrics_data(stream_id, data_point)
        elif stream.stream_type == DataStreamType.LOGS:
            await self._process_logs_data(stream_id, data_point)
        elif stream.stream_type == DataStreamType.EVENTS:
            await self._process_events_data(stream_id, data_point)
    
    async def _process_metrics_data(self, stream_id: str, data_point: DataPoint):
        """Procesar datos de métricas"""
        # Normalizar valores numéricos
        if isinstance(data_point.value, (int, float)):
            # Aplicar normalización básica
            pass
        
        # Agregar metadatos de procesamiento
        data_point.metadata['processed'] = True
        data_point.metadata['processing_timestamp'] = datetime.now()
    
    async def _process_logs_data(self, stream_id: str, data_point: DataPoint):
        """Procesar datos de logs"""
        # Extraer información estructurada de logs
        if isinstance(data_point.value, str):
            # Buscar patrones en logs
            if 'ERROR' in data_point.value.upper():
                data_point.metadata['log_level'] = 'ERROR'
                data_point.metadata['priority'] = 'high'
            elif 'WARN' in data_point.value.upper():
                data_point.metadata['log_level'] = 'WARNING'
                data_point.metadata['priority'] = 'medium'
            else:
                data_point.metadata['log_level'] = 'INFO'
                data_point.metadata['priority'] = 'low'
    
    async def _process_events_data(self, stream_id: str, data_point: DataPoint):
        """Procesar datos de eventos"""
        # Categorizar eventos
        if isinstance(data_point.value, dict):
            event_type = data_point.value.get('type', 'unknown')
            data_point.metadata['event_category'] = event_type
            data_point.metadata['event_processed'] = True
    
    def get_stream_status(self, stream_id: str) -> Dict[str, Any]:
        """Obtener estado de un stream específico"""
        if stream_id not in self.active_streams:
            return {'error': 'Stream no encontrado'}
        
        stream = self.active_streams[stream_id]
        return {
            'stream_id': stream_id,
            'stream_type': stream.stream_type.value,
            'data_points_count': len(stream.data_points),
            'processing_mode': stream.processing_mode.value,
            'buffer_usage': len(stream.data_points) / stream.buffer_size,
            'last_update': stream.data_points[-1].timestamp if stream.data_points else None
        }

class ComplexPatternAnalyzer:
    """Analizador de patrones complejos en tiempo real"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pattern_detection_algorithms = config.get('pattern_algorithms', [])
        self.min_pattern_confidence = config.get('min_confidence', 0.7)
        self.pattern_history = []
        self.active_patterns = {}
        
    async def analyze_stream_patterns(self, stream: DataStream) -> List[PatternAnalysis]:
        """Analizar patrones en un stream de datos"""
        if len(stream.data_points) < 10:
            return []
        
        patterns = []
        
        # Detectar patrones temporales
        temporal_patterns = await self._detect_temporal_patterns(stream)
        patterns.extend(temporal_patterns)
        
        # Detectar patrones de secuencia
        sequence_patterns = await self._detect_sequence_patterns(stream)
        patterns.extend(sequence_patterns)
        
        # Detectar patrones cíclicos
        cyclic_patterns = await self._detect_cyclic_patterns(stream)
        patterns.extend(cyclic_patterns)
        
        # Filtrar por confianza mínima
        valid_patterns = [p for p in patterns if p.confidence >= self.min_pattern_confidence]
        
        # Actualizar historial
        self.pattern_history.extend(valid_patterns)
        
        return valid_patterns
    
    async def _detect_temporal_patterns(self, stream: DataStream) -> List[PatternAnalysis]:
        """Detectar patrones temporales"""
        patterns = []
        
        if len(stream.data_points) < 20:
            return patterns
        
        # Analizar tendencias
        values = [dp.value for dp in stream.data_points if isinstance(dp.value, (int, float))]
        if len(values) >= 10:
            # Calcular tendencia lineal
            x = np.arange(len(values))
            slope = np.polyfit(x, values, 1)[0]
            
            if abs(slope) > 0.1:  # Umbral de tendencia
                trend_pattern = PatternAnalysis(
                    pattern_type="trend",
                    confidence=min(0.8 + abs(slope), 0.95),
                    start_time=stream.data_points[0].timestamp,
                    end_time=stream.data_points[-1].timestamp,
                    pattern_data=stream.data_points,
                    metadata={'slope': slope, 'trend_direction': 'increasing' if slope > 0 else 'decreasing'}
                )
                patterns.append(trend_pattern)
        
        return patterns
    
    async def _detect_sequence_patterns(self, stream: DataStream) -> List[PatternAnalysis]:
        """Detectar patrones de secuencia"""
        patterns = []
        
        if len(stream.data_points) < 15:
            return patterns
        
        # Buscar secuencias repetitivas
        values = [dp.value for dp in stream.data_points if isinstance(dp.value, (int, float))]
        
        # Detectar oscilaciones
        if len(values) >= 10:
            diffs = np.diff(values)
            oscillation_score = np.std(diffs)
            
            if oscillation_score > np.std(values) * 0.3:
                oscillation_pattern = PatternAnalysis(
                    pattern_type="oscillation",
                    confidence=min(0.7 + oscillation_score, 0.9),
                    start_time=stream.data_points[0].timestamp,
                    end_time=stream.data_points[-1].timestamp,
                    pattern_data=stream.data_points,
                    metadata={'oscillation_score': oscillation_score, 'frequency': 'variable'}
                )
                patterns.append(oscillation_pattern)
        
        return patterns
    
    async def _detect_cyclic_patterns(self, stream: DataStream) -> List[PatternAnalysis]:
        """Detectar patrones cíclicos"""
        patterns = []
        
        if len(stream.data_points) < 30:
            return patterns
        
        # Buscar patrones estacionales
        values = [dp.value for dp in stream.data_points if isinstance(dp.value, (int, float))]
        
        if len(values) >= 20:
            # Detectar periodicidad usando autocorrelación
            autocorr = np.correlate(values, values, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            
            # Encontrar picos en autocorrelación
            peaks = []
            for i in range(1, len(autocorr)-1):
                if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                    peaks.append(i)
            
            if len(peaks) > 1:
                # Calcular período promedio
                periods = np.diff(peaks)
                avg_period = np.mean(periods)
                
                cyclic_pattern = PatternAnalysis(
                    pattern_type="cyclic",
                    confidence=0.75,
                    start_time=stream.data_points[0].timestamp,
                    end_time=stream.data_points[-1].timestamp,
                    pattern_data=stream.data_points,
                    metadata={'average_period': avg_period, 'peak_count': len(peaks)}
                )
                patterns.append(cyclic_pattern)
        
        return patterns
    
    def get_pattern_summary(self) -> Dict[str, Any]:
        """Obtener resumen de patrones detectados"""
        if not self.pattern_history:
            return {'total_patterns': 0}
        
        pattern_types = [p.pattern_type for p in self.pattern_history]
        pattern_counts = {}
        
        for pattern_type in set(pattern_types):
            pattern_counts[pattern_type] = pattern_types.count(pattern_type)
        
        return {
            'total_patterns': len(self.pattern_history),
            'pattern_types': pattern_counts,
            'average_confidence': np.mean([p.confidence for p in self.pattern_history]),
            'recent_patterns': len([p for p in self.pattern_history 
                                  if p.end_time > datetime.now() - timedelta(hours=1)])
        }

class AdvancedAnomalyDetector:
    """Detector avanzado de anomalías"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.detection_thresholds = config.get('detection_thresholds', {})
        self.anomaly_history = []
        self.active_anomalies = {}
        self.detection_algorithms = [
            'statistical_threshold',
            'moving_average',
            'isolation_forest',
            'local_outlier_factor'
        ]
        
    async def detect_anomalies(self, stream: DataStream) -> List[AnomalyDetection]:
        """Detectar anomalías en un stream de datos"""
        anomalies = []
        
        if len(stream.data_points) < 5:
            return anomalies
        
        # Aplicar múltiples algoritmos de detección
        for algorithm in self.detection_algorithms:
            algorithm_anomalies = await self._apply_detection_algorithm(
                algorithm, stream
            )
            anomalies.extend(algorithm_anomalies)
        
        # Consolidar y filtrar anomalías
        consolidated_anomalies = self._consolidate_anomalies(anomalies)
        
        # Actualizar historial
        self.anomaly_history.extend(consolidated_anomalies)
        
        return consolidated_anomalies
    
    async def _apply_detection_algorithm(self, algorithm: str, stream: DataStream) -> List[AnomalyDetection]:
        """Aplicar algoritmo específico de detección"""
        anomalies = []
        
        if algorithm == 'statistical_threshold':
            anomalies = await self._statistical_threshold_detection(stream)
        elif algorithm == 'moving_average':
            anomalies = await self._moving_average_detection(stream)
        elif algorithm == 'isolation_forest':
            anomalies = await self._isolation_forest_detection(stream)
        elif algorithm == 'local_outlier_factor':
            anomalies = await self._local_outlier_factor_detection(stream)
        
        return anomalies
    
    async def _statistical_threshold_detection(self, stream: DataStream) -> List[AnomalyDetection]:
        """Detección basada en umbrales estadísticos"""
        anomalies = []
        
        numeric_points = [dp for dp in stream.data_points if isinstance(dp.value, (int, float))]
        if len(numeric_points) < 5:
            return anomalies
        
        values = [dp.value for dp in numeric_points]
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        # Umbral de 3 desviaciones estándar
        threshold = 3 * std_val
        
        for point in numeric_points[-10:]:  # Solo últimos 10 puntos
            if abs(point.value - mean_val) > threshold:
                anomaly = AnomalyDetection(
                    anomaly_type=AnomalyType.OUTLIER,
                    severity=min(abs(point.value - mean_val) / threshold, 1.0),
                    timestamp=point.timestamp,
                    data_point=point,
                    confidence=0.8,
                    description=f"Valor {point.value} excede umbral estadístico",
                    recommendations=["Verificar integridad de datos", "Revisar configuración del sensor"]
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    async def _moving_average_detection(self, stream: DataStream) -> List[AnomalyDetection]:
        """Detección basada en media móvil"""
        anomalies = []
        
        numeric_points = [dp for dp in stream.data_points if isinstance(dp.value, (int, float))]
        if len(numeric_points) < 10:
            return anomalies
        
        values = [dp.value for dp in numeric_points]
        window_size = 5
        
        for i in range(window_size, len(values)):
            window_values = values[i-window_size:i]
            moving_avg = np.mean(window_values)
            current_value = values[i]
            
            # Detectar cambios bruscos
            change_ratio = abs(current_value - moving_avg) / (moving_avg + 1e-6)
            
            if change_ratio > 0.5:  # Cambio del 50%
                point = numeric_points[i]
                anomaly = AnomalyDetection(
                    anomaly_type=AnomalyType.SPIKE if current_value > moving_avg else AnomalyType.DROP,
                    severity=min(change_ratio, 1.0),
                    timestamp=point.timestamp,
                    data_point=point,
                    confidence=0.7,
                    description=f"Cambio brusco del {change_ratio*100:.1f}% respecto a la media móvil",
                    recommendations=["Investigar causa del cambio", "Verificar estado del sistema"]
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    async def _isolation_forest_detection(self, stream: DataStream) -> List[AnomalyDetection]:
        """Detección usando algoritmo de bosque de aislamiento (simulado)"""
        anomalies = []
        
        numeric_points = [dp for dp in stream.data_points if isinstance(dp.value, (int, float))]
        if len(numeric_points) < 10:
            return anomalies
        
        values = [dp.value for dp in numeric_points]
        
        # Simular detección de outliers usando percentiles
        q25, q75 = np.percentile(values, [25, 75])
        iqr = q75 - q25
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr
        
        for point in numeric_points[-5:]:  # Solo últimos 5 puntos
            if point.value < lower_bound or point.value > upper_bound:
                anomaly = AnomalyDetection(
                    anomaly_type=AnomalyType.OUTLIER,
                    severity=0.6,
                    timestamp=point.timestamp,
                    data_point=point,
                    confidence=0.75,
                    description=f"Valor {point.value} identificado como outlier por IQR",
                    recommendations=["Revisar validez del dato", "Verificar calibración"]
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    async def _local_outlier_factor_detection(self, stream: DataStream) -> List[AnomalyDetection]:
        """Detección usando factor de outlier local (simulado)"""
        anomalies = []
        
        numeric_points = [dp for dp in stream.data_points if isinstance(dp.value, (int, float))]
        if len(numeric_points) < 8:
            return anomalies
        
        values = [dp.value for dp in numeric_points]
        
        # Simular LOF usando densidad local
        for i in range(4, len(values)):
            local_window = values[i-4:i+1]
            local_mean = np.mean(local_window)
            local_std = np.std(local_window)
            
            if local_std > 0:
                lof_score = abs(values[i] - local_mean) / local_std
                
                if lof_score > 2.0:  # Umbral de LOF
                    point = numeric_points[i]
                    anomaly = AnomalyDetection(
                        anomaly_type=AnomalyType.OUTLIER,
                        severity=min(lof_score / 3.0, 1.0),
                        timestamp=point.timestamp,
                        data_point=point,
                        confidence=0.7,
                        description=f"Valor {point.value} identificado como outlier por LOF (score: {lof_score:.2f})",
                        recommendations=["Analizar contexto temporal", "Verificar consistencia de datos"]
                    )
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _consolidate_anomalies(self, anomalies: List[AnomalyDetection]) -> List[AnomalyDetection]:
        """Consolidar anomalías similares"""
        if not anomalies:
            return []
        
        # Agrupar por timestamp cercano (dentro de 1 minuto)
        consolidated = []
        processed_timestamps = set()
        
        for anomaly in anomalies:
            if anomaly.timestamp in processed_timestamps:
                continue
            
            # Buscar anomalías similares en tiempo
            similar_anomalies = [
                a for a in anomalies
                if abs((a.timestamp - anomaly.timestamp).total_seconds()) < 60
                and a.anomaly_type == anomaly.anomaly_type
            ]
            
            if len(similar_anomalies) > 1:
                # Consolidar en una sola anomalía
                max_severity = max(a.severity for a in similar_anomalies)
                max_confidence = max(a.confidence for a in similar_anomalies)
                
                consolidated_anomaly = AnomalyDetection(
                    anomaly_type=anomaly.anomaly_type,
                    severity=max_severity,
                    timestamp=anomaly.timestamp,
                    data_point=anomaly.data_point,
                    confidence=max_confidence,
                    description=f"Anomalía consolidada: {anomaly.description}",
                    recommendations=anomaly.recommendations
                )
                
                consolidated.append(consolidated_anomaly)
                
                # Marcar timestamps como procesados
                for a in similar_anomalies:
                    processed_timestamps.add(a.timestamp)
            else:
                consolidated.append(anomaly)
                processed_timestamps.add(anomaly.timestamp)
        
        return consolidated
    
    def get_anomaly_summary(self) -> Dict[str, Any]:
        """Obtener resumen de anomalías detectadas"""
        if not self.anomaly_history:
            return {'total_anomalies': 0}
        
        anomaly_types = [a.anomaly_type.value for a in self.anomaly_history]
        type_counts = {}
        
        for anomaly_type in set(anomaly_types):
            type_counts[anomaly_type] = anomaly_types.count(anomaly_type)
        
        return {
            'total_anomalies': len(self.anomaly_history),
            'anomaly_types': type_counts,
            'average_severity': np.mean([a.severity for a in self.anomaly_history]),
            'average_confidence': np.mean([a.confidence for a in self.anomaly_history]),
            'recent_anomalies': len([a for a in self.anomaly_history 
                                   if a.timestamp > datetime.now() - timedelta(hours=1)])
        }

class RealtimeDataAnalyticsSystem:
    """Sistema principal de Análisis de Datos en Tiempo Real v4.8"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.stream_processor = StreamDataProcessor(config)
        self.pattern_analyzer = ComplexPatternAnalyzer(config)
        self.anomaly_detector = AdvancedAnomalyDetector(config)
        self.analytics_history = []
        self.performance_metrics = {}
        
    async def start(self):
        """Iniciar el sistema"""
        logger.info("🚀 Iniciando Sistema de Análisis de Datos en Tiempo Real v4.8")
        
        await self.stream_processor.start()
        
        logger.info("✅ Sistema iniciado correctamente")
    
    async def create_analytics_stream(self, stream_id: str, stream_type: DataStreamType,
                                    processing_mode: ProcessingMode = ProcessingMode.REAL_TIME) -> DataStream:
        """Crear stream de análisis"""
        return await self.stream_processor.create_stream(stream_id, stream_type, processing_mode)
    
    async def add_data_to_stream(self, stream_id: str, data_point: DataPoint):
        """Agregar datos a un stream"""
        await self.stream_processor.add_data_point(stream_id, data_point)
    
    async def run_analytics_cycle(self, stream_id: str) -> Dict[str, Any]:
        """Ejecutar ciclo completo de análisis"""
        if stream_id not in self.stream_processor.active_streams:
            raise ValueError(f"Stream {stream_id} no encontrado")
        
        stream = self.stream_processor.active_streams[stream_id]
        
        logger.info(f"📊 Ejecutando ciclo de análisis para stream: {stream_id}")
        
        # Analizar patrones
        patterns = await self.pattern_analyzer.analyze_stream_patterns(stream)
        
        # Detectar anomalías
        anomalies = await self.anomaly_detector.detect_anomalies(stream)
        
        # Generar resumen de análisis
        analysis_summary = {
            'stream_id': stream_id,
            'timestamp': datetime.now(),
            'data_points_count': len(stream.data_points),
            'patterns_detected': len(patterns),
            'anomalies_detected': len(anomalies),
            'patterns': patterns,
            'anomalies': anomalies,
            'stream_status': self.stream_processor.get_stream_status(stream_id)
        }
        
        # Registrar en historial
        self.analytics_history.append(analysis_summary)
        
        # Actualizar métricas de rendimiento
        self._update_performance_metrics(analysis_summary)
        
        return analysis_summary
    
    async def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Ejecutar análisis completo de todos los streams"""
        logger.info("🔍 Ejecutando análisis completo del sistema")
        
        comprehensive_results = {}
        
        for stream_id in self.stream_processor.active_streams:
            try:
                stream_analysis = await self.run_analytics_cycle(stream_id)
                comprehensive_results[stream_id] = stream_analysis
            except Exception as e:
                logger.error(f"Error analizando stream {stream_id}: {e}")
                comprehensive_results[stream_id] = {'error': str(e)}
        
        # Resumen general
        total_patterns = sum(len(r.get('patterns', [])) for r in comprehensive_results.values() 
                           if isinstance(r, dict) and 'patterns' in r)
        total_anomalies = sum(len(r.get('anomalies', [])) for r in comprehensive_results.values() 
                             if isinstance(r, dict) and 'anomalies' in r)
        
        comprehensive_summary = {
            'timestamp': datetime.now(),
            'total_streams': len(comprehensive_results),
            'total_patterns': total_patterns,
            'total_anomalies': total_anomalies,
            'stream_analyses': comprehensive_results,
            'pattern_summary': self.pattern_analyzer.get_pattern_summary(),
            'anomaly_summary': self.anomaly_detector.get_anomaly_summary()
        }
        
        return comprehensive_summary
    
    def _update_performance_metrics(self, analysis_summary: Dict[str, Any]):
        """Actualizar métricas de rendimiento"""
        if 'analysis_times' not in self.performance_metrics:
            self.performance_metrics['analysis_times'] = []
        
        # Simular tiempo de análisis
        analysis_time = random.uniform(0.1, 0.5)
        self.performance_metrics['analysis_times'].append(analysis_time)
        
        self.performance_metrics['total_analyses'] = len(self.analytics_history)
        self.performance_metrics['average_analysis_time'] = np.mean(
            self.performance_metrics['analysis_times'][-10:]
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema"""
        return {
            'system_name': 'Realtime Data Analytics System v4.8',
            'status': 'active',
            'total_streams': len(self.stream_processor.active_streams),
            'total_analyses': len(self.analytics_history),
            'performance_metrics': self.performance_metrics,
            'pattern_summary': self.pattern_analyzer.get_pattern_summary(),
            'anomaly_summary': self.anomaly_detector.get_anomaly_summary(),
            'timestamp': datetime.now()
        }

# Configuración del sistema
SYSTEM_CONFIG = {
    'max_buffer_size': 10000,
    'processing_workers': 4,
    'batch_size': 100,
    'pattern_algorithms': ['temporal', 'sequence', 'cyclic'],
    'min_confidence': 0.7,
    'detection_thresholds': {
        'statistical': 3.0,
        'moving_average': 0.5,
        'isolation_forest': 0.6,
        'local_outlier_factor': 2.0
    }
}

async def main():
    """Función principal para demostración"""
    system = RealtimeDataAnalyticsSystem(SYSTEM_CONFIG)
    await system.start()
    
    # Crear streams de demostración
    metrics_stream = await system.create_analytics_stream(
        'demo_metrics', DataStreamType.METRICS
    )
    logs_stream = await system.create_analytics_stream(
        'demo_logs', DataStreamType.LOGS
    )
    
    # Agregar datos de demostración
    for i in range(50):
        # Datos de métricas
        metrics_point = DataPoint(
            timestamp=datetime.now() + timedelta(seconds=i),
            value=100 + i * 2 + random.uniform(-5, 5),
            source='demo_sensor',
            data_type='temperature'
        )
        await system.add_data_to_stream('demo_metrics', metrics_point)
        
        # Datos de logs
        log_point = DataPoint(
            timestamp=datetime.now() + timedelta(seconds=i),
            value=f"Log entry {i}: System status normal",
            source='demo_service',
            data_type='application_log'
        )
        await system.add_data_to_stream('demo_logs', log_point)
        
        await asyncio.sleep(0.01)
    
    # Ejecutar análisis
    metrics_analysis = await system.run_analytics_cycle('demo_metrics')
    logs_analysis = await system.run_analytics_cycle('demo_logs')
    
    # Análisis completo
    comprehensive_analysis = await system.run_comprehensive_analysis()
    
    # Mostrar estado del sistema
    status = system.get_system_status()
    
    print("📊 Sistema de Análisis de Datos en Tiempo Real v4.8 - Demo Completado")
    print(f"📈 Total de streams: {status['total_streams']}")
    print(f"🔍 Total de análisis: {status['total_analyses']}")
    print(f"📊 Patrones detectados: {status['pattern_summary'].get('total_patterns', 0)}")
    print(f"⚠️ Anomalías detectadas: {status['anomaly_summary'].get('total_anomalies', 0)}")

if __name__ == "__main__":
    asyncio.run(main())
