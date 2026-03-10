from abc import ABC, abstractmethod
from typing import Any, Optional, Union
from ..models import AgentResponse

logger = logging.getLogger(__name__)


class BaseMessagingAdapter(ABC):
    """
    Abstract base for messaging platform adapters (Telegram, WhatsApp, etc.).

    Each adapter translates platform-specific events into a unified
    ``on_message`` call that forwards the text to an ``AgentClient``.
    """

    def __init__(self, agent_client: Any) -> None:
        self.agent_client = agent_client

    async def on_message(
        self,
        platform_user_id: str,
        text: str,
        metadata: Optional[dict] = None,
    ) -> AgentResponse:
        """
        Process an incoming message and return the agent's response.
        """

    async def send_response(
        self,
        platform_user_id: str,
        response: AgentResponse,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Send a response back to the user on the platform.
        """

    async def handle(
        self,
        platform_user_id: str,
        text: str,
        metadata: Optional[dict] = None,
    ) -> AgentResponse:
        """
        Full round-trip: receive a message, run the agent, send the reply.
        """
        logger.info(
            "[%s] Message from %s: %s",
            self.__name__,
            platform_user_id,
            text[:80],
        )
        # We always use the agent_client to run the logic
        # Note: agent_client.run currently returns str for simple BC.
        # But we can call the agent directly if we want the full AgentResponse.
        
        response = await self.on_message(platform_user_id, text, metadata)
        await self.send_response(platform_user_id, response, metadata)
        return response
