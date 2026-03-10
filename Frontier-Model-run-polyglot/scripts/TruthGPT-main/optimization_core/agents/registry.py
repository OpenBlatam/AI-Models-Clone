"""
Centralized Tool and Engine Registry for TruthGPT.
"""

from typing import Dict, Any, Optional
from .razonamiento_planificacion.tools import (
    FileReadTool,
    FileWriteTool,
    PythonExecutionTool,
    SystemBashTool,
    WebReaderTool,
    WebSearchTool,
    DelegateTaskTool,
)

class DummyAsyncLLM:
    """Echo LLM used when no real engine is provided."""
    async def __call__(self, prompt: str) -> str:
        return f"Echo from OpenClaw Agent: Received prompt of {len(prompt)} characters."

_TOOL_REGISTRY: Dict[str, type] = {
    "system_bash": SystemBashTool,
    "web_search": WebSearchTool,
    "web_reader": WebReaderTool,
    "file_read": FileReadTool,
    "file_write": FileWriteTool,
    "python_execute": PythonExecutionTool,
    "delegate_task": DelegateTaskTool,
}

def get_tool(name: str) -> Optional[type]:
    """Retrieve a tool class by its name."""
    return _TOOL_REGISTRY.get(name)

def get_all_tools() -> Dict[str, type]:
    """Retrieve the entire tool registry."""
    return _TOOL_REGISTRY.copy()
