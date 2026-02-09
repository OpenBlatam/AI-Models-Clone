"""
AWS CloudWatch Integration
===========================

Integración con AWS CloudWatch para:
- Logging estructurado
- Métricas personalizadas
- Alarmas
- Dashboards
"""

import logging
import json
from typing import Dict, Optional, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None


class CloudWatchLogger:
    """Logger para AWS CloudWatch Logs"""
    
    def __init__(
        self,
        log_group: str,
        log_stream: str = "default",
        region: str = "us-east-1"
    ):
        self.log_group = log_group
        self.log_stream = log_stream
        self.region = region
        self.client = None
        self.sequence_token = None
        self._setup()
    
    def _setup(self):
        """Configura cliente de CloudWatch Logs"""
        if not BOTO3_AVAILABLE:
            logger.warning("boto3 no disponible")
            return
        
        try:
            self.client = boto3.client('logs', region_name=self.region)
            
            # Crear log group si no existe
            try:
                self.client.create_log_group(logGroupName=self.log_group)
            except ClientError as e:
                if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                    raise
            
            # Crear log stream si no existe
            try:
                self.client.create_log_stream(
                    logGroupName=self.log_group,
                    logStreamName=self.log_stream
                )
            except ClientError as e:
                if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                    raise
            
            logger.info(f"CloudWatch Logger configurado: {self.log_group}/{self.log_stream}")
        except Exception as e:
            logger.error(f"Error configurando CloudWatch Logger: {e}")
    
    def log(
        self,
        message: str,
        level: str = "INFO",
        **kwargs
    ):
        """
        Envía log a CloudWatch
        
        Args:
            message: Mensaje del log
            level: Nivel (INFO, ERROR, WARNING, etc.)
            **kwargs: Datos adicionales
        """
        if not self.client:
            return
        
        try:
            log_event = {
                'timestamp': int(datetime.utcnow().timestamp() * 1000),
                'message': json.dumps({
                    "level": level,
                    "message": message,
                    **kwargs
                })
            }
            
            kwargs = {
                'logGroupName': self.log_group,
                'logStreamName': self.log_stream,
                'logEvents': [log_event]
            }
            
            if self.sequence_token:
                kwargs['sequenceToken'] = self.sequence_token
            
            response = self.client.put_log_events(**kwargs)
            self.sequence_token = response.get('nextSequenceToken')
        except ClientError as e:
            logger.error(f"Error enviando log a CloudWatch: {e}")


class CloudWatchMetrics:
    """Gestor de métricas para CloudWatch"""
    
    def __init__(self, region: str = "us-east-1", namespace: str = "BlatamAcademy"):
        self.region = region
        self.namespace = namespace
        self.client = None
        self.metric_buffer: List[Dict] = []
        self._setup()
    
    def _setup(self):
        """Configura cliente de CloudWatch"""
        if not BOTO3_AVAILABLE:
            logger.warning("boto3 no disponible")
            return
        
        try:
            self.client = boto3.client('cloudwatch', region_name=self.region)
            logger.info(f"CloudWatch Metrics configurado: {self.namespace}")
        except Exception as e:
            logger.error(f"Error configurando CloudWatch Metrics: {e}")
    
    def put_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "Count",
        dimensions: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Publica una métrica
        
        Args:
            metric_name: Nombre de la métrica
            value: Valor
            unit: Unidad (Count, Bytes, Seconds, etc.)
            dimensions: Dimensiones adicionales
            timestamp: Timestamp (default: ahora)
        """
        if not self.client:
            return
        
        metric_data = {
            'MetricName': metric_name,
            'Value': value,
            'Unit': unit,
            'Timestamp': timestamp or datetime.utcnow()
        }
        
        if dimensions:
            metric_data['Dimensions'] = [
                {'Name': k, 'Value': v} for k, v in dimensions.items()
            ]
        
        self.metric_buffer.append(metric_data)
        
        # Enviar en batch (máximo 20 métricas)
        if len(self.metric_buffer) >= 20:
            self.flush_metrics()
    
    def flush_metrics(self):
        """Envía métricas en buffer a CloudWatch"""
        if not self.client or not self.metric_buffer:
            return
        
        try:
            self.client.put_metric_data(
                Namespace=self.namespace,
                MetricData=self.metric_buffer
            )
            self.metric_buffer.clear()
        except ClientError as e:
            logger.error(f"Error enviando métricas: {e}")
    
    def increment_counter(
        self,
        metric_name: str,
        value: float = 1.0,
        dimensions: Optional[Dict[str, str]] = None
    ):
        """Incrementa un contador"""
        self.put_metric(metric_name, value, "Count", dimensions)
    
    def record_latency(
        self,
        metric_name: str,
        latency_seconds: float,
        dimensions: Optional[Dict[str, str]] = None
    ):
        """Registra latencia"""
        self.put_metric(metric_name, latency_seconds, "Seconds", dimensions)


# Instancias globales
cloudwatch_logger = CloudWatchLogger("blatam-academy-logs")
cloudwatch_metrics = CloudWatchMetrics()




