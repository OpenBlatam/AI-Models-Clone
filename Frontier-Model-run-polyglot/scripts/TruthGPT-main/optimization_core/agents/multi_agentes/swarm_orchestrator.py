"""
OpenClaw Swarm Orchestrator.

Routes user queries to the most appropriate agent within a swarm,
using either LLM-based intelligent routing or keyword-based fallback.
"""

import json
import logging
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, Field, create_model

from ..arquitecturas_fundamentales.base_agent import BaseAgent
from ..models import AgentResponse

logger = logging.getLogger(__name__)


class SwarmOrchestrator:
    """
    Routes queries to the best-fit agent in a multi-agent swarm.

    Routing strategy:
    1. If an LLM engine is provided, ask the LLM to pick the target agent.
    2. If the LLM returns an invalid name, fall back to keyword matching.
    3. If no LLM is available, use keyword matching directly.
    4. If nothing matches, delegate to the first registered agent.
    """

    def __init__(self, llm_engine: Optional[Any] = None) -> None:
        self.agents: Dict[str, BaseAgent] = {}
        self.llm = llm_engine

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent in the swarm."""
        self.agents[agent.name] = agent
        logger.info("Agent registered in swarm: %s (%s)", agent.name, agent.role)

    async def route_and_process(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Route *query* to the most suitable agent and return its response.
        
        Always returns a structured AgentResponse.
        """
        if not self.agents:
            raise ValueError("No agents registered in the swarm.")

        target_agent = await self._route_query(query)

        if target_agent is None:
            target_agent = next(iter(self.agents.values()))

        logger.info("Routing query to agent: %s", target_agent.name)
        return await target_agent.process(query, context)

    def _scrub_json(self, text: str) -> str:
        """Clean up LLM response to get a raw JSON string."""
        clean = text.strip()
        # Remove triple backticks first
        if "```" in clean:
            import re
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", clean, re.DOTALL)
            if match:
                clean = match.group(1).strip()
        
        # If still no valid JSON start/end, try to find the first '{' and last '}'
        if not (clean.startswith('{') and clean.endswith('}')):
            start = clean.find('{')
            end = clean.rfind('}')
            if start != -1 and end != -1:
                clean = clean[start:end+1]
        
        return clean

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _route_query(self, query: str) -> Optional[BaseAgent]:
        """
        Determine which agent should handle *query*.

        Tries LLM-based routing first; falls back to keyword matching.
        """
        if self.llm:
            return await self._route_via_llm(query)
        return self._route_via_keywords(query)

    async def _route_via_llm(self, query: str) -> BaseAgent:
        """Use the LLM to decide the target agent using strict Pydantic JSON validation."""
        agents_info = "\n".join(
            f"- {a.name}: {a.role}" for a in self.agents.values()
        )
        
        # Build dynamic literal exactly for the registered agents
        target_keys = list(self.agents.keys())
        schema_dict = {
            "title": "RouterDecision",
            "type": "object",
            "properties": {
                "reasoning": {
                    "title": "Reasoning",
                    "type": "string",
                    "description": "Explica paso a paso por qué escogiste a este agente en base a la petición del usuario."
                },
                "target_agent": {
                    "title": "Target Agent",
                    "type": "string",
                    "enum": target_keys,
                    "description": "El nombre exacto del agente seleccionado."
                }
            },
            "required": ["reasoning", "target_agent"]
        }
        schema_str = json.dumps(schema_dict, indent=2)

        prompt = (
            "### MASTER ROUTER ROLE\n"
            "You are the Master Router of a SOTA 2025 Multi-Agent Swarm.\n"
            "Your task is to route the user query to the most capable specialized agent.\n\n"
            "### AVAILABLE AGENTS\n"
            f"{agents_info}\n\n"
            f"### USER QUERY\n"
            f"'{query}'\n\n"
            "### INSTRUCTIONS\n"
            "1. Analyze the query semantic intent.\n"
            "2. Select the agent whose role best matches the query.\n"
            "3. Return a JSON response matching the following schema:\n"
            f"{schema_str}\n\n"
            "### CRITICAL RULE\n"
            "Respond ONLY with raw JSON. No conversational text, no markdown wrappers if possible."
        )

        for attempt in range(3):
            try:
                decision = await self.llm(prompt)
                clean_resp = self._scrub_json(decision)
                
                parsed = json.loads(clean_resp)
                chosen_name = parsed.get("target_agent", "")
                reasoning = parsed.get("reasoning", "")
                
                logger.debug(f"[Router Chain of Thought] {reasoning}")

                if chosen_name in self.agents:
                    logger.info(f"LLM Semantic Router selected: {chosen_name}")
                    return self.agents[chosen_name]

                logger.warning(
                    f"Swarm LLM returned invalid name: '{chosen_name}'. Attempt {attempt+1}/3"
                )
            except json.JSONDecodeError as e:
                logger.warning(f"Router LLM JSON Parse Error: {e}. Retry...")
                prompt += f"\nERROR: Tu respuesta no era un JSON válido ({e}). Corrige y responde de nuevo SÓLO con JSON."
            except Exception as e:
                logger.exception("LLM routing internal error.")
                break

        logger.warning("All LLM routing attempts failed. Falling back to keyword routing.")
        return self._route_via_keywords(query)

    def _route_via_keywords(self, query: str) -> BaseAgent:
        """Match agents by checking whether their name or role appears in the query."""
        query_lower = query.lower()
        for agent in self.agents.values():
            if agent.name.lower() in query_lower or agent.role.lower() in query_lower:
                return agent

        # Default: first registered agent
        return next(iter(self.agents.values()))
