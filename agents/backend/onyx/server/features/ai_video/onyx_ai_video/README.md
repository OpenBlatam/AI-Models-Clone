# Onyx AI Video System

A comprehensive, modular AI video generation system fully integrated with Onyx infrastructure. This system provides enterprise-grade video generation capabilities with plugin architecture, workflow orchestration, and seamless Onyx integration.

## 🚀 Features

- **Modular Architecture**: Clean, extensible design with separate modules for core functionality, workflows, plugins, and utilities
- **Onyx Integration**: Full integration with Onyx's LLM, logging, threading, security, and performance utilities
- **Plugin System**: Extensible plugin architecture for custom video processing capabilities
- **Workflow Orchestration**: Sophisticated workflow management for complex video generation pipelines
- **Performance Monitoring**: Real-time performance tracking and optimization
- **Security Framework**: Comprehensive security with encryption, access control, and input validation
- **Configuration Management**: Flexible configuration system with environment variables and config files
- **CLI Interface**: Full command-line interface for system management and video generation
- **API Integration**: RESTful API endpoints for programmatic access
- **Error Handling**: Robust error handling with custom exceptions and recovery mechanisms

## 📁 Project Structure

```
onyx_ai_video/
├── core/                    # Core system components
│   ├── integration.py      # Onyx integration manager
│   ├── exceptions.py       # Custom exceptions
│   └── models.py          # Data models
├── workflows/              # Video generation workflows
│   ├── video_workflow.py   # Main video workflow
│   └── workflow_manager.py # Workflow orchestration
├── plugins/                # Plugin system
│   ├── plugin_manager.py   # Plugin management
│   └── plugin_base.py      # Plugin base classes
├── config/                 # Configuration management
│   ├── config_manager.py   # Configuration manager
│   └── settings.py         # Onyx-specific settings
├── utils/                  # Utility modules
│   ├── logger.py          # Logging utilities
│   ├── performance.py     # Performance monitoring
│   └── security.py        # Security utilities
├── api/                   # API endpoints
│   ├── main.py           # Main API system
│   └── endpoints.py      # REST endpoints
├── cli/                   # Command-line interface
│   └── main.py           # CLI implementation
├── examples/              # Usage examples
│   └── basic_usage.py    # Basic usage examples
├── docs/                  # Documentation
├── tests/                 # Test suite
└── __init__.py           # Main package
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Onyx system installed and configured
- Required dependencies (see requirements.txt)

### Quick Start

1. **Clone the repository**:
   ```bash
   cd agents/backend/onyx/server/features/ai_video
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the system**:
   ```bash
   python -m onyx_ai_video.cli.main init
   ```

4. **Generate your first video**:
   ```bash
   python -m onyx_ai_video.cli.main generate --input "Create a video about AI" --user-id user123
   ```

## 📖 Usage

### Basic Usage

```python
import asyncio
from onyx_ai_video import OnyxAIVideoSystem, VideoRequest, VideoQuality

async def generate_video():
    # Initialize system
    system = OnyxAIVideoSystem()
    await system.initialize()
    
    # Create request
    request = VideoRequest(
        input_text="Create a video about artificial intelligence",
        user_id="user123",
        quality=VideoQuality.HIGH,
        duration=60
    )
    
    # Generate video
    response = await system.generate_video(request)
    
    print(f"Video generated: {response.output_url}")
    
    # Shutdown
    await system.shutdown()

asyncio.run(generate_video())
```

### CLI Usage

```bash
# Initialize system
python -m onyx_ai_video.cli.main init

# Generate video
python -m onyx_ai_video.cli.main generate --input "Create a video about AI" --user-id user123

# Check system status
python -m onyx_ai_video.cli.main status

# Monitor performance
python -m onyx_ai_video.cli.main monitor --interval 10

# List plugins
python -m onyx_ai_video.cli.main plugins list

# Manage configuration
python -m onyx_ai_video.cli.main config show
```

### API Usage

```python
from onyx_ai_video.api.main import get_system, generate_video
from onyx_ai_video.core.models import VideoRequest

async def api_example():
    # Get system instance
    system = await get_system()
    
    # Generate video
    request = VideoRequest(
        input_text="Create a video about machine learning",
        user_id="api_user"
    )
    
    response = await generate_video(request)
    return response
```

## 🔧 Configuration

### Environment Variables

```bash
# System configuration
AI_VIDEO_ENVIRONMENT=production
AI_VIDEO_DEBUG=false

# Logging
AI_VIDEO_LOGGING_LEVEL=INFO
AI_VIDEO_LOGGING_FILE_PATH=./logs/ai_video.log

# LLM configuration
AI_VIDEO_LLM_PROVIDER=openai
AI_VIDEO_LLM_MODEL=gpt-4
AI_VIDEO_LLM_TEMPERATURE=0.7

# Video configuration
AI_VIDEO_OUTPUT_DIRECTORY=./output
AI_VIDEO_TEMP_DIRECTORY=./temp

# Plugin configuration
AI_VIDEO_PLUGINS_DIRECTORY=./plugins
AI_VIDEO_MAX_WORKERS=10

# Performance configuration
AI_VIDEO_CACHE_ENABLED=true
AI_VIDEO_CACHE_SIZE=1000

# Security configuration
AI_VIDEO_ENCRYPTION_KEY=your-secret-key
AI_VIDEO_RATE_LIMIT_REQUESTS=100

# Onyx integration
ONYX_USE_LOGGING=true
ONYX_USE_LLM=true
ONYX_USE_TELEMETRY=true
ONYX_USE_ENCRYPTION=true
ONYX_USE_THREADING=true
ONYX_USE_RETRY=true
ONYX_USE_GPU=true
```

### Configuration File

Create a `config.yaml` file:

```yaml
system_name: "Onyx AI Video System"
version: "1.0.0"
environment: "production"
debug: false

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_path: "./logs/ai_video.log"
  max_size: 10
  backup_count: 5
  use_onyx_logging: true

llm:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 4000
  timeout: 60
  retry_attempts: 3
  use_onyx_llm: true

video:
  default_quality: "medium"
  default_format: "mp4"
  default_duration: 60
  max_duration: 600
  output_directory: "./output"
  temp_directory: "./temp"
  cleanup_temp: true

plugins:
  plugins_directory: "./plugins"
  auto_load: true
  enable_all: false
  max_workers: 10
  timeout: 300
  retry_attempts: 3

performance:
  enable_monitoring: true
  metrics_interval: 60
  cache_enabled: true
  cache_size: 1000
  cache_ttl: 3600
  gpu_enabled: true
  max_concurrent_requests: 10

security:
  enable_encryption: true
  encryption_key: null  # Set via environment variable
  validate_input: true
  max_input_length: 10000
  rate_limit_enabled: true
  rate_limit_requests: 100
  use_onyx_security: true

onyx:
  use_onyx_logging: true
  use_onyx_llm: true
  use_onyx_telemetry: true
  use_onyx_encryption: true
  use_onyx_threading: true
  use_onyx_retry: true
  use_onyx_gpu: true
  onyx_config_path: null
```

## 🔌 Plugin Development

### Creating a Plugin

```python
from onyx_ai_video.plugins.plugin_base import OnyxPluginBase, OnyxPluginContext

class MyCustomPlugin(OnyxPluginBase):
    def __init__(self):
        super().__init__(
            name="my_custom_plugin",
            version="1.0.0",
            description="A custom video processing plugin",
            author="Your Name",
            category="custom"
        )
    
    async def execute(self, context: OnyxPluginContext) -> dict:
        """Execute the plugin."""
        input_data = context.input_data
        
        # Your custom processing logic here
        processed_data = self._process_data(input_data)
        
        return {
            "status": "success",
            "processed_data": processed_data,
            "metadata": {
                "processing_time": 1.5,
                "custom_field": "value"
            }
        }
    
    def _process_data(self, data: dict) -> dict:
        """Process input data."""
        # Your processing logic
        return data
```

### Plugin Configuration

```yaml
# plugins/my_plugin/config.yaml
name: "my_custom_plugin"
version: "1.0.0"
enabled: true
parameters:
  custom_param: "value"
  timeout: 30
timeout: 60
max_workers: 2
dependencies: []
conflicts: []
gpu_required: false
memory_required: 512
cpu_cores_required: 1
```

## 📊 Monitoring and Metrics

### Performance Monitoring

```python
from onyx_ai_video.utils.performance import get_performance_monitor

# Get performance metrics
monitor = get_performance_monitor()
metrics = monitor.get_performance_summary()

print(f"CPU Usage: {metrics['system_metrics']['cpu_percent']}%")
print(f"Memory Usage: {metrics['system_metrics']['memory_percent']}%")
print(f"Active Operations: {metrics['active_operations']}")
```

### System Status

```python
from onyx_ai_video.api.main import get_system_status

status = await get_system_status()
print(f"System Status: {status.status}")
print(f"Uptime: {status.uptime} seconds")
print(f"Error Rate: {status.error_rate}%")
```

## 🔒 Security

### Access Control

```python
from onyx_ai_video.utils.security import validate_access, grant_access

# Validate user access
has_access = validate_access("user123", "resource456", ["read", "write"])

# Grant access
token = grant_access("user123", "resource456", ["read"], expires_at=datetime.now() + timedelta(hours=1))
```

### Input Validation

```python
from onyx_ai_video.utils.security import validate_input

is_valid, result = validate_input("User input text", max_length=1000)
if not is_valid:
    print(f"Validation failed: {result}")
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/performance/

# Run with coverage
python -m pytest --cov=onyx_ai_video tests/
```

### Test Examples

```python
import pytest
from onyx_ai_video import OnyxAIVideoSystem, VideoRequest

@pytest.mark.asyncio
async def test_video_generation():
    system = OnyxAIVideoSystem()
    await system.initialize()
    
    request = VideoRequest(
        input_text="Test video generation",
        user_id="test_user"
    )
    
    response = await system.generate_video(request)
    
    assert response.status == "completed"
    assert response.request_id == request.request_id
    
    await system.shutdown()
```

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**:
   ```bash
   export AI_VIDEO_ENVIRONMENT=production
   export AI_VIDEO_ENCRYPTION_KEY=your-secret-key
   export ONYX_ROOT=/path/to/onyx
   ```

2. **System Initialization**:
   ```bash
   python -m onyx_ai_video.cli.main init --config production_config.yaml
   ```

3. **Service Management**:
   ```bash
   # Start system
   python -m onyx_ai_video.cli.main start
   
   # Monitor system
   python -m onyx_ai_video.cli.main monitor
   
   # Shutdown system
   python -m onyx_ai_video.cli.main shutdown
   ```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY onyx_ai_video/ ./onyx_ai_video/

EXPOSE 8000

CMD ["python", "-m", "onyx_ai_video.cli.main", "start"]
```

## 📚 Documentation

- [System Overview](docs/SYSTEM_OVERVIEW.md)
- [API Reference](docs/API_REFERENCE.md)
- [Plugin Development Guide](docs/PLUGIN_DEVELOPMENT.md)
- [Configuration Guide](docs/CONFIGURATION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Added plugin system and performance monitoring
- **v1.2.0**: Enhanced Onyx integration and security features

---

**Onyx AI Video System** - Enterprise-grade AI video generation with Onyx integration. 