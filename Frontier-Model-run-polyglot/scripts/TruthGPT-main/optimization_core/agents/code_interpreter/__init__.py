"""
OpenClaw Agent -- Code Interpreter.

A specialised autonomous agent that writes, executes, and iterates on
Python code to solve tasks.  It uses the LLM as the reasoning engine and
the ``PythonExecutionTool`` + ``FileWriteTool`` combo for execution.
"""

import logging
from typing import Any, Dict, Optional

from ..arquitecturas_fundamentales.base_agent import BaseAgent
from ..razonamiento_planificacion.orchestrator import MultiUserReActAgent
from ..models import AgentResponse
from ..razonamiento_planificacion.tools import (
    FileReadTool,
    FileWriteTool,
    PythonExecutionTool,
)

logger = logging.getLogger(__name__)


class CodeInterpreterAgent(BaseAgent):
    """
    Autonomous code-writing and execution agent.

    Given a task, the agent will:
    1. Write Python code to solve it.
    2. Execute the code and inspect the output.
    3. Fix errors or refine the solution iteratively (ReAct loop).
    """

    def __init__(self, llm_engine: Any) -> None:
        super().__init__(
            name="CodeInterpreterAgent",
            role="Interprete de Codigo y Ejecucion Autonoma de Python",
        )

        custom_instructions = (
            "You are an autonomous Code Interpreter agent.\n"
            "Your workflow:\n"
            "1. Analyse the user request and plan a Python solution.\n"
            "2. Write the code to a temporary file using file_write.\n"
            "3. Execute it with python_execute and inspect the output.\n"
            "4. If there are errors, fix the code and re-execute.\n"
            "5. Return the final output to the user.\n"
            "Always show the code you wrote AND its output in the final answer."
        )

        self.react_agent = MultiUserReActAgent(
            llm_engine=llm_engine,
            custom_system_instructions=custom_instructions,
        )
        self.react_agent.register_tool(PythonExecutionTool())
        self.react_agent.register_tool(FileWriteTool())
        self.react_agent.register_tool(FileReadTool())

    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        user_id = (context or {}).get("user_id", "code_interpreter_default")
        logger.info("[%s] Processing: %s", self.name, query[:80])
        try:
            response: AgentResponse = await self.react_agent.process_message(user_id, query)
            self.add_to_memory("user", query)
            self.add_to_memory("assistant", response.content)
            return response
        except Exception as e:
            logger.error("[%s] Error: %s", self.name, e)
            return AgentResponse(content=f"Error in {self.name}: {e}", action_type="final_answer")
