"""
OpenClaw Multi-Agent -- Graph-Based Orchestrator (LangGraph).

Implements a Directed Acyclic Graph (DAG) state machine for agents using LangGraph.
This allows sequential and conditional workflows where one agent's output 
becomes the next agent's input, with persistence and cyclic support.
"""

import logging
from typing import Any, Callable, Dict, Optional, TypedDict, Annotated, Sequence
import operator

try:
    from langgraph.graph import StateGraph, END
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False

# Contexto de imports
try:
    from agents.arquitecturas_fundamentales.base_agent import BaseAgent
    from agents.models import AgentResponse
except ImportError:
    from ..arquitecturas_fundamentales.base_agent import BaseAgent
    from ..models import AgentResponse

logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """Shared state object passed between agents in the LangGraph."""
    user_id: str
    initial_input: str
    current_input: str
    history: Annotated[list[dict], operator.add]
    metadata: dict


class GraphOrchestrator:
    """
    LangGraph-based orchestrator for sequential and conditional agent workflows.

    Usage:
        orchestrator = GraphOrchestrator()
        orchestrator.add_node("data_agent", data_agent)
        orchestrator.add_node("writer_agent", writer_agent)
        
        orchestrator.add_edge("data_agent", "writer_agent")
        orchestrator.set_entry_point("data_agent")
        orchestrator.compile()
        
        result = await orchestrator.run("user_1", "Analyze sales.csv and write a report")
    """

    def __init__(self) -> None:
        self.nodes: Dict[str, BaseAgent] = {}
        if not HAS_LANGGRAPH:
            logger.warning("LangGraph no está instalado. Usando fallback básico o fallará. 'pip install langgraph'")
        self.workflow = StateGraph(GraphState) if HAS_LANGGRAPH else None
        self.app = None
        self.entry_point: Optional[str] = None

    def add_node(self, name: str, agent: BaseAgent) -> None:
        """Register an agent as a node in the graph."""
        self.nodes[name] = agent
        
        async def _node_executor(state: GraphState) -> dict:
            logger.info(f"LangGraph executing node: {name}")
            prompt = (
                f"[SYSTEM INSTRUCTION: You are part of a pipeline. "
                f"Previous output: {state['current_input']}]\n\n"
                f"Next task: Please continue the workflow."
            )
            if len(state["history"]) == 0:
                prompt = state["initial_input"]
                
            # Assume process is an async method of BaseAgent in this context
            result = await agent.process(prompt, context={"user_id": state["user_id"]})
            
            result_text = result.content if isinstance(result, AgentResponse) else str(result)
            
            return {
                "current_input": result_text,
                "history": [{"agent": name, "result": result_text}]
            }
            
        if self.workflow:
            self.workflow.add_node(name, _node_executor)
        logger.info(f"Added LangGraph node: {name}")

    def set_entry_point(self, name: str) -> None:
        """Set the starting node of the graph."""
        self.entry_point = name
        if self.workflow:
            if name not in self.nodes:
                raise ValueError(f"Entry point {name} is not a valid node.")
            self.workflow.set_entry_point(name)

    def add_edge(self, from_node: str, to_node: str) -> None:
        """Add a static sequence from one node to another."""
        if self.workflow:
            # Si to_node es '__end__', convertimos a END de langgraph
            target = END if to_node == "__end__" else to_node
            self.workflow.add_edge(from_node, target)

    def add_conditional_edge(self, from_node: str, condition_func: Callable[[GraphState], str]) -> None:
        """Add a dynamic edge based on the state."""
        if self.workflow:
            self.workflow.add_conditional_edges(from_node, condition_func)

    def compile(self) -> None:
        """Compiles the LangGraph for execution."""
        if self.workflow:
            self.app = self.workflow.compile()
            logger.info("LangGraph compilado exitosamente.")

    async def run(self, user_id: str, initial_input: str) -> AgentResponse:
        """Execute the compiled LangGraph and return a structured AgentResponse."""
        if not HAS_LANGGRAPH or not self.app:
            raise RuntimeError("LangGraph no está instalado o el grafo no está compilado. Ejecuta 'pip install langgraph' y llama a 'compile()'.")

        initial_state = {
            "user_id": user_id,
            "initial_input": initial_input,
            "current_input": initial_input,
            "history": [],
            "metadata": {}
        }

        logger.info(f"Starting LangGraph Orchestrator for {user_id}")
        
        # Ejecutar grafo asíncronamente
        final_state = await self.app.ainvoke(initial_state)
        
        return AgentResponse(
            content=final_state["current_input"],
            action_type="final_answer",
            metadata={"history": final_state["history"]}
        )
