import logging
import re
import asyncio
from typing import List, Dict, Any, Callable, Protocol, Optional, runtime_checkable, Type

# Contexto de imports
try:
    from agents.memoria_aprendizaje.sqlite_memory import SQLiteMemory, BaseMemory
    from agents.memoria_aprendizaje.vector_memory import VectorMemory
    from agents.razonamiento_planificacion.tools import BaseTool
    from agents.razonamiento_planificacion.config import settings
except ImportError:
    from ..memoria_aprendizaje.sqlite_memory import SQLiteMemory, BaseMemory
    from ..memoria_aprendizaje.vector_memory import VectorMemory
    from ..memoria_aprendizaje.core_memory import CoreMemory
    from ..memoria_aprendizaje.core_memory_tools import CoreMemoryAppendTool, CoreMemoryReplaceTool
    from .tools import BaseTool, ToolResult, MCPTool
    from .models import AgentAction, AgentResponse
    from .config import settings
    from .mcp_client import MCPClient

try:
    from agents.observability import global_tracer
except ImportError:
    from ..observability import global_tracer

logger = logging.getLogger(__name__)

from .models import AgentAction, AgentResponse, InferenceResult

@runtime_checkable
class AsyncLLMEngine(Protocol):
    """Protocolo para un motor de inferencia LLM asíncrono."""
    async def __call__(self, prompt: str) -> Union[str, InferenceResult]:
        ...

from pydantic import BaseModel, Field

class AgentAction(BaseModel):
    tool: Optional[str] = Field(None, description="Nombre de la herramienta a usar. Null si respondes al usuario final.")
    cmd: Optional[str] = Field(None, description="Argumento o comando a enviar a la herramienta.")
    respuesta_final: Optional[str] = Field(None, description="Tu mensaje final dirigido al usuario usando Markdown. Null si usas una herramienta.")
    handoff: Optional[str] = Field(None, description="[OPCIONAL] Nombre del agente experto al que quieres transferir la conversación si tú no puedes resolver la petición.")

class MultiUserReActAgent:
    """
    Orquestador ReAct Multi-Usuario de Grado Empresarial.
    Gestión asíncrona de bucles de razonamiento e integración Pydantic (JSON).
    """

    def __init__(
        self, 
        llm_engine: AsyncLLMEngine, 
        memory: Optional[BaseMemory] = None,
        vector_memory: Optional[VectorMemory] = None,
        memory_db_path: Optional[str] = None,
        custom_system_instructions: Optional[str] = None,
        use_reflexion: bool = False,
        tools: Optional[List[BaseTool]] = None
    ):
        self.llm = llm_engine
        self.memory = memory or SQLiteMemory(db_path=memory_db_path or settings.DATABASE_PATH)
        self.vector_memory = vector_memory or VectorMemory()
        self.core_memory = CoreMemory()
        self.tools: Dict[str, BaseTool] = {}
        self.custom_system_instructions = custom_system_instructions
        self.use_reflexion = use_reflexion
        self.name = "MultiUserReActAgent"

        if tools:
            for tool in tools:
                self.register_tool(tool)
        
        # Add memory self-update tools
        self.register_tool(CoreMemoryAppendTool(self.core_memory))
        self.register_tool(CoreMemoryReplaceTool(self.core_memory))

    def register_tool(self, tool: BaseTool) -> None:
        """Registra una herramienta disponible para el agente."""
        self.tools[tool.name] = tool
        logger.info(f"Agente {self.name}: Herramienta '{tool.name}' registrada.")

    async def load_mcp_tools(self, server_url: str):
        """
        Descubre y registra dinámicamente herramientas desde un servidor MCP.
        """
        logger.info(f"Cargando herramientas MCP desde {server_url}...")
        client = MCPClient(server_url)
        tools_info = await client.list_tools()
        
        for t_info in tools_info:
            mcp_tool = MCPTool(client, t_info)
            self.register_tool(mcp_tool)
        
        logger.info(f"Se cargaron {len(tools_info)} herramientas MCP.")

    def _get_system_instructions(self) -> str:
        """Genera instrucciones dinámicas basadas en las herramientas registradas."""
        tools_desc = "\n".join([f"- {t.name}: {t.description}" for t in self.tools.values()])
        base_instructions = settings.SYSTEM_PROMPT_TEMPLATE.format(name=settings.AGENT_NAME)
        
        if self.custom_system_instructions:
            base_instructions += f"\n\n{self.custom_system_instructions}"
            
        return base_instructions + (
            f"\nTienes acceso a estas herramientas:\n{tools_desc}\n\n"
            "IMPORTANTE: Debes responder ÚNICA y EXCLUSIVAMENTE con un JSON puro que cumpla estrictamente este esquema Pydantic:\n"
            f"{AgentAction.model_json_schema()}\n"
            "No incluyas NADA de texto fuera del JSON, ni siquiera tildes invertidas ```json."
        )

    async def _format_context(self, user_id: str) -> str:
        history = await self.memory.get_history(user_id)
        if not history:
            return f"--- MEMORIA PRIVADA ({user_id}) ---\nSin historial previo.\n"
        
        context = f"--- MEMORIA PRIVADA ({user_id}) ---\n"
        for msg in history:
            context += f"{msg['role'].upper()}: {msg['content']}\n"
        context += "--------------------------------------\n"
        return context

    async def process_message(self, user_id: str, message: str) -> AgentResponse:
        """
        Procesa un mensaje de forma asíncrona aislando el contexto por usuario.
        """
        logger.info(f"Iniciando proceso asíncrono para {user_id}")
        await self.memory.add_message(user_id, "user", message)
        
        system_prompt = self._get_system_instructions()
        user_context = await self._format_context(user_id)
        
        # Inject Long-Term RAG Context
        if self.vector_memory and self.vector_memory.enabled:
            rag_context = await self.vector_memory.get_context_for_prompt(message, user_id)
            if rag_context:
                user_context += f"\n{rag_context}\n"
        
        core_context = await self.core_memory.get_formatted_context(user_id)
        system_prompt = f"{system_prompt}\n{core_context}"
        
        current_prompt = f"{system_prompt}\n{user_context}\nUSER: {message}\nTRUTHGPT: "
        
        # Iniciar traza de observabilidad
        trace_id = global_tracer.start_trace(name="process_message", agent_name="MultiUserReActAgent")
        
        # Resilient LLM call using Tenacity
        try:
            from tenacity import retry, wait_exponential, stop_after_attempt
            @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3), reraise=True)
            async def _safe_llm_call(prompt: str) -> str:
                span = global_tracer.start_span(trace_id, name="llm_inference", kind="llm_call", input_data=prompt[-500:])
                try:
                    res = await self.llm(prompt)
                    # Handle both raw string and InferenceResult
                    res_text = res.text if hasattr(res, 'text') else str(res)
                    span.finish(output=res_text)
                    return res_text
                except Exception as e:
                    span.finish(output=str(e), status="error")
                    raise e
        except ImportError:
            logger.warning("Instala 'tenacity' para reintentos automáticos (exponential backoff).")
            async def _safe_llm_call(prompt: str) -> str:
                span = global_tracer.start_span(trace_id, name="llm_inference", kind="llm_call", input_data=prompt[-500:])
                try:
                    res = await self.llm(prompt)
                    res_text = res.text if hasattr(res, 'text') else str(res)
                    span.finish(output=res_text)
                    return res_text
                except Exception as e:
                    span.finish(output=str(e), status="error")
                    raise e
        
        for i in range(settings.MAX_ITERATIONS):
            # Inferencia asíncrona robusta (con reintentos)
            response = await _safe_llm_call(current_prompt)
            
            try:
                import json
                clean_resp = response.strip()
                if clean_resp.startswith("```json"):
                    clean_resp = clean_resp[7:-3].strip()
                elif clean_resp.startswith("```"):
                    clean_resp = clean_resp[3:-3].strip()
                    
                action = AgentAction.model_validate_json(clean_resp)
                
                if action.tool:
                    if action.tool in self.tools:
                        tool_instance = self.tools[action.tool]
                        if tool_instance.requires_approval:
                            logger.info(f"HITL PAUSE: Require aprobación para {action.tool}")
                            # Guardamos la intención en memoria
                            await self.memory.add_message(user_id, "assistant", clean_resp)
                            await self.memory.add_message(user_id, "assistant", f"⏳ Esperando aprobación manual para ejecutar: {action.tool}")
                            return AgentResponse(
                                content=f"⏳ Esperando aprobación para: {action.tool}",
                                action_type="approval_required",
                                metadata={"tool": action.tool, "cmd": action.cmd}
                            )
                            
                        logger.info(f"Ejecutando {action.tool} asíncronamente...")
                        result = await self._execute_tool_action(trace_id, action, user_id)
                    else:
                        result = f"Error: La herramienta '{action.tool}' no existe."
                    current_prompt += f"{clean_resp}\nTOOL_RESULT: {result}\nTRUTHGPT: "
                    
                elif action.respuesta_final:
                    # Llegamos a la respuesta final
                    if self.use_reflexion:
                        logger.info("Auto-Reflexion: Evaluando respuesta interna...")
                        critique_prompt = (
                            f"{current_prompt}\n{clean_resp}\n"
                            "[SISTEMA INTERNO]: Evalúa críticamente tu respuesta anterior frente a la petición. "
                            "¿Resuelve completamente el problema o la pregunta? "
                            "Si la respuesta es perfecta y sin errores, responde EXACTAMENTE '<final>APROBADO</final>'. "
                            "Si falta información o hubo un error, escribe tu crítica y planifica el siguiente paso (puedes usar herramientas de nuevo)."
                        )
                        critique_response = await _safe_llm_call(critique_prompt)
                        
                        if "<final>APROBADO</final>" in critique_response:
                            logger.info("Auto-Reflexion: Aprobado.")
                            if self.vector_memory and self.vector_memory.enabled:
                                await self.vector_memory.add_episodic(user_id, "ReActAgent", f"User: {message}\nSuccess: {action.respuesta_final}")
                                asyncio.create_task(self.vector_memory.compact_episodic_memory(user_id, _safe_llm_call))
                            
                            await self.memory.add_message(user_id, "assistant", action.respuesta_final)
                            global_tracer.finish_trace(trace_id)
                            return AgentResponse(content=action.respuesta_final, action_type="final_answer")
                        else:
                            logger.info("Auto-Reflexion: Crítica detectó áreas de mejora. Reintentando...")
                            current_prompt = f"{critique_prompt}\n{critique_response}\nTRUTHGPT: "
                    else:
                        if self.vector_memory and self.vector_memory.enabled:
                            await self.vector_memory.add_episodic(user_id, "ReActAgent", f"User: {message}\nAnswer: {action.respuesta_final}")
                            asyncio.create_task(self.vector_memory.compact_episodic_memory(user_id, _safe_llm_call))
                        await self.memory.add_message(user_id, "assistant", action.respuesta_final)
                        return AgentResponse(content=action.respuesta_final, action_type="final_answer")
                elif action.handoff:
                    logger.info(f"Iniciando Swarm Handoff hacia: {action.handoff}")
                    await self.memory.add_message(user_id, "assistant", f"Transferring control to {action.handoff}...")
                    return AgentResponse(
                        content=f"Transferring to {action.handoff}...",
                        action_type="handoff",
                        handoff_target=action.handoff
                    )
                else:
                    raise ValueError("Debes proveer 'tool', 'respuesta_final' o 'handoff' en tu JSON.")
                    
            except Exception as e:
                logger.warning(f"Error parseando Pydantic JSON: {e}")
                current_prompt += f"\n[ERROR DE SISTEMA]: Tu respuesta violó el esquema JSON obligatorio. Detalle: {str(e)}\nCorrige y responde solo en JSON.\nTRUTHGPT: "
        
        fallback = "Límite de razonamiento alcanzado. Por favor, simplifica tu petición."
        await self.memory.add_message(user_id, "assistant", fallback)
        global_tracer.finish_trace(trace_id)
        return AgentResponse(content=fallback, action_type="final_answer")

    from typing import AsyncIterator
    
    async def astream_process_message(self, user_id: str, message: str) -> 'AsyncIterator[str]':
        """
        Procesa un mensaje de forma asíncrona y hace yield de los pasos (Streaming / SSE).
        Emite JSON strings que representan eventos o estados parciales.
        """
        import json
        logger.info(f"Iniciando proceso STREAMING para {user_id}")
        await self.memory.add_message(user_id, "user", message)
        
        system_prompt = self._get_system_instructions()
        user_context = await self._format_context(user_id)
        
        # Inject Long-Term RAG Context
        if self.vector_memory and self.vector_memory.enabled:
            rag_context = await self.vector_memory.get_context_for_prompt(message, user_id)
            if rag_context:
                user_context += f"\n{rag_context}\n"
        
        core_context = await self.core_memory.get_formatted_context(user_id)
        system_prompt = f"{system_prompt}\n{core_context}"
                
        current_prompt = f"{system_prompt}\n{user_context}\nUSER: {message}\nTRUTHGPT: "
        
        trace_id = global_tracer.start_trace(name="astream_process", agent_name="MultiUserReActAgent")
        
        try:
            from tenacity import retry, wait_exponential, stop_after_attempt
            @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3), reraise=True)
            async def _safe_llm_call(prompt: str) -> str:
                span = global_tracer.start_span(trace_id, name="llm_inference", kind="llm_call", input_data=prompt[-500:])
                try:
                    res = await self.llm(prompt)
                    res_text = res.text if hasattr(res, 'text') else str(res)
                    span.finish(output=res_text)
                    return res_text
                except Exception as e:
                    span.finish(output=str(e), status="error")
                    raise e
        except ImportError:
            async def _safe_llm_call(prompt: str) -> str:
                span = global_tracer.start_span(trace_id, name="llm_inference", kind="llm_call", input_data=prompt[-500:])
                try:
                    res = await self.llm(prompt)
                    res_text = res.text if hasattr(res, 'text') else str(res)
                    span.finish(output=res_text)
                    return res_text
                except Exception as e:
                    span.finish(output=str(e), status="error")
                    raise e
        
        for i in range(settings.MAX_ITERATIONS):
            yield json.dumps({"event": "thinking", "iteration": i+1}) + "\n"
            
            response = await _safe_llm_call(current_prompt)
            
            try:
                clean_resp = response.strip()
                if clean_resp.startswith("```json"):
                    clean_resp = clean_resp[7:-3].strip()
                elif clean_resp.startswith("```"):
                    clean_resp = clean_resp[3:-3].strip()
                    
                action = AgentAction.model_validate_json(clean_resp)
                
                if action.tool:
                    if action.tool in self.tools:
                        tool_instance = self.tools[action.tool]
                        if tool_instance.requires_approval:
                            logger.info(f"STREAMING HITL PAUSE: Require aprobación para {action.tool}")
                            yield json.dumps({"event": "requires_approval", "tool": action.tool, "cmd": action.cmd}) + "\n"
                            
                            # Guardamos la intención en memoria
                            await self.memory.add_message(user_id, "assistant", clean_resp)
                            approval_msg = f"<WAITING_FOR_APPROVAL tool='{action.tool}' cmd='{action.cmd}'/>"
                            await self.memory.add_message(user_id, "assistant", f"⏳ Esperando aprobación manual para ejecutar: {action.tool}")
                            yield json.dumps({"event": "final_answer", "content": approval_msg}) + "\n"
                            return
                            
                        yield json.dumps({"event": "tool_call", "tool": action.tool, "cmd": action.cmd}) + "\n"
                        result = await self._execute_tool_action(trace_id, action, user_id)
                    else:
                        yield json.dumps({"event": "tool_call", "tool": action.tool, "cmd": action.cmd}) + "\n"
                        result = f"Error: La herramienta '{action.tool}' no existe."
                    
                    yield json.dumps({"event": "tool_result", "tool": action.tool, "result": str(result)[:200] + "..."}) + "\n"
                    current_prompt += f"{clean_resp}\nTOOL_RESULT: {result}\nTRUTHGPT: "
                    
                elif action.respuesta_final:
                    if self.use_reflexion:
                        yield json.dumps({"event": "reflexion", "status": "evaluating"}) + "\n"
                        critique_prompt = (
                            f"{current_prompt}\n{clean_resp}\n"
                            "[SISTEMA INTERNO]: Evalúa críticamente tu respuesta anterior frente a la petición. "
                            "¿Resuelve completamente el problema o la pregunta? "
                            "Si la respuesta es perfecta y sin errores, responde EXACTAMENTE '<final>APROBADO</final>'. "
                            "Si falta información o hubo un error, escribe tu crítica y planifica el siguiente paso (puedes usar herramientas de nuevo)."
                        )
                        critique_response = await _safe_llm_call(critique_prompt)
                        
                        if "<final>APROBADO</final>" in critique_response:
                            yield json.dumps({"event": "reflexion_approved"}) + "\n"
                            if self.vector_memory and self.vector_memory.enabled:
                                await self.vector_memory.add_episodic(user_id, "ReActAgent", f"User: {message}\nSuccess: {action.respuesta_final}")
                                asyncio.create_task(self.vector_memory.compact_episodic_memory(user_id, _safe_llm_call))
                            await self.memory.add_message(user_id, "assistant", action.respuesta_final)
                            yield json.dumps({"event": "final_answer", "content": action.respuesta_final}) + "\n"
                            global_tracer.finish_trace(trace_id)
                            return
                        else:
                            yield json.dumps({"event": "reflexion_rejected", "critique": critique_response}) + "\n"
                            current_prompt = f"{critique_prompt}\n{critique_response}\nTRUTHGPT: "
                    else:
                        if self.vector_memory and self.vector_memory.enabled:
                            await self.vector_memory.add_episodic(user_id, "ReActAgent", f"User: {message}\nAnswer: {action.respuesta_final}")
                            asyncio.create_task(self.vector_memory.compact_episodic_memory(user_id, _safe_llm_call))
                        await self.memory.add_message(user_id, "assistant", action.respuesta_final)
                        yield json.dumps({"event": "final_answer", "content": action.respuesta_final}) + "\n"
                        return
                elif action.handoff:
                    logger.info(f"STREAMING: Iniciando Swarm Handoff hacia: {action.handoff}")
                    yield json.dumps({"event": "handoff", "target": action.handoff}) + "\n"
                    handoff_msg = f"<HANDOFF target='{action.handoff}'/>"
                    await self.memory.add_message(user_id, "assistant", f"Transferring control to {action.handoff}...")
                    yield json.dumps({"event": "final_answer", "content": handoff_msg}) + "\n"
                    return
                else:
                    raise ValueError("Debes proveer 'tool', 'respuesta_final' o 'handoff' en tu JSON.")
                    
            except Exception as e:
                logger.warning(f"Error parseando Pydantic JSON: {e}")
                yield json.dumps({"event": "error", "message": f"Syntax error recovering: {str(e)}"}) + "\n"
                current_prompt += f"\n[ERROR DE SISTEMA]: Tu respuesta violó el esquema JSON obligatorio. Detalle: {str(e)}\nCorrige y responde solo en JSON.\nTRUTHGPT: "
        
        fallback = "Límite de razonamiento alcanzado. Por favor, simplifica tu petición."
        await self.memory.add_message(user_id, "assistant", fallback)
        yield json.dumps({"event": "error", "message": fallback}) + "\n"
        global_tracer.finish_trace(trace_id)

    async def _execute_tool_action(self, trace_id: str, action: AgentAction, user_id: str) -> str:
        """Helper para ejecutar una herramienta y manejar señales internas (Core Memory)."""
        tool_instance = self.tools[action.tool]
        tool_span = global_tracer.start_span(trace_id, name=action.tool, kind="tool_call", input_data=action.cmd)
        
        try:
            raw_result = await tool_instance.run(action.cmd or "")
            
            # Handle ToolResult signals
            if isinstance(raw_result, ToolResult):
                result_str = raw_result.output
                if raw_result.signal == "core_memory_append":
                    block = raw_result.metadata.get("block")
                    content = raw_result.metadata.get("content")
                    await self.core_memory.append_to_block(user_id, block, content)
                    result_str = f"SYSTEM: Memoria CORE ({block}) actualizada."
                elif raw_result.signal == "core_memory_replace":
                    block = raw_result.metadata.get("block")
                    content = raw_result.metadata.get("content")
                    await self.core_memory.update_block(user_id, block, content)
                    result_str = f"SYSTEM: Memoria CORE ({block}) remplazada totalmente."
            else:
                result_str = str(raw_result)
                
            tool_span.finish(output=result_str)
            return result_str
            
        except Exception as e:
            logger.error(f"Error ejecutando {action.tool}: {e}")
            tool_span.finish(output=str(e), status="error")
            return f"Error: {str(e)}"
