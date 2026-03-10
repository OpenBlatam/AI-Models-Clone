import logging
import random
from typing import Any, Dict, Optional
from ..arquitecturas_fundamentales.base_agent import BaseAgent
from ..models import AgentResponse

logger = logging.getLogger(__name__)

class SimpleEnv:
    """Un entorno simulado para el Agente RL (Ej. Sistema de Anuncios, Pipeline)."""
    def __init__(self):
        self.state = "idle"
        self.performance_metric = 50

    def step(self, action: str) -> tuple[str, float, bool]:
        """Acepta una acción y devuelve (next_state, reward, done)."""
        if action == "optimize":
            self.performance_metric += random.randint(5, 15)
            self.state = "optimizing"
            reward = 10.0
        elif action == "explore":
            self.state = "exploring"
            reward = 5.0
            if random.random() < 0.2:
                self.performance_metric -= 10 # Encontró un problema inesperado
        elif action == "stop":
            self.state = "stopped"
            return self.state, 0.0, True
        else:
            self.state = "error_state"
            reward = -5.0
            
        done = self.performance_metric >= 100
        return self.state, reward, done

class RLAgent(BaseAgent):
    """
    OpenClaw Embodied RL Agent (Agente de Aprendizaje por Refuerzo Incorporado)
    Un agente autónomo que utiliza el LLM como "Política (Policy)" para decidir qué acción
    tomar interactuando con un entorno continuo, maximizando una recompensa.
    """
    def __init__(self, llm_engine: Any, env: Any = None):
        super().__init__(name="EmbodiedRLAgent", role="Agente de Aprendizaje por Refuerzo y Optimización")
        self.llm = llm_engine
        self.env = env or SimpleEnv()
        self.cumulative_reward = 0.0

    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        logger.info(f"{self.name} iniciando ciclo RL con objetivo: {query}")
        
        trajectory = []
        max_steps = 5
        
        for step_num in range(max_steps):
            state_desc = f"Estado=({self.env.state}), Métrica={self.env.performance_metric}"
            logger.info(f"[{self.name}] Observación Paso {step_num+1}: {state_desc}")
            
            # El LLM actúa como nuestra Policy decidiendo la acción según el estado
            prompt = (
                f"Eres un agente inteligente RL optimizando un sistema autónomo.\n"
                f"Objetivo global: {query}\n"
                f"Observación actual: {state_desc}\n"
                "Acciones permitidas: 'optimize' (seguro pero lento), 'explore' (arriesgado pero descubre), 'stop' (terminar).\n"
                "REGLA: Responde ÚNICAMENTE con la acción elegida, sin ningún markdown ni puntuación adicional."
            )
            
            try:
                # 1. Obtenemos acción de la Policy
                raw_action = await self.llm(prompt)
                action = raw_action.strip().lower()
                
                # Normalizamos
                if "optimize" in action:
                    action = "optimize"
                elif "explore" in action:
                    action = "explore"
                elif "stop" in action:
                    action = "stop"
                else:
                    action = "explore"  # Por defecto explorar
                
                logger.info(f"[{self.name}] Acción recomendada por el LLM: {action}")
                
                # 2. Transición del entorno
                next_state, reward, done = self.env.step(action)
                self.cumulative_reward += reward
                
                trajectory.append(f"[Score: {self.env.performance_metric} -> Act: {action} -> R: {reward}]")
                
                if done:
                    logger.info(f"[{self.name}] Episodio completado con éxito. Métrica >= 100.")
                    break
                    
            except Exception as e:
                return AgentResponse(content=f"Error crítico durante la simulación RL: {str(e)}", action_type="final_answer")
                
        # Resumen final
        summary = (
            f"**Simulación Embodied RL Completada**\n"
            f"- Objetivo Original: {query}\n"
            f"- Recompensa Total Acumulada: {self.cumulative_reward}\n"
            f"- Métrica de Rendimiento Final: {self.env.performance_metric}/100\n\n"
            f"**Trayectoria de Decisiones (State -> Action -> Reward):**\n" + " \n ".join(trajectory)
        )
        self.add_to_memory("user", query)
        self.add_to_memory("assistant", summary)
        return AgentResponse(content=summary, action_type="final_answer")
