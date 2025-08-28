"""
Advanced Configuration System for Modular SEO System
Provides configuration management with validation, hot-reload, and multiple backends
"""

import asyncio
import json
import logging
import os
import re
import time
import yaml
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union
from typing_extensions import Protocol
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logger = logging.getLogger(__name__)


class ConfigBackend(Enum):
    """Configuration backend types."""

    MEMORY = "memory"
    FILE = "file"
    ENVIRONMENT = "environment"
    DATABASE = "database"
    REMOTE = "remote"


class ConfigValidationLevel(Enum):
    """Configuration validation levels."""

    NONE = "none"
    BASIC = "basic"
    STRICT = "strict"
    CUSTOM = "custom"


@dataclass
class ConfigSchema:
    """Schema for configuration validation."""

    properties: Dict[str, Any] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)
    type: str = "object"
    additional_properties: bool = True
    pattern_properties: Dict[str, Any] = field(default_factory=dict)
    dependencies: Dict[str, Any] = field(default_factory=dict)
    custom_validators: Dict[str, Callable] = field(default_factory=dict)


@dataclass
class ConfigValue:
    """Configuration value with metadata."""

    value: Any
    source: str
    timestamp: float
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_status: bool = True
    validation_errors: List[str] = field(default_factory=list)


class ConfigValidator(Protocol):
    """Protocol for configuration validators."""

    def validate(self, config: Dict[str, Any], schema: ConfigSchema) -> tuple[bool, List[str]]:
        """Validate configuration against schema."""
        ...


class ConfigBackendProtocol(Protocol):
    """Protocol for configuration backends."""

    async def load(self) -> Dict[str, Any]:
        """Load configuration from backend."""
        ...

    async def save(self, config: Dict[str, Any]) -> bool:
        """Save configuration to backend."""
        ...

    async def watch(self, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """Watch for configuration changes."""
        ...

    async def stop_watching(self) -> bool:
        """Stop watching for configuration changes."""
        ...


class BaseConfigBackend(ABC):
    """Base class for configuration backends."""

    def __init__(self, name: str):
        self.name = name
        self.is_watching = False
        self._callbacks: List[Callable] = []

    @abstractmethod
    async def load(self) -> Dict[str, Any]:
        """Load configuration from backend."""
        pass

    @abstractmethod
    async def save(self, config: Dict[str, Any]) -> bool:
        """Save configuration to backend."""
        pass

    async def watch(self, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """Watch for configuration changes."""
        self._callbacks.append(callback)
        self.is_watching = True
        return True

    async def stop_watching(self) -> bool:
        """Stop watching for configuration changes."""
        self._callbacks.clear()
        self.is_watching = False
        return True

    async def _notify_callbacks(self, config: Dict[str, Any]):
        """Notify all registered callbacks of configuration changes."""
        for callback in self._callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(config)
                else:
                    callback(config)
            except Exception as e:
                logger.error(f"Error in configuration callback: {e}")


class MemoryConfigBackend(BaseConfigBackend):
    """In-memory configuration backend."""

    def __init__(self, name: str = "memory"):
        super().__init__(name)
        self._config: Dict[str, Any] = {}

    async def load(self) -> Dict[str, Any]:
        """Load configuration from memory."""
        return self._config.copy()

    async def save(self, config: Dict[str, Any]) -> bool:
        """Save configuration to memory."""
        try:
            self._config = config.copy()
            await self._notify_callbacks(self._config)
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration to memory: {e}")
            return False


class FileConfigBackend(BaseConfigBackend):
    """File-based configuration backend."""

    def __init__(self, file_path: str, file_format: str = "yaml"):
        super().__init__(f"file_{Path(file_path).stem}")
        self.file_path = Path(file_path)
        self.file_format = file_format.lower()
        self._observer: Optional[Observer] = None
        self._event_handler: Optional[FileConfigEventHandler] = None

    async def load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            if not self.file_path.exists():
                logger.warning(f"Configuration file {self.file_path} does not exist")
                return {}

            with open(self.file_path, "r", encoding="utf-8") as f:
                if self.file_format == "yaml":
                    config = yaml.safe_load(f)
                elif self.file_format == "json":
                    config = json.load(f)
                else:
                    raise ValueError(f"Unsupported file format: {self.file_format}")

                return config or {}

        except Exception as e:
            logger.error(f"Failed to load configuration from {self.file_path}: {e}")
            return {}

    async def save(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file."""
        try:
            # Ensure directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.file_path, "w", encoding="utf-8") as f:
                if self.file_format == "yaml":
                    yaml.dump(config, f, default_flow_style=False, indent=2)
                elif self.file_format == "json":
                    json.dump(config, f, indent=2, ensure_ascii=False)
                else:
                    raise ValueError(f"Unsupported file format: {self.file_format}")

            return True

        except Exception as e:
            logger.error(f"Failed to save configuration to {self.file_path}: {e}")
            return False

    async def watch(self, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """Watch for file changes."""
        if self.is_watching:
            return await super().watch(callback)

        try:
            self._event_handler = FileConfigEventHandler(self, callback)
            self._observer = Observer()
            self._observer.schedule(self._event_handler, str(self.file_path.parent), recursive=False)
            self._observer.start()

            return await super().watch(callback)

        except Exception as e:
            logger.error(f"Failed to start file watching: {e}")
            return False

    async def stop_watching(self) -> bool:
        """Stop watching for file changes."""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None

        if self._event_handler:
            self._event_handler = None

        return await super().stop_watching()


class FileConfigEventHandler(FileSystemEventHandler):
    """Event handler for file configuration changes."""

    def __init__(self, backend: FileConfigBackend, callback: Callable):
        self.backend = backend
        self.callback = callback
        self.last_modified = 0

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory or event.src_path != str(self.backend.file_path):
            return

        # Debounce rapid file changes
        current_time = time.time()
        if current_time - self.last_modified < 0.1:
            return

        self.last_modified = current_time

        # Load and notify
        asyncio.create_task(self._handle_config_change())

    async def _handle_config_change(self):
        """Handle configuration change."""
        try:
            config = await self.backend.load()
            await self.backend._notify_callbacks(config)
        except Exception as e:
            logger.error(f"Error handling configuration change: {e}")


class EnvironmentConfigBackend(BaseConfigBackend):
    """Environment variable configuration backend."""

    def __init__(self, name: str = "environment", prefix: str = "SEO_"):
        super().__init__(name)
        self.prefix = prefix

    async def load(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}

        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                config_key = key[len(self.prefix) :].lower()
                config[config_key] = self._parse_value(value)

        return config

    async def save(self, config: Dict[str, Any]) -> bool:
        """Environment variables cannot be saved to."""
        logger.warning("Cannot save configuration to environment variables")
        return False

    def _parse_value(self, value: str) -> Any:
        """Parse environment variable value."""
        # Try to parse as different types
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        elif value.isdigit():
            return int(value)
        elif value.replace(".", "").isdigit() and value.count(".") == 1:
            return float(value)
        else:
            return value


class ConfigurationManager:
    """Main configuration manager."""

    def __init__(
        self,
        validation_level: ConfigValidationLevel = ConfigValidationLevel.BASIC,
        default_config: Optional[Dict[str, Any]] = None,
    ):
        self.validation_level = validation_level
        self.default_config = default_config or {}
        self.backends: Dict[str, BaseConfigBackend] = {}
        self.schemas: Dict[str, ConfigSchema] = {}
        self.validators: Dict[str, ConfigValidator] = {}
        self._config_cache: Dict[str, ConfigValue] = {}
        self._lock = asyncio.Lock()
        self._change_callbacks: List[Callable] = []

        # Configuration change tracking
        self._last_change = time.time()
        self._change_count = 0

        # Performance metrics
        self._load_times: List[float] = []
        self._validation_times: List[float] = []

    def add_backend(self, backend: BaseConfigBackend) -> bool:
        """Add a configuration backend."""
        try:
            self.backends[backend.name] = backend
            logger.info(f"Added configuration backend: {backend.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add configuration backend {backend.name}: {e}")
            return False

    def remove_backend(self, backend_name: str) -> bool:
        """Remove a configuration backend."""
        if backend_name in self.backends:
            backend = self.backends[backend_name]
            asyncio.create_task(backend.stop_watching())
            del self.backends[backend_name]
            logger.info(f"Removed configuration backend: {backend_name}")
            return True
        return False

    def add_schema(self, name: str, schema: ConfigSchema) -> bool:
        """Add a configuration schema."""
        try:
            self.schemas[name] = schema
            logger.info(f"Added configuration schema: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add configuration schema {name}: {e}")
            return False

    def add_validator(self, name: str, validator: ConfigValidator) -> bool:
        """Add a configuration validator."""
        try:
            self.validators[name] = validator
            logger.info(f"Added configuration validator: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add configuration validator {name}: {e}")
            return False

    async def load_config(self, backend_name: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from backends."""
        start_time = time.time()

        async with self._lock:
            try:
                config = self.default_config.copy()

                # Load from specified backend or all backends
                backends_to_load = [backend_name] if backend_name else list(self.backends.keys())

                for name in backends_to_load:
                    if name in self.backends:
                        backend_config = await self.backends[name].load()
                        config.update(backend_config)

                        # Cache the configuration
                        self._config_cache[name] = ConfigValue(value=backend_config, source=name, timestamp=time.time())

                # Validate configuration
                if self.validation_level != ConfigValidationLevel.NONE:
                    config = await self._validate_config(config)

                # Update metrics
                load_time = time.time() - start_time
                self._load_times.append(load_time)
                if len(self._load_times) > 100:
                    self._load_times.pop(0)

                logger.debug(f"Configuration loaded in {load_time:.4f}s")
                return config

            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
                return self.default_config.copy()

    async def save_config(self, config: Dict[str, Any], backend_name: Optional[str] = None) -> bool:
        """Save configuration to backends."""
        try:
            # Validate configuration before saving
            if self.validation_level != ConfigValidationLevel.NONE:
                config = await self._validate_config(config)

            # Save to specified backend or all backends
            backends_to_save = [backend_name] if backend_name else list(self.backends.keys())

            success = True
            for name in backends_to_save:
                if name in self.backends:
                    if not await self.backends[name].save(config):
                        success = False

            if success:
                # Update cache
                for name in backends_to_save:
                    if name in self.backends:
                        self._config_cache[name] = ConfigValue(value=config, source=name, timestamp=time.time())

                # Notify change callbacks
                await self._notify_change_callbacks(config)

                self._change_count += 1
                self._last_change = time.time()

            return success

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False

    async def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        config = await self.load_config()
        return config.get(key, default)

    async def set_config(self, key: str, value: Any) -> bool:
        """Set a configuration value."""
        config = await self.load_config()
        config[key] = value
        return await self.save_config(config)

    async def watch_config(self, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """Watch for configuration changes."""
        self._change_callbacks.append(callback)

        # Start watching all backends
        for backend in self.backends.values():
            await backend.watch(callback)

        return True

    async def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration against schemas."""
        start_time = time.time()

        try:
            # Apply all schemas
            for schema_name, schema in self.schemas.items():
                if schema_name in self.validators:
                    validator = self.validators[schema_name]
                    is_valid, errors = validator.validate(config, schema)

                    if not is_valid:
                        logger.warning(f"Configuration validation failed for schema {schema_name}: {errors}")
                        # Continue with validation but log warnings

                # Basic validation
                if not self._basic_validation(config, schema):
                    logger.warning(f"Basic validation failed for schema {schema_name}")

            # Update metrics
            validation_time = time.time() - start_time
            self._validation_times.append(validation_time)
            if len(self._validation_times) > 100:
                self._validation_times.pop(0)

            return config

        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return config

    def _basic_validation(self, config: Dict[str, Any], schema: ConfigSchema) -> bool:
        """Perform basic configuration validation."""
        try:
            # Check required fields
            for required_field in schema.required:
                if required_field not in config:
                    logger.warning(f"Required configuration field missing: {required_field}")
                    return False

            # Check type constraints
            for field_name, field_schema in schema.properties.items():
                if field_name in config:
                    if not self._validate_field_type(config[field_name], field_schema):
                        logger.warning(f"Field {field_name} type validation failed")
                        return False

            return True

        except Exception as e:
            logger.error(f"Basic validation error: {e}")
            return False

    def _validate_field_type(self, value: Any, field_schema: Dict[str, Any]) -> bool:
        """Validate a field's type."""
        expected_type = field_schema.get("type")
        if not expected_type:
            return True

        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "integer":
            return isinstance(value, int)
        elif expected_type == "number":
            return isinstance(value, (int, float))
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "array":
            return isinstance(value, list)
        elif expected_type == "object":
            return isinstance(value, dict)

        return True

    async def _notify_change_callbacks(self, config: Dict[str, Any]):
        """Notify all registered change callbacks."""
        for callback in self._change_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(config)
                else:
                    callback(config)
            except Exception as e:
                logger.error(f"Error in configuration change callback: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get configuration manager statistics."""
        return {
            "backends": list(self.backends.keys()),
            "schemas": list(self.schemas.keys()),
            "validators": list(self.validators.keys()),
            "change_count": self._change_count,
            "last_change": self._last_change,
            "cache_size": len(self._config_cache),
            "avg_load_time": sum(self._load_times) / len(self._load_times) if self._load_times else 0,
            "avg_validation_time": sum(self._validation_times) / len(self._validation_times)
            if self._validation_times
            else 0,
            "validation_level": self.validation_level.value,
        }

    async def reload_config(self) -> Dict[str, Any]:
        """Reload configuration from all backends."""
        # Clear cache
        self._config_cache.clear()

        # Reload
        return await self.load_config()

    async def export_config(self, format: str = "yaml") -> str:
        """Export configuration to string format."""
        config = await self.load_config()

        if format.lower() == "yaml":
            return yaml.dump(config, default_flow_style=False, indent=2)
        elif format.lower() == "json":
            return json.dumps(config, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global configuration manager instance
config_manager = ConfigurationManager()


# Convenience functions
async def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value using global manager."""
    return await config_manager.get_config(key, default)


async def set_config(key: str, value: Any) -> bool:
    """Set configuration value using global manager."""
    return await config_manager.set_config(key, value)


async def load_config() -> Dict[str, Any]:
    """Load configuration using global manager."""
    return await config_manager.load_config()


def add_config_backend(backend: BaseConfigBackend) -> bool:
    """Add configuration backend to global manager."""
    return config_manager.add_backend(backend)


def add_config_schema(name: str, schema: ConfigSchema) -> bool:
    """Add configuration schema to global manager."""
    return config_manager.add_schema(name, schema)
