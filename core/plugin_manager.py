"""
Plugin management system for the modular dependency management system.
Allows dynamic loading and management of plugins.
"""

import os
import sys
import importlib
import importlib.util
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import logging

from .dependency_structures import ServiceStatus, ServicePriority


@dataclass
class PluginInfo:
    """Information about a loaded plugin"""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = field(default_factory=list)
    entry_point: Optional[str] = None
    is_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PluginHook:
    """Plugin hook definition"""
    name: str
    callback: Callable
    priority: int = 0
    is_async: bool = False


class PluginManager:
    """Manages plugin loading, registration, and execution"""
    
    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        self.plugins: Dict[str, PluginInfo] = {}
        self.hooks: Dict[str, List[PluginHook]] = {}
        self.plugin_modules: Dict[str, Any] = {}
        self.plugin_dirs = plugin_dirs or ["plugins"]
        self.logger = logging.getLogger(__name__)
        
        # Create plugin directories if they don't exist
        for plugin_dir in self.plugin_dirs:
            Path(plugin_dir).mkdir(exist_ok=True)
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugins in plugin directories"""
        discovered = []
        
        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                continue
                
            for item in os.listdir(plugin_dir):
                plugin_path = os.path.join(plugin_dir, item)
                
                if os.path.isdir(plugin_path):
                    # Directory-based plugin
                    init_file = os.path.join(plugin_path, "__init__.py")
                    if os.path.exists(init_file):
                        discovered.append(item)
                        
                elif item.endswith('.py') and not item.startswith('_'):
                    # Single file plugin
                    discovered.append(item[:-3])
        
        return discovered
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a plugin by name"""
        try:
            # Try to find the plugin
            plugin_path = None
            for plugin_dir in self.plugin_dirs:
                potential_path = os.path.join(plugin_dir, plugin_name)
                
                if os.path.isdir(potential_path):
                    # Directory-based plugin
                    init_file = os.path.join(potential_path, "__init__.py")
                    if os.path.exists(init_file):
                        plugin_path = potential_path
                        break
                        
                elif os.path.exists(potential_path + '.py'):
                    # Single file plugin
                    plugin_path = potential_path + '.py'
                    break
            
            if not plugin_path:
                self.logger.error(f"Plugin {plugin_name} not found")
                return False
            
            # Load the plugin module
            if plugin_path.endswith('.py'):
                # Single file plugin
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                # Directory-based plugin
                sys.path.insert(0, plugin_path)
                module = importlib.import_module(plugin_name)
                sys.path.pop(0)
            
            # Extract plugin information
            plugin_info = PluginInfo(
                name=plugin_name,
                version=getattr(module, '__version__', '1.0.0'),
                description=getattr(module, '__description__', ''),
                author=getattr(module, '__author__', 'Unknown'),
                dependencies=getattr(module, '__dependencies__', []),
                entry_point=getattr(module, '__entry_point__', None)
            )
            
            # Store the plugin
            self.plugins[plugin_name] = plugin_info
            self.plugin_modules[plugin_name] = module
            
            # Register hooks if the plugin has them
            if hasattr(module, 'register_hooks'):
                module.register_hooks(self)
            
            self.logger.info(f"Plugin {plugin_name} loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin"""
        if plugin_name not in self.plugins:
            return False
        
        try:
            # Remove hooks
            hooks_to_remove = []
            for hook_name, hooks in self.hooks.items():
                hooks_to_remove.extend([
                    (hook_name, hook) for hook in hooks 
                    if hasattr(hook.callback, '__module__') and 
                    hook.callback.__module__.startswith(plugin_name)
                ])
            
            for hook_name, hook in hooks_to_remove:
                self.hooks[hook_name].remove(hook)
            
            # Remove plugin
            del self.plugins[plugin_name]
            del self.plugin_modules[plugin_name]
            
            self.logger.info(f"Plugin {plugin_name} unloaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def register_hook(self, hook_name: str, callback: Callable, priority: int = 0, is_async: bool = False):
        """Register a hook callback"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        
        hook = PluginHook(
            name=hook_name,
            callback=callback,
            priority=priority,
            is_async=is_async
        )
        
        self.hooks[hook_name].append(hook)
        
        # Sort by priority (higher priority first)
        self.hooks[hook_name].sort(key=lambda h: h.priority, reverse=True)
    
    async def execute_hooks(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Execute all registered hooks for a given hook name"""
        results = []
        
        if hook_name not in self.hooks:
            return results
        
        for hook in self.hooks[hook_name]:
            try:
                if hook.is_async:
                    result = await hook.callback(*args, **kwargs)
                else:
                    result = hook.callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error executing hook {hook_name}: {e}")
                results.append(None)
        
        return results
    
    def execute_hooks_sync(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Execute all registered hooks synchronously"""
        results = []
        
        if hook_name not in self.hooks:
            return results
        
        for hook in self.hooks[hook_name]:
            try:
                if hook.is_async:
                    self.logger.warning(f"Hook {hook_name} is async but called synchronously")
                    results.append(None)
                else:
                    result = hook.callback(*args, **kwargs)
                    results.append(result)
            except Exception as e:
                self.logger.error(f"Error executing hook {hook_name}: {e}")
                results.append(None)
        
        return results
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get information about a plugin"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[PluginInfo]:
        """List all loaded plugins"""
        return list(self.plugins.values())
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].is_enabled = True
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].is_enabled = False
            return True
        return False
    
    def get_plugin_module(self, plugin_name: str) -> Optional[Any]:
        """Get the module object for a plugin"""
        return self.plugin_modules.get(plugin_name)
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin"""
        if self.unload_plugin(plugin_name):
            return self.load_plugin(plugin_name)
        return False


# Global plugin manager instance
plugin_manager = PluginManager()


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance"""
    return plugin_manager


def register_hook(hook_name: str, callback: Callable, priority: int = 0, is_async: bool = False):
    """Register a hook with the global plugin manager"""
    plugin_manager.register_hook(hook_name, callback, priority, is_async)


async def execute_hooks(hook_name: str, *args, **kwargs) -> List[Any]:
    """Execute hooks with the global plugin manager"""
    return await plugin_manager.execute_hooks(hook_name, *args, **kwargs)


def execute_hooks_sync(hook_name: str, *args, **kwargs) -> List[Any]:
    """Execute hooks synchronously with the global plugin manager"""
    return plugin_manager.execute_hooks_sync(hook_name, *args, **kwargs)
