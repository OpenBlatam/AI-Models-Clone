"""
Agent Communication Models.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict

class AgentAction(BaseModel):
    """Result of an LLM reasoning step."""
    tool: Optional[str] = Field(None, description="Nombre de la herramienta a usar. Null si respondes al usuario final.")
    cmd: Optional[str] = Field(None, description="Argumento o comando a enviar a la herramienta.")
    respuesta_final: Optional[str] = Field(None, description="Tu mensaje final dirigido al usuario usando Markdown. Null si usas una herramienta.")
    handoff: Optional[str] = Field(None, description="[OPCIONAL] Nombre del agente experto al que quieres transferir la conversación.")

class AgentResponse(BaseModel):
    """Response from the agent orchestrator to the client."""
    content: str
    action_type: str  # 'final_answer', 'handoff', 'approval_required'
    metadata: Dict[str, Any] = Field(default_factory=dict)
    handoff_target: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)

class InferenceResult(BaseModel):
    """Unified model for LLM inference outputs."""
    text: str = Field(..., description="The generated text content.")
    tokens_generated: Optional[int] = Field(None, description="Number of tokens produced.")
    latency_ms: Optional[float] = Field(None, description="Time taken for inference in milliseconds.")
    model_name: Optional[str] = Field(None, description="Name of the model that generated this.")
    finish_reason: Optional[str] = Field(None, description="Why the generation stopped.")
    metadata: Dict[str, Any] = Field(default_factory=dict)
class AgentConfig(BaseModel):
    """Configuration for the AgentClient."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    llm_engine: Optional[Any] = None
    memory_db_path: str = "openclaw_memory.db"
    use_swarm: bool = False
    use_vector_memory: bool = False
    use_reflexion: bool = False
    max_handoff_depth: int = 5
    enable_telemetry: bool = True
