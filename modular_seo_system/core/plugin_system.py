"""
Plugin System for Modular SEO System
Provides dynamic plugin loading, management, and lifecycle control
"""

import asyncio
import importlib
import inspect
import json
import logging
import os
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union
from typing_extensions import Protocol

from .interfaces import BaseComponent

# Configure logging
logger = logging.getLogger(__name__)


class PluginProtocol(Protocol):
    """Protocol that all plugins must implement."""

    name: str
    version: str
    description: str

    async def initialize(self) -> bool:
        """Initialize the plugin."""
        ...

    async def shutdown(self) -> bool:
        """Shutdown the plugin."""
        ...

    async def health_check(self) -> bool:
        """Check plugin health."""
        ...

    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata."""
        ...


@dataclass
class PluginInfo:
    """Information about a plugin."""

    name: str
    version: str
    description: str
    author: str = ""
    license: str = ""
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    loaded: bool = False
    error_count: int = 0
    last_error: Optional[str] = None
    load_time: Optional[float] = None
    last_health_check: Optional[float] = None


class PluginManager:
    """Manages plugin loading, lifecycle, and dependencies."""

    def __init__(self, plugin_directories: Optional[List[str]] = None):
        self.plugin_directories = plugin_directories or ["plugins"]
        self.plugins: Dict[str, PluginProtocol] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        self.plugin_dependencies: Dict[str, Set[str]] = {}
        self.plugin_dependents: Dict[str, Set[str]] = {}
        self.loaded_modules: Set[str] = set()
        self._lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()

        # Plugin lifecycle hooks
        self.pre_load_hooks: List[callable] = []
        self.post_load_hooks: List[callable] = []
        self.pre_unload_hooks: List[callable] = []
        self.post_unload_hooks: List[callable] = []

    async def discover_plugins(self) -> List[PluginInfo]:
        """Discover available plugins in plugin directories."""
        discovered_plugins = []

        for plugin_dir in self.plugin_directories:
            plugin_path = Path(plugin_dir)
            if not plugin_path.exists():
                continue

            for item in plugin_path.iterdir():
                if item.is_dir() and (item / "__init__.py").exists():
                    plugin_info = await self._inspect_plugin_directory(item)
                    if plugin_info:
                        discovered_plugins.append(plugin_info)

        return discovered_plugins

    async def _inspect_plugin_directory(self, plugin_path: Path) -> Optional[PluginInfo]:
        """Inspect a plugin directory for plugin information."""
        try:
            # Check for plugin.json
            plugin_json = plugin_path / "plugin.json"
            if plugin_json.exists():
                with open(plugin_json, "r") as f:
                    metadata = json.load(f)
                    return PluginInfo(**metadata)

            # Check for __init__.py
            init_file = plugin_path / "__init__.py"
            if init_file.exists():
                # Try to import and inspect
                module_name = str(plugin_path.relative_to(Path.cwd())).replace(os.sep, ".")
                try:
                    module = importlib.import_module(module_name)
                    return await self._extract_plugin_info_from_module(module, plugin_path.name)
                except ImportError:
                    pass

            return None

        except Exception as e:
            logger.warning(f"Failed to inspect plugin directory {plugin_path}: {e}")
            return None

    async def _extract_plugin_info_from_module(self, module: Any, plugin_name: str) -> Optional[PluginInfo]:
        """Extract plugin information from a module."""
        try:
            # Look for plugin classes
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BaseComponent) and obj != BaseComponent:
                    # Check if it has required attributes
                    if hasattr(obj, "name") and hasattr(obj, "version"):
                        return PluginInfo(
                            name=getattr(obj, "name", plugin_name),
                            version=getattr(obj, "version", "1.0.0"),
                            description=getattr(obj, "__doc__", f"Plugin {plugin_name}"),
                            author=getattr(obj, "author", ""),
                            license=getattr(obj, "license", ""),
                            dependencies=getattr(obj, "dependencies", []),
                            tags=getattr(obj, "tags", []),
                        )

            return None

        except Exception as e:
            logger.warning(f"Failed to extract plugin info from module: {e}")
            return None

    async def load_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Load a specific plugin."""
        async with self._lock:
            try:
                # Check if plugin is already loaded
                if plugin_name in self.plugins:
                    logger.warning(f"Plugin {plugin_name} is already loaded")
                    return True

                # Find plugin in directories
                plugin_info = await self._find_plugin_info(plugin_name)
                if not plugin_info:
                    logger.error(f"Plugin {plugin_name} not found")
                    return False

                # Check dependencies
                if not await self._check_dependencies(plugin_info):
                    logger.error(f"Plugin {plugin_name} dependencies not met")
                    return False

                # Run pre-load hooks
                await self._run_hooks(self.pre_load_hooks, plugin_info)

                # Load the plugin
                plugin = await self._load_plugin_instance(plugin_info, config)
                if not plugin:
                    return False

                # Initialize plugin
                if not await plugin.initialize():
                    logger.error(f"Failed to initialize plugin {plugin_name}")
                    return False

                # Store plugin and info
                self.plugins[plugin_name] = plugin
                self.plugin_info[plugin_name] = plugin_info
                plugin_info.loaded = True
                plugin_info.load_time = time.time()

                # Update dependency tracking
                self._update_dependency_tracking(plugin_info)

                # Run post-load hooks
                await self._run_hooks(self.post_load_hooks, plugin_info)

                logger.info(f"Plugin {plugin_name} loaded successfully")
                return True

            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_name}: {e}")
                if plugin_name in self.plugin_info:
                    self.plugin_info[plugin_name].error_count += 1
                    self.plugin_info[plugin_name].last_error = str(e)
                return False

    async def _find_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Find plugin information by name."""
        discovered_plugins = await self.discover_plugins()
        for plugin_info in discovered_plugins:
            if plugin_info.name == plugin_name:
                return plugin_info
        return None

    async def _check_dependencies(self, plugin_info: PluginInfo) -> bool:
        """Check if plugin dependencies are met."""
        for dep in plugin_info.dependencies:
            if dep not in self.plugins:
                logger.warning(f"Plugin {plugin_info.name} depends on {dep} which is not loaded")
                return False
        return True

    async def _load_plugin_instance(
        self, plugin_info: PluginInfo, config: Optional[Dict[str, Any]]
    ) -> Optional[PluginProtocol]:
        """Load plugin instance from module."""
        try:
            # Find the plugin module
            for plugin_dir in self.plugin_directories:
                plugin_path = Path(plugin_dir) / plugin_info.name
                if plugin_path.exists() and (plugin_path / "__init__.py").exists():
                    module_name = str(plugin_path.relative_to(Path.cwd())).replace(os.sep, ".")

                    # Import module
                    module = importlib.import_module(module_name)
                    self.loaded_modules.add(module_name)

                    # Find plugin class
                    for name, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, BaseComponent)
                            and obj != BaseComponent
                            and getattr(obj, "name", "") == plugin_info.name
                        ):
                            # Create instance with config
                            if config:
                                plugin = obj(**config)
                            else:
                                plugin = obj()

                            return plugin

            logger.error(f"Could not find plugin class for {plugin_info.name}")
            return None

        except Exception as e:
            logger.error(f"Failed to load plugin instance for {plugin_info.name}: {e}")
            return None

    def _update_dependency_tracking(self, plugin_info: PluginInfo):
        """Update dependency tracking information."""
        # Track what this plugin depends on
        self.plugin_dependencies[plugin_info.name] = set(plugin_info.dependencies)

        # Track what depends on this plugin
        for dep in plugin_info.dependencies:
            if dep not in self.plugin_dependents:
                self.plugin_dependents[dep] = set()
            self.plugin_dependents[dep].add(plugin_info.name)

    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin."""
        async with self._lock:
            try:
                if plugin_name not in self.plugins:
                    logger.warning(f"Plugin {plugin_name} is not loaded")
                    return True

                plugin_info = self.plugin_info[plugin_name]

                # Check if other plugins depend on this one
                dependents = self.plugin_dependents.get(plugin_name, set())
                if dependents:
                    logger.warning(f"Cannot unload {plugin_name}, plugins depend on it: {dependents}")
                    return False

                # Run pre-unload hooks
                await self._run_hooks(self.pre_unload_hooks, plugin_info)

                # Shutdown plugin
                await self.plugins[plugin_name].shutdown()

                # Remove from tracking
                del self.plugins[plugin_name]
                plugin_info.loaded = False

                # Clean up dependency tracking
                self._cleanup_dependency_tracking(plugin_name)

                # Run post-unload hooks
                await self._run_hooks(self.post_unload_hooks, plugin_info)

                logger.info(f"Plugin {plugin_name} unloaded successfully")
                return True

            except Exception as e:
                logger.error(f"Failed to unload plugin {plugin_name}: {e}")
                return False

    def _cleanup_dependency_tracking(self, plugin_name: str):
        """Clean up dependency tracking for a plugin."""
        # Remove from dependencies
        if plugin_name in self.plugin_dependencies:
            del self.plugin_dependencies[plugin_name]

        # Remove from dependents
        if plugin_name in self.plugin_dependents:
            del self.plugin_dependents[plugin_name]

        # Remove from other plugins' dependency lists
        for deps in self.plugin_dependencies.values():
            deps.discard(plugin_name)

        for deps in self.plugin_dependents.values():
            deps.discard(plugin_name)

    async def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin."""
        if await self.unload_plugin(plugin_name):
            return await self.load_plugin(plugin_name)
        return False

    async def get_plugin(self, plugin_name: str) -> Optional[PluginProtocol]:
        """Get a loaded plugin by name."""
        return self.plugins.get(plugin_name)

    async def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get plugin information by name."""
        return self.plugin_info.get(plugin_name)

    async def list_plugins(self) -> List[PluginInfo]:
        """List all plugins (loaded and discovered)."""
        return list(self.plugin_info.values())

    async def list_loaded_plugins(self) -> List[str]:
        """List names of loaded plugins."""
        return list(self.plugins.keys())

    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all loaded plugins."""
        health_status = {}

        for name, plugin in self.plugins.items():
            try:
                health_status[name] = await plugin.health_check()
                self.plugin_info[name].last_health_check = time.time()
            except Exception as e:
                logger.error(f"Health check failed for plugin {name}: {e}")
                health_status[name] = False
                self.plugin_info[name].last_error = str(e)

        return health_status

    async def _run_hooks(self, hooks: List[callable], plugin_info: PluginInfo):
        """Run plugin lifecycle hooks."""
        for hook in hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(plugin_info)
                else:
                    hook(plugin_info)
            except Exception as e:
                logger.error(f"Hook {hook.__name__} failed: {e}")

    def add_hook(self, hook_type: str, hook: callable):
        """Add a lifecycle hook."""
        if hook_type == "pre_load":
            self.pre_load_hooks.append(hook)
        elif hook_type == "post_load":
            self.post_load_hooks.append(hook)
        elif hook_type == "pre_unload":
            self.pre_unload_hooks.append(hook)
        elif hook_type == "post_unload":
            self.post_unload_hooks.append(hook)
        else:
            raise ValueError(f"Unknown hook type: {hook_type}")

    async def shutdown(self):
        """Shutdown all plugins."""
        logger.info("Shutting down plugin manager...")

        # Set shutdown event
        self._shutdown_event.set()

        # Unload all plugins
        for plugin_name in list(self.plugins.keys()):
            await self.unload_plugin(plugin_name)

        logger.info("Plugin manager shutdown complete")


# Global plugin manager instance
plugin_manager = PluginManager()
