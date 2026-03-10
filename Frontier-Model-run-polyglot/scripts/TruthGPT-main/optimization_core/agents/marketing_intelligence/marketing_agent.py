"""
OpenClaw Marketing Intelligence Agent.

Specialised in creating marketing content and competitive analysis
by leveraging web-search tools through the ReAct architecture.
"""

import logging
from typing import Any, Dict, Optional

from ..arquitecturas_fundamentales.base_agent import BaseAgent
from ..razonamiento_planificacion.orchestrator import MultiUserReActAgent
from ..razonamiento_planificacion.tools import WebReaderTool, WebSearchTool
from ..models import AgentResponse

logger = logging.getLogger(__name__)

# Marketing-specific system prompt extension
_MARKETING_SYSTEM_EXTENSION = (
    "\n\n"
    "SPECIFIC ROLE: You are an autonomous Digital Marketing Intelligence, "
    "SEO, and Growth Hacking agent.\n"
    "You MUST use your web tools (web_search, web_reader) to research "
    "competitors when solving problems. Search for current trends and "
    "provide data-driven content strategies."
)


class _MarketingReActAgent(MultiUserReActAgent):
    """ReAct agent with marketing-specific system instructions."""

    def _get_system_instructions(self) -> str:
        base = super()._get_system_instructions()
        return f"{base}{_MARKETING_SYSTEM_EXTENSION}"


class ContentMarketingAgent(BaseAgent):
    """
    OpenClaw Marketing Intelligence Agent.

    Delegates query processing to an internal ReAct agent that has
    web-search and web-reader tools, with a marketing-focused system prompt.
    """

    def __init__(self, llm_engine: Any) -> None:
        super().__init__(
            name="MarketingAgent",
            role="Marketing and SEO Specialist",
        )
        self._react = _MarketingReActAgent(llm_engine=llm_engine)
        self._react.register_tool(WebSearchTool())
        self._react.register_tool(WebReaderTool())

    async def process(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Process a marketing query using the internal ReAct agent."""
        logger.info("%s processing: %s", self.name, query)

        user_id = (
            context.get("user_id", "default_marketing_user")
            if context
            else "default_marketing_user"
        )

        try:
            response: AgentResponse = await self._react.process_message(user_id, query)
            self.add_to_memory("user", query)
            self.add_to_memory("assistant", response.content)
            return response
        except Exception:
            logger.exception("Error processing in %s", self.name)
            return AgentResponse(content=f"Error in {self.name}: processing failed.", action_type="final_answer")
