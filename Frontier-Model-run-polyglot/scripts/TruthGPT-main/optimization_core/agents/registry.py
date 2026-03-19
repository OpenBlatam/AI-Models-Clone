"""
Centralized Tool and Engine Registry for TruthGPT — Pydantic-First.

Provides a singleton registry for discovering, registering, and
introspecting tools available to agents.
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .razonamiento_planificacion.tools import (
    FileReadTool,
    FileWriteTool,
    PythonExecutionTool,
    SystemBashTool,
    WebReaderTool,
    WebSearchTool,
    DelegateTaskTool,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class ToolInfo(BaseModel):
    """Structured introspection data for a registered tool."""
    name: str
    class_name: str
    module: str = ""
    has_run: bool = True


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class ToolRegistry:
    """Dynamic singleton registry for TruthGPT tools."""

    _instance = None
    _tools: Dict[str, type] = {}

    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
            cls._instance._init_builtins()
            cls._instance.discover_plugins()
        return cls._instance

    def _init_builtins(self) -> None:
        """Register core tools."""
        self._tools = {
            "system_bash": SystemBashTool,
            "web_search": WebSearchTool,
            "web_reader": WebReaderTool,
            "file_read": FileReadTool,
            "file_write": FileWriteTool,
            "python_execute": PythonExecutionTool,
            "delegate_task": DelegateTaskTool,
        }

    def register(self, name: str, tool_cls: type) -> None:
        """Manually register a tool."""
        self._tools[name] = tool_cls
        logger.info("Tool registered: %s -> %s", name, tool_cls.__name__)

    def get_tool(self, name: str) -> Optional[type]:
        return self._tools.get(name)

    def get_all_tools(self) -> Dict[str, type]:
        """Return all valid registered tools."""
        return {
            k: v for k, v in self._tools.items()
            if isinstance(k, str) and not k.startswith("__")
        }

    def list_tools(self) -> List[ToolInfo]:
        """Return structured Pydantic introspection of all registered tools."""
        return [
            ToolInfo(
                name=name,
                class_name=cls.__name__,
                module=cls.__module__ if hasattr(cls, "__module__") else "",
                has_run=hasattr(cls, "run"),
            )
            for name, cls in self.get_all_tools().items()
        ]

    def discover_plugins(self, plugins_dir: str = "plugins") -> None:
        """Dynamically load tools from a directory."""
        path = Path(plugins_dir)
        if not path.exists():
            return

        for file in path.glob("*.py"):
            if file.name == "__init__.py":
                continue

            module_name = f"{plugins_dir}.{file.stem}"
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and hasattr(obj, "name") and hasattr(obj, "run"):
                        self.register(obj.name, obj)
                        logger.info("Plugin discovered: %s", obj.name)
            except Exception as e:
                logger.warning("Error loading plugin %s: %s", module_name, e)


# Global singleton
registry = ToolRegistry()


def get_tool(name: str) -> Optional[type]:
    return registry.get_tool(name)


def get_all_tools() -> Dict[str, type]:
    return registry.get_all_tools()


def list_tools() -> List[ToolInfo]:
    """Return structured list of all registered tools."""
    return registry.list_tools()

