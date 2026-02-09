# Enhanced Performance Monitor v3.7

## Overview

The Enhanced Performance Monitor v3.7 is a comprehensive, modular performance monitoring system that provides real-time system monitoring, threshold-based alerting, auto-scaling capabilities, and extensive metrics collection. It integrates seamlessly with existing systems while providing advanced monitoring features.

## Features

### 🚀 Core Monitoring Capabilities
- **Real-time System Metrics**: CPU, memory, disk, network, and process monitoring
- **Service-level Monitoring**: Track performance of individual services and applications
- **Custom Metrics**: Define and monitor application-specific metrics
- **Historical Data**: Maintain performance history with configurable retention

### ⚠️ Advanced Alerting System
- **Configurable Thresholds**: Set warning and critical thresholds for any metric
- **Multiple Operators**: Support for >, <, >=, <=, ==, != comparisons
- **Action-based Responses**: Log, alert, auto-scale, or restart based on violations
- **Alert History**: Comprehensive tracking of all alerts with severity levels

### 🔄 Auto-scaling Intelligence
- **Smart Scaling**: Automatic resource scaling based on performance metrics
- **Configurable Policies**: Define scaling thresholds and factors
- **Resource Management**: Scale worker processes, memory allocation, and thread pools
- **Load Balancing**: Distribute load across available resources

### 📊 Data Export & Integration
- **Multiple Formats**: Export to JSON, CSV, and Prometheus formats
- **External Systems**: Integration with Prometheus, Grafana, and other monitoring tools
- **API Access**: RESTful API for external system integration
- **Real-time Streaming**: Live metrics streaming for dashboards

### 🏗️ Modular Architecture
- **Plugin System**: Extensible architecture for custom monitoring modules
- **Service Discovery**: Automatic discovery of available services
- **Dependency Management**: Handle complex service dependencies
- **Hot Reloading**: Update configurations without restart

## Quick Start

### Installation

1. **Install Dependencies**:
```bash
pip install -r performance_monitor_requirements.txt
```

2. **Basic Usage**:
```python
from performance_monitor_v3_7 import create_performance_monitor

# Create monitor with default configuration
monitor = create_performance_monitor()

# Start monitoring
monitor.start_monitoring()

# Stop monitoring
monitor.stop_monitoring()
```

### Configuration

The monitor can be configured using YAML, JSON, or Python dictionaries:

```python
config = {
    'monitoring_interval': 5.0,
    'auto_scaling_enabled': True,
    'scaling_thresholds': {
        'cpu_usage': {'scale_up_threshold': 80, 'scale_down_threshold': 20}
    }
}

monitor = create_performance_monitor(config)
```

## Architecture

### Core Components

1. **EnhancedPerformanceMonitor**: Main monitoring class
2. **PerformanceThreshold**: Threshold configuration and evaluation
3. **PerformanceAlert**: Alert generation and management
4. **MetricSeries**: Time-series data storage and analysis

### Integration Points

- **MetricsCollector**: Integrates with existing metrics collection systems
- **HealthMonitor**: Connects with health monitoring systems
- **EventSystem**: Publishes monitoring events for external consumption
- **ConfigManager**: Manages configuration and hot-reloading

## Advanced Usage

### Custom Thresholds

```python
from performance_monitor_v3_7 import PerformanceThreshold

# Create custom threshold
threshold = PerformanceThreshold(
    metric_name="custom_metric",
    warning_threshold=50.0,
    critical_threshold=80.0,
    operator=">",
    enabled=True,
    action="auto_scale"
)

monitor.add_threshold(threshold)
```

### Service Monitoring

```python
# Add monitoring for a custom service
service_metrics = {
    'response_time': {
        'description': 'API response time',
        'unit': 'milliseconds',
        'labels': {'service': 'my_api'}
    },
    'throughput': {
        'description': 'Requests per second',
        'unit': 'req/sec',
        'labels': {'service': 'my_api'}
    }
}

monitor.add_service_monitoring('my_api', service_metrics)

# Record metrics
monitor.record_service_metric('my_api', 'response_time', 150.0)
monitor.record_service_metric('my_api', 'throughput', 100.0)
```

### Auto-scaling Configuration

```python
scaling_config = {
    'cpu_usage': {
        'scale_up_threshold': 80.0,
        'scale_down_threshold': 20.0,
        'scale_up_factor': 1.5,
        'scale_down_factor': 0.7
    }
}

monitor = create_performance_monitor({
    'auto_scaling_enabled': True,
    'scaling_thresholds': scaling_config
})
```

## Configuration Reference

### Monitoring Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `monitoring_interval` | float | 5.0 | Collection interval in seconds |
| `auto_scaling_enabled` | bool | false | Enable auto-scaling |
| `data_retention.history_hours` | int | 24 | Performance history retention |
| `data_retention.alerts_days` | int | 7 | Alert history retention |

### Threshold Configuration

```yaml
thresholds:
  cpu_usage:
    warning_threshold: 70.0
    critical_threshold: 90.0
    operator: ">"
    enabled: true
    action: "alert"
    description: "CPU usage percentage"
```

### Auto-scaling Configuration

```yaml
auto_scaling:
  enabled: true
  thresholds:
    cpu_usage:
      scale_up_threshold: 80.0
      scale_down_threshold: 20.0
      scale_up_factor: 1.5
      scale_down_factor: 0.7
```

## API Reference

### Core Methods

#### `start_monitoring()`
Start the performance monitoring system.

#### `stop_monitoring()`
Stop the performance monitoring system.

#### `add_threshold(threshold: PerformanceThreshold)`
Add a new performance threshold.

#### `remove_threshold(metric_name: str)`
Remove a performance threshold.

#### `add_service_monitoring(service_name: str, metrics: Dict)`
Add monitoring for a specific service.

#### `record_service_metric(service_name: str, metric_name: str, value: float, **kwargs)`
Record a metric value for a service.

#### `get_performance_summary(window_seconds: Optional[float] = None) -> Dict`
Get comprehensive performance summary.

#### `export_metrics(format: str = "json", file_path: Optional[str] = None) -> str`
Export metrics in specified format.

### Data Structures

#### `PerformanceThreshold`
```python
@dataclass
class PerformanceThreshold:
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    operator: str = ">"
    enabled: bool = True
    action: str = "log"
```

#### `PerformanceAlert`
```python
@dataclass
class PerformanceAlert:
    timestamp: float
    threshold_name: str
    status: str
    message: str
    current_value: float
    threshold_value: float
    service_name: Optional[str] = None
    severity: str = "info"
```

## Demo and Examples

### Running the Demo

```bash
cd core
python performance_monitor_demo.py
```

The demo includes:
- **Scenario 1**: Normal operation monitoring
- **Scenario 2**: High load simulation
- **Scenario 3**: Error condition simulation
- **Scenario 4**: Recovery simulation

### Example Integrations

#### FastAPI Integration
```python
from fastapi import FastAPI
from performance_monitor_v3_7 import create_performance_monitor

app = FastAPI()
monitor = create_performance_monitor()

@app.middleware("http")
async def monitor_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    monitor.record_service_metric('fastapi', 'response_time', process_time)
    return response
```

#### Background Task Monitoring
```python
import asyncio
from performance_monitor_v3_7 import create_performance_monitor

monitor = create_performance_monitor()

async def background_task():
    start_time = time.time()
    
    # Perform work
    await asyncio.sleep(5)
    
    # Record metrics
    duration = time.time() - start_time
    monitor.record_service_metric('background', 'task_duration', duration)
```

## Performance Considerations

### Memory Management
- Configurable data retention periods
- Automatic cleanup of old metrics
- Efficient data structures for time-series data

### CPU Optimization
- Asynchronous metric collection
- Configurable collection intervals
- Background processing for heavy operations

### Storage Optimization
- Compressed data storage
- Configurable compression levels
- Efficient serialization formats

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   - Reduce data retention periods
   - Decrease collection frequency
   - Enable data compression

2. **Missing Metrics**
   - Check service monitoring configuration
   - Verify metric names and labels
   - Ensure monitoring is started

3. **Threshold Violations Not Triggering**
   - Verify threshold configuration
   - Check metric data availability
   - Ensure threshold actions are enabled

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.getLogger('performance_monitor_v3_7').setLevel(logging.DEBUG)
```

## Contributing

### Development Setup

1. **Clone the repository**
2. **Install development dependencies**
3. **Run tests**: `pytest test_performance_monitor.py`
4. **Format code**: `black performance_monitor_v3_7.py`

### Adding New Features

1. **Create feature branch**
2. **Implement functionality**
3. **Add tests**
4. **Update documentation**
5. **Submit pull request**

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the demo examples
- Consult the troubleshooting guide

## Roadmap

### Upcoming Features
- **Machine Learning Integration**: Predictive scaling and anomaly detection
- **Cloud Provider Integration**: AWS, Azure, GCP monitoring
- **Advanced Visualization**: Real-time dashboards and charts
- **Distributed Monitoring**: Multi-node monitoring coordination
- **Custom Alert Channels**: Webhook, Slack, Teams integration

### Version History
- **v3.7**: Enhanced modular architecture, auto-scaling, comprehensive monitoring
- **v3.6**: Refactored system with improved performance
- **v3.5**: Initial modular architecture implementation

---

**Enhanced Performance Monitor v3.7** - Professional-grade monitoring for modern applications.
