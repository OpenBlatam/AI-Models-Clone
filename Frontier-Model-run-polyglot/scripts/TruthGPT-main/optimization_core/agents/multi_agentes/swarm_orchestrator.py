import logging
from typing import Dict, Any, List, Optional
from ..arquitecturas_fundamentales.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class SwarmOrchestrator:
    """
    OpenClaw Swarm Orchestrator
    Encargado de enrutar consultas al agente más adecuado dentro de un enjambre (swarm).
    """
    def __init__(self, llm_engine: Optional[Any] = None):
        self.agents: Dict[str, BaseAgent] = {}
        self.llm = llm_engine

    def register_agent(self, agent: BaseAgent):
        self.agents[agent.name] = agent
        logger.info(f"Agente registrado en el swarm: {agent.name} ({agent.role})")

    async def route_and_process(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        # Enrutamiento Inteligente usando LLM
        target_agent = list(self.agents.values())[0] # Default fallback
        if self.llm:
            agents_info = "\\n".join([f"- {a.name}: {a.role}" for a in self.agents.values()])
            prompt = (
                f"Eres un Enrutador Maestro en un enjambre de agentes (Swarm).\\n"
                f"Tu trabajo es leer la siguiente consulta del usuario y decidir qué agente debe procesarla.\\n"
                f"Agentes disponibles:\\n{agents_info}\\n\\n"
                f"Consulta del usuario: '{query}'\\n"
                f"REGLA OBLIGATORIA: Responde ÚNICAMENTE con el nombre exacto del agente, sin ninguna otra palabra."
            )
            
            try:
                # Obtenemos la decisión de ruteo del LLM
                decision = await self.llm(prompt)
                chosen_name = decision.strip()
                
                # Validamos que el agente exista
                if chosen_name in self.agents:
                    target_agent = self.agents[chosen_name]
                else:
                    # Fallback si el LLM se equivoca o inventa un nombre
                    logger.warning(f"Swarm LLM devolvió un nombre no válido: '{chosen_name}'. Usando fallback de palabras clave.")
                    for agent in self.agents.values():
                        if agent.name.lower() in query.lower() or agent.role.lower() in query.lower():
                            target_agent = agent
                            break
                    if 'target_agent' not in locals():
                        target_agent = next(iter(self.agents.values()))
            except Exception as e:
                logger.error(f"Error en enrutamiento por LLM: {str(e)}. Usando primer agente.")
        else:
            # Fallback a palabras clave si no hay LLM
            for agent in self.agents.values():
                if agent.name.lower() in query.lower() or agent.role.lower() in query.lower():
                    target_agent = agent
                    break
            
            # Si no hay coincidencia, seleccionar el primer agente por defecto
            if 'target_agent' not in locals():
                target_agent = next(iter(self.agents.values()))
        logger.info(f"Enrutando consulta al agente: {target_agent.name}")
        return await target_agent.process(query, context)
