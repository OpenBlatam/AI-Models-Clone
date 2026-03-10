"""
OpenClaw Agent -- Data Analysis.

Specialised agent for reading, parsing and analysing structured data
(CSV, JSON, Excel).  Uses PythonExecutionTool to run pandas/matplotlib
scripts and returns insights plus generated charts.
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


class DataAnalysisAgent(BaseAgent):
    """
    Autonomous data analysis agent.

    Capabilities:
    - Read CSV / JSON / Excel files.
    - Generate summary statistics, correlations, and distributions.
    - Create matplotlib / seaborn charts and save them to disk.
    - Answer natural-language questions about the data.
    """

    def __init__(self, llm_engine: Any) -> None:
        super().__init__(
            name="DataAnalysisAgent",
            role="Analista de Datos Autonomo con Python y Pandas",
        )

        custom_instructions = (
            "You are an autonomous Data Analysis agent.\n"
            "Your workflow:\n"
            "1. Read the data file the user provides (use file_read).\n"
            "2. Write a Python script that uses pandas to clean and analyse the data.\n"
            "3. Execute the script (python_execute) and inspect the output.\n"
            "4. If the user asks for a chart, generate it with matplotlib/seaborn "
            "and save it as a PNG file (use file_write for any helper code).\n"
            "5. Summarise your findings in a clear, structured report.\n"
            "Always include numeric insights (mean, median, std, top values)."
        )

        self.react_agent = MultiUserReActAgent(
            llm_engine=llm_engine,
            custom_system_instructions=custom_instructions,
        )
        self.react_agent.register_tool(PythonExecutionTool())
        self.react_agent.register_tool(FileReadTool())
        self.react_agent.register_tool(FileWriteTool())

    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        user_id = (context or {}).get("user_id", "data_analysis_default")
        logger.info("[%s] Processing: %s", self.name, query[:80])
        try:
            response: AgentResponse = await self.react_agent.process_message(user_id, query)
            self.add_to_memory("user", query)
            self.add_to_memory("assistant", response.content)
            return response
        except Exception as e:
            logger.exception("[%s] Error processing query: %s", self.name, e)
            return AgentResponse(content=f"Error in {self.name}: {str(e)}", action_type="final_answer")
