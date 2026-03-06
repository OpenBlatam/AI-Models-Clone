from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import uuid
import time
from .client import AgentClient

# Instancia global del cliente del agente para la API
# Al ser API, usamos una config estándar asíncrona (con o sin swarm)
# Para producción, se usaría un LLM real (ej: llamando a build_model localmente).
agent_client = AgentClient(use_swarm=False)

router = APIRouter(
    prefix="/v1/agent",
    tags=["Agent API"],
    responses={404: {"description": "Not found"}},
)

class AgentRequest(BaseModel):
    prompt: str = Field(..., description="Instrucción a ejecutar por el agente")
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID de usuario para mantener la memoria y el contexto")
    enable_swarm: bool = Field(False, description="Activar el enjambre de agentes en lugar de un único agente ReAct")
    tools: Optional[list[str]] = Field(None, description="Lista opcional de herramientas a registrar/habilitar")

class AgentResponse(BaseModel):
    user_id: str
    response: str
    latency_ms: float

@router.post("/run", response_model=AgentResponse)
async def run_agent(req: AgentRequest):
    """
    Ejecuta un agente autónomo de OpenClaw.
    """
    start_time = time.time()
    
    try:
        # Re-inicializar si cambia el modo de swarm (para esta demo rápida de API)
        if req.enable_swarm != agent_client.use_swarm:
            agent_client.use_swarm = req.enable_swarm
            if req.enable_swarm:
                agent_client.swarm = __import__('optimization_core.agents.multi_agentes.swarm_orchestrator', fromlist=['SwarmOrchestrator']).SwarmOrchestrator()
                agent_client._init_default_swarm()
        
        # Añadir herramientas bajo demanda si se solicitan
        if req.tools and not agent_client.use_swarm:
            for tool in req.tools:
                agent_client.add_tool(tool)

        # Ejecutar el agente
        result = await agent_client.run(user_id=req.user_id, prompt=req.prompt)
        
        latency_ms = (time.time() - start_time) * 1000
        return AgentResponse(
            user_id=req.user_id,
            response=result,
            latency_ms=latency_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del agente: {str(e)}")

@router.delete("/memory/{user_id}")
async def clear_agent_memory(user_id: str):
    """Limpia el contexto de memoria del agente para un usuario dado."""
    success = await agent_client.clear_memory(user_id)
    return {"success": success, "message": f"Memoria de {user_id} borrada."}
