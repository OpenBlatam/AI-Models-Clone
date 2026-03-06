import logging
from typing import Any, Dict, Optional
from ..arquitecturas_fundamentales.base_agent import BaseAgent
from ..razonamiento_planificacion.orchestrator import MultiUserReActAgent
from ..razonamiento_planificacion.tools import WebSearchTool, WebReaderTool

logger = logging.getLogger(__name__)

class ContentMarketingAgent(BaseAgent):
    """
    OpenClaw Marketing Intelligence Agent
    Especializado en crear contenido y análisis de marketing utilizando herramientas web para buscar data real.
    """
    def __init__(self, llm_engine: Any):
        super().__init__(name="MarketingAgent", role="Especialista en Marketing y SEO")
        # Utilizamos la arquitectura ReAct interna para darle autonomía real
        self.react_agent = MultiUserReActAgent(llm_engine=llm_engine)
        self.react_agent.register_tool(WebSearchTool())
        self.react_agent.register_tool(WebReaderTool())
        
        # Sobrescribimos temporalmente las instrucciones base para que actúe como marketero
        self.original_get_system = self.react_agent._get_system_instructions
        
        def custom_system_instructions() -> str:
            base_instructions = self.original_get_system()
            return (
                f"{base_instructions}\n\n"
                "ROL ESPECÍFICO DE ESTE AGENTE: Eres un agente autónomo de Inteligencia en Marketing Digital, SEO y Growth Hacking.\n"
                "DEBES utilizar tus herramientas web (web_search, web_reader) para investigar a la competencia al resolver "
                "problemas. Busca tendencias actuales y proporciona estrategias de contenido basadas en datos verídicos."
            )
        self.react_agent._get_system_instructions = custom_system_instructions

    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        logger.info(f"{self.name} procesando: {query}")
        user_id = context.get("user_id", "default_marketing_user") if context else "default_marketing_user"
        
        try:
            # Delegamos al agente ReAct para que tome decisiones y use herramientas
            response = await self.react_agent.process_message(user_id, query)
            self.add_to_memory("user", query)
            self.add_to_memory("assistant", response)
            return response
        except Exception as e:
            logger.error(f"Error procesando en {self.name}: {str(e)}")
            return f"Error en {self.name}: {str(e)}"
