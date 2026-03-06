import logging
from typing import Any, Dict, List, Optional
import asyncio

# Imports de componentes internos
from .memoria_aprendizaje.sqlite_memory import SQLiteMemory
from .razonamiento_planificacion.orchestrator import MultiUserReActAgent
from .razonamiento_planificacion.tools import (
    SystemBashTool, WebSearchTool, WebReaderTool, 
    FileReadTool, FileWriteTool, PythonExecutionTool
)
from .multi_agentes.swarm_orchestrator import SwarmOrchestrator
from .marketing_intelligence.marketing_agent import ContentMarketingAgent

logger = logging.getLogger(__name__)

class DummyAsyncLLM:
    """Fallback LLM para pruebas si no se provee uno real."""
    async def __call__(self, prompt: str) -> str:
        return f"Echo from OpenClaw Agent: Recibí prompt de {len(prompt)} caracteres."

class AgentClient:
    """
    OpenClaw Agent Client (SDK)
    Interfaz principal para inicializar y usar agentes autónomos,
    diseñada para ser tan fácil de usar como OpenClaw.
    """
    
    # Registro de herramientas disponibles
    AVAILABLE_TOOLS = {
        "system_bash": SystemBashTool,
        "web_search": WebSearchTool,
        "web_reader": WebReaderTool,
        "file_read": FileReadTool,
        "file_write": FileWriteTool,
        "python_execute": PythonExecutionTool
    }

    def __init__(self, 
                 llm_engine: Optional[Any] = None, 
                 memory_db_path: str = "openclaw_memory.db",
                 use_swarm: bool = False):
        """
        Inicializa el cliente de agentes.
        :param llm_engine: Motor LLM asíncrono (debe tener un método asíncrono __call__(prompt)).
        :param memory_db_path: Ruta a la base de datos de memoria persistente.
        :param use_swarm: Si es True, inicializa un enjambre de agentes en lugar de uno solo.
        """
        self.llm_engine = llm_engine or DummyAsyncLLM()
        self.memory = SQLiteMemory(db_path=memory_db_path)
        self.use_swarm = use_swarm
        
        if self.use_swarm:
            self.swarm = SwarmOrchestrator(llm_engine=self.llm_engine)
            self._init_default_swarm()
        else:
            self.agent = MultiUserReActAgent(llm_engine=self.llm_engine, memory=self.memory)
            self._register_default_tools()

    def _init_default_swarm(self):
        """Inicializa agentes por defecto para el swarm."""
        marketing_agent = ContentMarketingAgent(llm_engine=self.llm_engine)
        from .embodied_rl.rl_agent import RLAgent
        rl_agent = RLAgent(llm_engine=self.llm_engine)
        
        self.swarm.register_agent(marketing_agent)
        self.swarm.register_agent(rl_agent)
        logger.info("Swarm inicializado con MarketingAgent y RLAgent por defecto.")

    def _register_default_tools(self):
        """Si no es swarm, carga las herramientas básicas al agente principal."""
        for tool_name, tool_class in self.AVAILABLE_TOOLS.items():
            try:
                self.agent.register_tool(tool_class())
            except Exception as e:
                logger.warning(f"No se pudo registrar herramienta {tool_name}: {e}")

    def add_tool(self, tool_name: str):
        """Habilita una herramienta específica en el agente."""
        if not self.use_swarm and tool_name in self.AVAILABLE_TOOLS:
            self.agent.register_tool(self.AVAILABLE_TOOLS[tool_name]())
            return True
        return False

    async def run(self, user_id: str, prompt: str) -> str:
        """
        Ejecuta el agente o el swarm para procesar un prompt.
        :param user_id: ID del usuario (para mantener contexto de memoria).
        :param prompt: Instrucción o consulta.
        :return: Respuesta final del agente.
        """
        if self.use_swarm:
            # Swarm orchestrator maneja el enrutamiento y procesamiento
            return await self.swarm.route_and_process(prompt, context={"user_id": user_id})
        else:
            # Agente ReAct estándar
            return await self.agent.process_message(user_id, prompt)

    async def clear_memory(self, user_id: str):
        """Limpia la memoria episódica del agente para un usuario dado."""
        await self.memory.clear_memory(user_id)
        return True
