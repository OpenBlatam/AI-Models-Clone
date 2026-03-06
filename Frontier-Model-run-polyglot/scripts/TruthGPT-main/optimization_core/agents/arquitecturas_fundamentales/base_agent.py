from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseAgent(ABC):
    """
    OpenClaw Base Agent Interface
    Define la estructura fundamental para cualquier agente del ecosistema.
    """
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.memory: List[Dict[str, Any]] = []

    @abstractmethod
    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Procesa una consulta y devuelve la respuesta del agente."""
        pass

    def add_to_memory(self, role: str, content: str):
        self.memory.append({"role": role, "content": content})

    def get_memory(self) -> List[Dict[str, Any]]:
        return self.memory

    def clear_memory(self):
        self.memory.clear()
