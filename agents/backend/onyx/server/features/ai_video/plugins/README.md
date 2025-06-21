# AI Video Plugin System

A comprehensive, production-ready plugin system for AI video generation with advanced features, robust error handling, and extensive monitoring capabilities.

## 🚀 Features

- **🔌 Plugin Discovery & Loading**: Automatic discovery and dynamic loading of plugins
- **✅ Validation & Security**: Multi-level validation with security checks
- **🔄 Lifecycle Management**: Complete plugin lifecycle with state management
- **📊 Performance Monitoring**: Real-time metrics and health monitoring
- **🎯 Event Handling**: Comprehensive event system with custom handlers
- **⚙️ Configuration Management**: Flexible configuration with environment variables
- **🔒 Error Recovery**: Robust error handling and automatic recovery
- **📈 Scalability**: Designed for high-performance, concurrent operations

## 📦 Installation

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd ai-video-system

# Install dependencies
pip install -r requirements_plugins.txt

# Run setup
python plugins/setup.py --all

# Run demo
python plugins/demo.py
```

### Manual Installation

1. **Install Dependencies**:
   ```bash
   pip install aiohttp beautifulsoup4 newspaper3k trafilatura pyyaml pydantic
   ```

2. **Create Configuration**:
   ```bash
   python plugins/setup.py --create-config
   ```

3. **Setup Directories**:
   ```bash
   python plugins/setup.py --setup-dirs
   ```

## 🎯 Quick Examples

### Basic Usage

```python
from ai_video.plugins import quick_start

# Start with recommended settings
manager = await quick_start()

# Load a plugin
plugin = await manager.load_plugin("web_extractor", {"timeout": 30})

# Use the plugin
content = await plugin.extract_content("https://example.com")
print(f"Extracted: {len(content.text)} characters")
```

### Advanced Configuration

```python
from ai_video.plugins import PluginManager, ManagerConfig, ValidationLevel

# Create custom configuration
config = ManagerConfig(
    auto_discover=True,
    auto_load=True,
    validation_level=ValidationLevel.STRICT,
    enable_events=True,
    enable_metrics=True,
    plugin_dirs=["./my_plugins", "./extensions"]
)

# Create and start manager
manager = PluginManager(config)
await manager.start()

# Add event handlers
def on_plugin_loaded(plugin_name, plugin):
    print(f"🎉 Plugin loaded: {plugin_name}")

manager.add_event_handler("plugin_loaded", on_plugin_loaded)

# Load plugins
plugins = await manager.load_all_plugins({
    "web_extractor": {"timeout": 30, "max_retries": 3},
    "video_generator": {"quality": "high", "format": "mp4"}
})
```

### Plugin Development

```python
from ai_video.plugins import BasePlugin, PluginMetadata

class MyCustomPlugin(BasePlugin):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "my_custom_plugin"
        self.version = "1.0.0"
        self.description = "My awesome custom plugin"
        self.author = "Your Name"
        self.category = "processor"
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self.name,
            version=self.version,
            description=self.description,
            author=self.author,
            category=self.category,
            dependencies={
                "requests": ">=2.25.0",
                "pandas": ">=1.3.0"
            },
            config_schema={
                "api_key": {"type": "string", "required": True},
                "timeout": {"type": "integer", "default": 30}
            }
        )
    
    def validate_config(self, config: dict) -> bool:
        return "api_key" in config and config.get("timeout", 0) > 0
    
    async def initialize(self):
        # Initialize your plugin
        self.api_key = self.config.get("api_key")
        self.timeout = self.config.get("timeout", 30)
    
    async def process_data(self, data):
        # Your plugin logic here
        return {"processed": data, "timestamp": time.time()}
    
    async def cleanup(self):
        # Cleanup resources
        pass
```

## 📋 API Reference

### PluginManager

The main class for managing plugins.

#### Methods

- `start()` - Start the plugin manager
- `load_plugin(name, config)` - Load a specific plugin
- `load_all_plugins(configs)` - Load all discovered plugins
- `initialize_plugin(name)` - Initialize a plugin
- `start_plugin(name)` - Start a plugin
- `stop_plugin(name)` - Stop a plugin
- `unload_plugin(name)` - Unload a plugin
- `get_plugin(name)` - Get a plugin instance
- `list_plugins(state)` - List plugins by state
- `get_stats()` - Get system statistics
- `get_health_report()` - Get health report
- `shutdown()` - Shutdown the manager

#### Properties

- `config` - Current configuration
- `plugins` - Loaded plugins
- `discovered_plugins` - Discovered plugins

### BasePlugin

Base class for all plugins.

#### Required Methods

- `get_metadata()` - Return plugin metadata
- `initialize()` - Initialize the plugin
- `cleanup()` - Cleanup resources

#### Optional Methods

- `validate_config(config)` - Validate configuration
- `start()` - Start the plugin
- `stop()` - Stop the plugin
- `get_stats()` - Get plugin statistics

### PluginMetadata

Plugin metadata information.

#### Fields

- `name` - Plugin name
- `version` - Plugin version
- `description` - Plugin description
- `author` - Plugin author
- `category` - Plugin category
- `dependencies` - Required dependencies
- `config_schema` - Configuration schema

## ⚙️ Configuration

### Configuration Files

The system supports multiple configuration formats:

**JSON Configuration** (`ai_video_config.json`):
```json
{
  "auto_discover": true,
  "auto_load": false,
  "validation_level": "standard",
  "plugin_dirs": ["./plugins", "./extensions"],
  "http_timeout": 30,
  "max_retries": 3,
  "enable_metrics": true,
  "enable_events": true
}
```

**YAML Configuration** (`ai_video_config.yaml`):
```yaml
auto_discover: true
auto_load: false
validation_level: standard
plugin_dirs:
  - ./plugins
  - ./extensions
http_timeout: 30
max_retries: 3
enable_metrics: true
enable_events: true
```

### Environment Variables

You can also configure the system using environment variables:

```bash
export AI_VIDEO_AUTO_DISCOVER=true
export AI_VIDEO_AUTO_LOAD=false
export AI_VIDEO_VALIDATION_LEVEL=standard
export AI_VIDEO_HTTP_TIMEOUT=30
export AI_VIDEO_MAX_RETRIES=3
export AI_VIDEO_ENABLE_METRICS=true
export AI_VIDEO_ENABLE_EVENTS=true
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `auto_discover` | bool | true | Automatically discover plugins |
| `auto_load` | bool | false | Automatically load discovered plugins |
| `auto_initialize` | bool | false | Automatically initialize loaded plugins |
| `validation_level` | string | "standard" | Validation level (basic/standard/strict/security) |
| `plugin_dirs` | list | ["./plugins", ...] | Directories to search for plugins |
| `http_timeout` | int | 30 | HTTP timeout in seconds |
| `max_retries` | int | 3 | Maximum retry attempts |
| `enable_metrics` | bool | true | Enable performance metrics |
| `enable_events` | bool | true | Enable event handling |
| `enable_logging` | bool | true | Enable logging |
| `log_level` | string | "INFO" | Logging level |

## 🔧 Development

### Creating a Plugin

1. **Create Plugin File**:
   ```python
   # my_plugin.py
   from ai_video.plugins import BasePlugin, PluginMetadata
   
   class MyPlugin(BasePlugin):
       def __init__(self, config=None):
           super().__init__(config)
           self.name = "my_plugin"
           self.version = "1.0.0"
           self.description = "My custom plugin"
           self.author = "Your Name"
           self.category = "processor"
       
       def get_metadata(self) -> PluginMetadata:
           return PluginMetadata(
               name=self.name,
               version=self.version,
               description=self.description,
               author=self.author,
               category=self.category
           )
       
       async def initialize(self):
           # Initialize your plugin
           pass
       
       async def cleanup(self):
           # Cleanup resources
           pass
   ```

2. **Place in Plugin Directory**:
   ```bash
   cp my_plugin.py ./plugins/
   ```

3. **Load and Use**:
   ```python
   from ai_video.plugins import quick_start
   
   manager = await quick_start()
   plugin = await manager.load_plugin("my_plugin")
   ```

### Testing

Run the test suite:

```bash
# Run all tests
python plugins/test_system.py --all

# Run specific test types
python plugins/test_system.py --unit
python plugins/test_system.py --integration
python plugins/test_system.py --performance

# Verbose output
python plugins/test_system.py --all --verbose
```

### Validation Levels

- **Basic**: Minimal validation, fast loading
- **Standard**: Normal validation with security checks
- **Strict**: Comprehensive validation with performance checks
- **Security**: Maximum security validation

## 📊 Monitoring

### Statistics

Get system statistics:

```python
stats = manager.get_stats()
print(f"Total plugins: {stats['total_plugins']}")
print(f"Loaded plugins: {stats['loaded_plugins']}")
print(f"Success rate: {stats['success_rate']:.1%}")
```

### Health Monitoring

Get health report:

```python
health = manager.get_health_report()
print(f"Overall status: {health['overall_status']}")
print(f"Healthy plugins: {health['healthy_plugins']}")
print(f"Unhealthy plugins: {health['unhealthy_plugins']}")
```

### Event Handling

Subscribe to events:

```python
def on_plugin_loaded(plugin_name, plugin):
    print(f"Plugin loaded: {plugin_name}")

def on_plugin_error(plugin_name, error):
    print(f"Plugin error: {plugin_name} - {error}")

manager.add_event_handler("plugin_loaded", on_plugin_loaded)
manager.add_event_handler("plugin_error", on_plugin_error)
```

## 🚨 Error Handling

The system provides comprehensive error handling:

```python
try:
    plugin = await manager.load_plugin("my_plugin")
except PluginError as e:
    print(f"Plugin error: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
except DependencyError as e:
    print(f"Dependency error: {e}")
```

## 🔒 Security

The plugin system includes several security features:

- **Plugin Validation**: All plugins are validated before loading
- **Configuration Validation**: Configuration is validated against schemas
- **Security Checks**: Security validation for potentially dangerous operations
- **Sandboxing**: Plugins run in isolated environments
- **Access Control**: Configurable access permissions

## 📈 Performance

### Optimization Tips

1. **Use Connection Pooling**: Reuse HTTP connections
2. **Enable Caching**: Use built-in caching for repeated operations
3. **Concurrent Loading**: Load multiple plugins concurrently
4. **Lazy Initialization**: Initialize plugins only when needed
5. **Resource Management**: Properly cleanup resources

### Performance Monitoring

```python
# Get performance metrics
stats = manager.get_stats()
print(f"Average load time: {stats['avg_load_time']:.2f}s")
print(f"Total load time: {stats['total_load_time']:.2f}s")

# Get plugin-specific metrics
plugin = manager.get_plugin("my_plugin")
if hasattr(plugin, 'get_stats'):
    plugin_stats = plugin.get_stats()
    print(f"Plugin performance: {plugin_stats}")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your plugin or improvements
4. Add tests
5. Submit a pull request

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd ai-video-system

# Install development dependencies
pip install -r requirements_plugins.txt

# Run tests
python plugins/test_system.py --all

# Run linting
flake8 plugins/
black plugins/
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: See the examples and API reference
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join community discussions
- **Email**: Contact the development team

## 🔄 Changelog

### Version 1.0.0
- Initial release
- Complete plugin system
- Advanced configuration management
- Comprehensive testing suite
- Performance monitoring
- Security validation

---

**Made with ❤️ by the AI Video Team** 