import logging
import re
import asyncio
from typing import List, Dict, Any, Callable, Protocol, Optional, runtime_checkable, Type

# Contexto de imports
try:
    from agents.memoria_aprendizaje.sqlite_memory import SQLiteMemory, BaseMemory
    from agents.razonamiento_planificacion.tools import BaseTool
    from agents.razonamiento_planificacion.config import settings
except ImportError:
    from ..memoria_aprendizaje.sqlite_memory import SQLiteMemory, BaseMemory
    from .tools import BaseTool
    from .config import settings

logger = logging.getLogger(__name__)

@runtime_checkable
class AsyncLLMEngine(Protocol):
    """Protocolo para un motor de inferencia LLM asíncrono."""
    async def __call__(self, prompt: str) -> str:
        ...

class MultiUserReActAgent:
    """
    Orquestador ReAct Multi-Usuario de Grado Empresarial.
    Gestión asíncrona de bucles de razonamiento y herramientas.
    """
    
    TOOL_PATTERN = re.compile(r"<tool>(.*?)</tool>", re.DOTALL)
    CMD_PATTERN = re.compile(r"<cmd>(.*?)</cmd>", re.DOTALL)

    def __init__(
        self, 
        llm_engine: AsyncLLMEngine, 
        memory: Optional[BaseMemory] = None,
        memory_db_path: Optional[str] = None
    ):
        self.llm = llm_engine
        self.memory = memory or SQLiteMemory(db_path=memory_db_path or settings.DATABASE_PATH)
        self.tools: Dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool):
        """Registra una instancia de BaseTool."""
        self.tools[tool.name] = tool
        logger.info(f"Habilidad registrada: {tool.name}")

    def _get_system_instructions(self) -> str:
        """Genera instrucciones dinámicas basadas en las herramientas registradas."""
        tools_desc = "\n".join([f"- {t.name}: {t.description}" for t in self.tools.values()])
        return settings.SYSTEM_PROMPT_TEMPLATE.format(name=settings.AGENT_NAME) + (
            f"\nTienes acceso a estas herramientas:\n{tools_desc}\n\n"
            "Formato XML obligatorio para herramientas:\n"
            "<tool>nombre</tool>\n"
            "<cmd>argumento</cmd>\n"
        )

    async def _format_context(self, user_id: str) -> str:
        history = await self.memory.get_history(user_id)
        if not history:
            return f"--- MEMORIA PRIVADA ({user_id}) ---\nSin historial previo.\n"
        
        context = f"--- MEMORIA PRIVADA ({user_id}) ---\n"
        for msg in history:
            context += f"{msg['role'].upper()}: {msg['content']}\n"
        context += "--------------------------------------\n"
        return context

    async def process_message(self, user_id: str, message: str) -> str:
        """
        Procesa un mensaje de forma asíncrona aislando el contexto por usuario.
        """
        logger.info(f"Iniciando proceso asíncrono para {user_id}")
        await self.memory.add_message(user_id, "user", message)
        
        system_prompt = self._get_system_instructions()
        user_context = await self._format_context(user_id)
        current_prompt = f"{system_prompt}\n{user_context}\nUSER: {message}\nTRUTHGPT: "
        
        for i in range(settings.MAX_ITERATIONS):
            # Inferencia asíncrona
            response = await self.llm(current_prompt)
            
            tool_match = self.TOOL_PATTERN.search(response)
            if tool_match:
                tool_name = tool_match.group(1).strip()
                cmd_match = self.CMD_PATTERN.search(response)
                cmd = cmd_match.group(1).strip() if cmd_match else ""

                if tool_name in self.tools:
                    logger.info(f"Ejecutando {tool_name} asíncronamente...")
                    result = await self.tools[tool_name].run(cmd)
                else:
                    result = f"Error: La herramienta '{tool_name}' no existe."
                
                current_prompt += f"{response}\nTOOL_RESULT: {result}\nTRUTHGPT: "
            else:
                await self.memory.add_message(user_id, "assistant", response)
                return response
        
        fallback = "Límite de razonamiento alcanzado. Por favor, simplifica tu petición."
        await self.memory.add_message(user_id, "assistant", fallback)
        return fallback
