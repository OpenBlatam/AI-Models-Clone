from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from ..models import AgentResponse

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
    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Procesa una consulta y devuelve un objeto AgentResponse estructurado."""
        pass

    def add_to_memory(self, role: str, content: str):
        self.memory.append({"role": role, "content": content})

    def get_memory(self) -> List[Dict[str, Any]]:
        """Devuelve una copia de la memoria episódica."""
        return self.memory.copy()

    def clear_memory(self):
        self.memory.clear()
