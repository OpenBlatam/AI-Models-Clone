"""
Task Executor - Ejecutor de tareas
===================================

Ejecuta comandos recibidos desde Cursor.
"""

import asyncio
import logging
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Estados de una tarea"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionResult:
    """Resultado de ejecución de tarea"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0


class TaskExecutor:
    """Ejecutor de tareas"""
    
    def __init__(self, timeout: float = 300.0):
        self.timeout = timeout
        self.active_executions: Dict[str, asyncio.Task] = {}
        
    async def execute(self, command: str, task_id: str) -> ExecutionResult:
        """Ejecutar un comando"""
        start_time = datetime.now()
        
        try:
            logger.info(f"🔨 Executing command: {command[:100]}...")
            
            # Ejecutar comando con timeout
            result = await asyncio.wait_for(
                self._run_command(command),
                timeout=self.timeout
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ExecutionResult(
                success=True,
                output=result,
                execution_time=execution_time
            )
            
        except asyncio.TimeoutError:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Task timeout after {self.timeout}s"
            logger.error(f"⏱️ {error_msg}")
            return ExecutionResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)
            logger.error(f"❌ Execution error: {error_msg}")
            return ExecutionResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
            
    async def _run_command(self, command: str) -> str:
        """Ejecutar comando real"""
        from .command_executor import CommandExecutor
        
        executor = CommandExecutor(timeout=self.timeout)
        result = await executor.execute(command)
        
        if result["success"]:
            return result["output"]
        else:
            raise Exception(result.get("error", "Unknown error"))
        
    async def cancel(self, task_id: str) -> bool:
        """Cancelar una tarea en ejecución"""
        if task_id in self.active_executions:
            task = self.active_executions[task_id]
            task.cancel()
            del self.active_executions[task_id]
            logger.info(f"🚫 Task cancelled: {task_id}")
            return True
        return False

