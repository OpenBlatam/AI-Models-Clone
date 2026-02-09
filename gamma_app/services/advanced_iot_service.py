"""
Advanced IoT Service with Device Management and Real-time Data Processing
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import random
import math
from collections import defaultdict, deque
import statistics

from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class DeviceType(Enum):
    """IoT device types"""
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    GATEWAY = "gateway"
    CAMERA = "camera"
    SMART_DEVICE = "smart_device"
    WEARABLE = "wearable"
    VEHICLE = "vehicle"
    INDUSTRIAL = "industrial"
    HOME_AUTOMATION = "home_automation"
    ENVIRONMENTAL = "environmental"

class DeviceStatus(Enum):
    """Device status"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    UNKNOWN = "unknown"

class DataType(Enum):
    """Data types"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    LIGHT = "light"
    MOTION = "motion"
    SOUND = "sound"
    VIBRATION = "vibration"
    LOCATION = "location"
    BATTERY = "battery"
    SIGNAL_STRENGTH = "signal_strength"
    CUSTOM = "custom"

class AlertLevel(Enum):
    """Alert levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class IoTDevice:
    """IoT device definition"""
    id: str
    name: str
    device_type: DeviceType
    status: DeviceStatus
    location: Dict[str, float] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    battery_level: Optional[float] = None
    signal_strength: Optional[float] = None
    firmware_version: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SensorData:
    """Sensor data point"""
    id: str
    device_id: str
    data_type: DataType
    value: Union[float, int, str, bool]
    unit: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    quality: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DeviceCommand:
    """Device command"""
    id: str
    device_id: str
    command: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    status: str = "pending"
    result: Optional[Any] = None

@dataclass
class Alert:
    """IoT alert"""
    id: str
    device_id: str
    alert_type: str
    level: AlertLevel
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class DeviceGroup:
    """Device group"""
    id: str
    name: str
    description: str
    device_ids: List[str] = field(default_factory=list)
    rules: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

class AdvancedIoTService:
    """Advanced IoT Service with Device Management and Real-time Data Processing"""
    
    def __init__(self):
        self.devices = {}
        self.device_groups = {}
        self.sensor_data = {}
        self.device_commands = {}
        self.alerts = {}
        self.data_streams = {}
        self.device_callbacks = defaultdict(list)
        self.alert_callbacks = defaultdict(list)
        
        # Data processing
        self.data_buffer = defaultdict(lambda: deque(maxlen=1000))
        self.data_aggregators = {}
        self.anomaly_detectors = {}
        
        # Background tasks
        self.data_processing_queue = asyncio.Queue()
        self.command_queue = asyncio.Queue()
        self.alert_queue = asyncio.Queue()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("Advanced IoT Service initialized")
    
    def _start_background_tasks(self):
        """Start background tasks"""
        try:
            # Start data processing
            asyncio.create_task(self._process_sensor_data())
            
            # Start command processing
            asyncio.create_task(self._process_device_commands())
            
            # Start alert processing
            asyncio.create_task(self._process_alerts())
            
            # Start device monitoring
            asyncio.create_task(self._monitor_devices())
            
            # Start data aggregation
            asyncio.create_task(self._aggregate_data())
            
            # Start anomaly detection
            asyncio.create_task(self._detect_anomalies())
            
            logger.info("Background tasks started")
            
        except Exception as e:
            logger.error(f"Error starting background tasks: {e}")
    
    async def _process_sensor_data(self):
        """Process sensor data"""
        try:
            while True:
                try:
                    data = await asyncio.wait_for(self.data_processing_queue.get(), timeout=1.0)
                    await self._handle_sensor_data(data)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing sensor data: {e}")
                    
        except Exception as e:
            logger.error(f"Error in sensor data processor: {e}")
    
    async def _process_device_commands(self):
        """Process device commands"""
        try:
            while True:
                try:
                    command = await asyncio.wait_for(self.command_queue.get(), timeout=1.0)
                    await self._execute_device_command(command)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing device command: {e}")
                    
        except Exception as e:
            logger.error(f"Error in device command processor: {e}")
    
    async def _process_alerts(self):
        """Process alerts"""
        try:
            while True:
                try:
                    alert = await asyncio.wait_for(self.alert_queue.get(), timeout=1.0)
                    await self._handle_alert(alert)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing alert: {e}")
                    
        except Exception as e:
            logger.error(f"Error in alert processor: {e}")
    
    async def _monitor_devices(self):
        """Monitor device health"""
        try:
            while True:
                try:
                    await asyncio.sleep(30)  # Check every 30 seconds
                    
                    current_time = datetime.utcnow()
                    
                    for device_id, device in self.devices.items():
                        # Check if device is offline
                        time_since_last_seen = current_time - device.last_seen
                        
                        if time_since_last_seen > timedelta(minutes=5) and device.status == DeviceStatus.ONLINE:
                            device.status = DeviceStatus.OFFLINE
                            await self._create_alert(
                                device_id,
                                "device_offline",
                                AlertLevel.WARNING,
                                f"Device {device.name} has been offline for {time_since_last_seen}"
                            )
                        
                        # Check battery level
                        if device.battery_level is not None and device.battery_level < 20:
                            await self._create_alert(
                                device_id,
                                "low_battery",
                                AlertLevel.WARNING,
                                f"Device {device.name} has low battery: {device.battery_level}%"
                            )
                        
                        # Check signal strength
                        if device.signal_strength is not None and device.signal_strength < -80:
                            await self._create_alert(
                                device_id,
                                "weak_signal",
                                AlertLevel.WARNING,
                                f"Device {device.name} has weak signal: {device.signal_strength} dBm"
                            )
                    
                except Exception as e:
                    logger.error(f"Error monitoring devices: {e}")
                    
        except Exception as e:
            logger.error(f"Error in device monitor: {e}")
    
    async def _aggregate_data(self):
        """Aggregate sensor data"""
        try:
            while True:
                try:
                    await asyncio.sleep(60)  # Aggregate every minute
                    
                    for device_id, data_buffer in self.data_buffer.items():
                        if len(data_buffer) > 0:
                            # Calculate statistics
                            values = [d.value for d in data_buffer if isinstance(d.value, (int, float))]
                            
                            if values:
                                stats = {
                                    'count': len(values),
                                    'mean': statistics.mean(values),
                                    'median': statistics.median(values),
                                    'min': min(values),
                                    'max': max(values),
                                    'std': statistics.stdev(values) if len(values) > 1 else 0
                                }
                                
                                # Store aggregated data
                                self.data_aggregators[device_id] = {
                                    'timestamp': datetime.utcnow(),
                                    'statistics': stats
                                }
                    
                except Exception as e:
                    logger.error(f"Error aggregating data: {e}")
                    
        except Exception as e:
            logger.error(f"Error in data aggregator: {e}")
    
    async def _detect_anomalies(self):
        """Detect anomalies in sensor data"""
        try:
            while True:
                try:
                    await asyncio.sleep(30)  # Check every 30 seconds
                    
                    for device_id, data_buffer in self.data_buffer.items():
                        if len(data_buffer) < 10:  # Need at least 10 data points
                            continue
                        
                        # Get recent values
                        recent_values = [d.value for d in list(data_buffer)[-10:] if isinstance(d.value, (int, float))]
                        
                        if len(recent_values) < 5:
                            continue
                        
                        # Simple anomaly detection using z-score
                        mean = statistics.mean(recent_values)
                        std = statistics.stdev(recent_values) if len(recent_values) > 1 else 0
                        
                        if std > 0:
                            for i, value in enumerate(recent_values[-3:]):  # Check last 3 values
                                z_score = abs((value - mean) / std)
                                
                                if z_score > 3:  # Anomaly threshold
                                    await self._create_alert(
                                        device_id,
                                        "anomaly_detected",
                                        AlertLevel.WARNING,
                                        f"Anomalous value detected: {value} (z-score: {z_score:.2f})",
                                        {'value': value, 'z_score': z_score, 'mean': mean, 'std': std}
                                    )
                    
                except Exception as e:
                    logger.error(f"Error detecting anomalies: {e}")
                    
        except Exception as e:
            logger.error(f"Error in anomaly detector: {e}")
    
    async def register_device(self, device: IoTDevice) -> str:
        """Register IoT device"""
        try:
            device_id = str(uuid.uuid4())
            device.id = device_id
            device.created_at = datetime.utcnow()
            device.last_seen = datetime.utcnow()
            
            self.devices[device_id] = device
            
            # Initialize data buffer
            self.data_buffer[device_id] = deque(maxlen=1000)
            
            logger.info(f"Device registered: {device_id}")
            
            return device_id
            
        except Exception as e:
            logger.error(f"Error registering device: {e}")
            raise
    
    async def send_sensor_data(self, device_id: str, data_type: DataType, value: Union[float, int, str, bool], 
                             unit: str, quality: float = 1.0, metadata: Dict[str, Any] = None) -> str:
        """Send sensor data"""
        try:
            if device_id not in self.devices:
                raise ValueError(f"Device not found: {device_id}")
            
            # Create sensor data
            data_id = str(uuid.uuid4())
            sensor_data = SensorData(
                id=data_id,
                device_id=device_id,
                data_type=data_type,
                value=value,
                unit=unit,
                quality=quality,
                metadata=metadata or {}
            )
            
            # Store data
            self.sensor_data[data_id] = sensor_data
            
            # Add to buffer
            self.data_buffer[device_id].append(sensor_data)
            
            # Update device last seen
            self.devices[device_id].last_seen = datetime.utcnow()
            self.devices[device_id].status = DeviceStatus.ONLINE
            
            # Add to processing queue
            await self.data_processing_queue.put(sensor_data)
            
            logger.info(f"Sensor data sent: {data_id}")
            
            return data_id
            
        except Exception as e:
            logger.error(f"Error sending sensor data: {e}")
            raise
    
    async def _handle_sensor_data(self, sensor_data: SensorData):
        """Handle incoming sensor data"""
        try:
            # Check for threshold alerts
            await self._check_threshold_alerts(sensor_data)
            
            # Trigger callbacks
            for callback in self.device_callbacks[sensor_data.device_id]:
                try:
                    await callback(sensor_data)
                except Exception as e:
                    logger.error(f"Error in device callback: {e}")
            
            logger.info(f"Sensor data processed: {sensor_data.id}")
            
        except Exception as e:
            logger.error(f"Error handling sensor data: {e}")
    
    async def _check_threshold_alerts(self, sensor_data: SensorData):
        """Check for threshold-based alerts"""
        try:
            device = self.devices[sensor_data.device_id]
            
            # Define thresholds based on data type
            thresholds = {
                DataType.TEMPERATURE: {'min': -10, 'max': 50},
                DataType.HUMIDITY: {'min': 0, 'max': 100},
                DataType.PRESSURE: {'min': 800, 'max': 1200},
                DataType.BATTERY: {'min': 10, 'max': 100}
            }
            
            if sensor_data.data_type in thresholds and isinstance(sensor_data.value, (int, float)):
                threshold = thresholds[sensor_data.data_type]
                value = sensor_data.value
                
                if value < threshold['min']:
                    await self._create_alert(
                        sensor_data.device_id,
                        f"{sensor_data.data_type.value}_low",
                        AlertLevel.WARNING,
                        f"{sensor_data.data_type.value} is below threshold: {value} {sensor_data.unit}",
                        {'value': value, 'threshold': threshold['min'], 'unit': sensor_data.unit}
                    )
                
                elif value > threshold['max']:
                    await self._create_alert(
                        sensor_data.device_id,
                        f"{sensor_data.data_type.value}_high",
                        AlertLevel.WARNING,
                        f"{sensor_data.data_type.value} is above threshold: {value} {sensor_data.unit}",
                        {'value': value, 'threshold': threshold['max'], 'unit': sensor_data.unit}
                    )
            
        except Exception as e:
            logger.error(f"Error checking threshold alerts: {e}")
    
    async def send_device_command(self, device_id: str, command: str, parameters: Dict[str, Any] = None, 
                                priority: int = 0) -> str:
        """Send command to device"""
        try:
            if device_id not in self.devices:
                raise ValueError(f"Device not found: {device_id}")
            
            # Create command
            command_id = str(uuid.uuid4())
            device_command = DeviceCommand(
                id=command_id,
                device_id=device_id,
                command=command,
                parameters=parameters or {},
                priority=priority
            )
            
            self.device_commands[command_id] = device_command
            
            # Add to command queue
            await self.command_queue.put(device_command)
            
            logger.info(f"Device command sent: {command_id}")
            
            return command_id
            
        except Exception as e:
            logger.error(f"Error sending device command: {e}")
            raise
    
    async def _execute_device_command(self, command: DeviceCommand):
        """Execute device command"""
        try:
            command.status = "executing"
            command.executed_at = datetime.utcnow()
            
            # Mock command execution
            # In a real implementation, this would send the command to the actual device
            
            await asyncio.sleep(1)  # Simulate execution time
            
            # Mock successful execution
            command.status = "completed"
            command.result = {"success": True, "message": "Command executed successfully"}
            
            logger.info(f"Device command executed: {command.id}")
            
        except Exception as e:
            logger.error(f"Error executing device command: {e}")
            command.status = "failed"
            command.result = {"success": False, "error": str(e)}
    
    async def _create_alert(self, device_id: str, alert_type: str, level: AlertLevel, 
                          message: str, data: Dict[str, Any] = None):
        """Create alert"""
        try:
            alert_id = str(uuid.uuid4())
            alert = Alert(
                id=alert_id,
                device_id=device_id,
                alert_type=alert_type,
                level=level,
                message=message,
                data=data or {}
            )
            
            self.alerts[alert_id] = alert
            
            # Add to alert queue
            await self.alert_queue.put(alert)
            
            logger.info(f"Alert created: {alert_id}")
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
    
    async def _handle_alert(self, alert: Alert):
        """Handle alert"""
        try:
            # Trigger alert callbacks
            for callback in self.alert_callbacks[alert.device_id]:
                try:
                    await callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")
            
            logger.info(f"Alert handled: {alert.id}")
            
        except Exception as e:
            logger.error(f"Error handling alert: {e}")
    
    async def create_device_group(self, name: str, description: str, device_ids: List[str] = None) -> str:
        """Create device group"""
        try:
            group_id = str(uuid.uuid4())
            group = DeviceGroup(
                id=group_id,
                name=name,
                description=description,
                device_ids=device_ids or []
            )
            
            self.device_groups[group_id] = group
            
            logger.info(f"Device group created: {group_id}")
            
            return group_id
            
        except Exception as e:
            logger.error(f"Error creating device group: {e}")
            raise
    
    async def add_device_to_group(self, group_id: str, device_id: str):
        """Add device to group"""
        try:
            if group_id not in self.device_groups:
                raise ValueError(f"Device group not found: {group_id}")
            
            if device_id not in self.devices:
                raise ValueError(f"Device not found: {device_id}")
            
            group = self.device_groups[group_id]
            if device_id not in group.device_ids:
                group.device_ids.append(device_id)
            
            logger.info(f"Device {device_id} added to group {group_id}")
            
        except Exception as e:
            logger.error(f"Error adding device to group: {e}")
            raise
    
    async def get_device_data(self, device_id: str, data_type: DataType = None, 
                            start_time: datetime = None, end_time: datetime = None) -> List[Dict[str, Any]]:
        """Get device data"""
        try:
            if device_id not in self.devices:
                raise ValueError(f"Device not found: {device_id}")
            
            # Filter data
            filtered_data = []
            for data in self.sensor_data.values():
                if data.device_id == device_id:
                    if data_type and data.data_type != data_type:
                        continue
                    if start_time and data.timestamp < start_time:
                        continue
                    if end_time and data.timestamp > end_time:
                        continue
                    
                    filtered_data.append({
                        'id': data.id,
                        'data_type': data.data_type.value,
                        'value': data.value,
                        'unit': data.unit,
                        'timestamp': data.timestamp.isoformat(),
                        'quality': data.quality,
                        'metadata': data.metadata
                    })
            
            # Sort by timestamp
            filtered_data.sort(key=lambda x: x['timestamp'])
            
            return filtered_data
            
        except Exception as e:
            logger.error(f"Error getting device data: {e}")
            raise
    
    async def get_device_statistics(self, device_id: str, data_type: DataType = None) -> Dict[str, Any]:
        """Get device statistics"""
        try:
            if device_id not in self.devices:
                raise ValueError(f"Device not found: {device_id}")
            
            # Get aggregated data
            if device_id in self.data_aggregators:
                return self.data_aggregators[device_id]
            
            # Calculate from buffer
            data_buffer = self.data_buffer[device_id]
            if not data_buffer:
                return {}
            
            # Filter by data type if specified
            values = []
            for data in data_buffer:
                if data_type is None or data.data_type == data_type:
                    if isinstance(data.value, (int, float)):
                        values.append(data.value)
            
            if not values:
                return {}
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'statistics': {
                    'count': len(values),
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'min': min(values),
                    'max': max(values),
                    'std': statistics.stdev(values) if len(values) > 1 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting device statistics: {e}")
            raise
    
    async def register_device_callback(self, device_id: str, callback: Callable):
        """Register device data callback"""
        try:
            self.device_callbacks[device_id].append(callback)
            logger.info(f"Device callback registered for device: {device_id}")
            
        except Exception as e:
            logger.error(f"Error registering device callback: {e}")
            raise
    
    async def register_alert_callback(self, device_id: str, callback: Callable):
        """Register alert callback"""
        try:
            self.alert_callbacks[device_id].append(callback)
            logger.info(f"Alert callback registered for device: {device_id}")
            
        except Exception as e:
            logger.error(f"Error registering alert callback: {e}")
            raise
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        try:
            status = {
                'service': 'Advanced IoT Service',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'devices': {
                    'total': len(self.devices),
                    'online': len([d for d in self.devices.values() if d.status == DeviceStatus.ONLINE]),
                    'offline': len([d for d in self.devices.values() if d.status == DeviceStatus.OFFLINE]),
                    'by_type': {}
                },
                'device_groups': {
                    'total': len(self.device_groups)
                },
                'sensor_data': {
                    'total_points': len(self.sensor_data),
                    'buffered_points': sum(len(buffer) for buffer in self.data_buffer.values())
                },
                'commands': {
                    'total': len(self.device_commands),
                    'pending': len([c for c in self.device_commands.values() if c.status == 'pending']),
                    'completed': len([c for c in self.device_commands.values() if c.status == 'completed']),
                    'failed': len([c for c in self.device_commands.values() if c.status == 'failed'])
                },
                'alerts': {
                    'total': len(self.alerts),
                    'unacknowledged': len([a for a in self.alerts.values() if not a.acknowledged]),
                    'unresolved': len([a for a in self.alerts.values() if not a.resolved]),
                    'by_level': {}
                },
                'queues': {
                    'data_processing_queue_size': self.data_processing_queue.qsize(),
                    'command_queue_size': self.command_queue.qsize(),
                    'alert_queue_size': self.alert_queue.qsize()
                }
            }
            
            # Count devices by type
            for device in self.devices.values():
                device_type = device.device_type.value
                status['devices']['by_type'][device_type] = status['devices']['by_type'].get(device_type, 0) + 1
            
            # Count alerts by level
            for alert in self.alerts.values():
                level = alert.level.value
                status['alerts']['by_level'][level] = status['alerts']['by_level'].get(level, 0) + 1
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                'service': 'Advanced IoT Service',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


























