"""
Command Executor - Ejecuta comandos reales
==========================================

Ejecuta comandos Python, shell, o llama a APIs.
"""

import asyncio
import logging
import subprocess
import sys
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class CommandExecutor:
    """Ejecutor de comandos reales"""
    
    def __init__(self, timeout: float = 300.0, working_dir: Optional[str] = None):
        self.timeout = timeout
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        self.working_dir.mkdir(parents=True, exist_ok=True)
    
    async def execute(self, command: str, command_type: str = "auto") -> Dict[str, Any]:
        """
        Ejecutar un comando
        
        Args:
            command: Comando a ejecutar
            command_type: Tipo de comando (auto, python, shell, api)
        
        Returns:
            Dict con resultado de ejecución
        """
        start_time = datetime.now()
        
        try:
            # Detectar tipo de comando automáticamente
            if command_type == "auto":
                command_type = self._detect_command_type(command)
            
            logger.info(f"🔨 Executing {command_type} command: {command[:100]}...")
            
            # Ejecutar según el tipo
            if command_type == "python":
                result = await self._execute_python(command)
            elif command_type == "shell":
                result = await self._execute_shell(command)
            elif command_type == "api":
                result = await self._execute_api_call(command)
            else:
                # Por defecto, intentar como Python
                result = await self._execute_python(command)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "output": result,
                "execution_time": execution_time,
                "command_type": command_type
            }
            
        except asyncio.TimeoutError:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Command timeout after {self.timeout}s"
            logger.error(f"⏱️ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "execution_time": execution_time,
                "command_type": command_type
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)
            logger.error(f"❌ Execution error: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "execution_time": execution_time,
                "command_type": command_type
            }
    
    def _detect_command_type(self, command: str) -> str:
        """Detectar tipo de comando automáticamente"""
        command = command.strip()
        
        # Python code
        if command.startswith("python:") or command.startswith("py:"):
            return "python"
        
        # Shell command
        if command.startswith("shell:") or command.startswith("sh:"):
            return "shell"
        
        # API call
        if command.startswith("http://") or command.startswith("https://"):
            return "api"
        
        # Si contiene imports o es código Python
        if any(keyword in command for keyword in ["import ", "def ", "class ", "print(", "="]):
            return "python"
        
        # Por defecto shell
        return "shell"
    
    async def _execute_python(self, code: str) -> str:
        """Ejecutar código Python"""
        # Limpiar prefijos
        code = code.replace("python:", "").replace("py:", "").strip()
        
        # Crear script temporal
        script_file = self.working_dir / f"temp_script_{datetime.now().timestamp()}.py"
        
        try:
            # Escribir código
            script_file.write_text(code, encoding='utf-8')
            
            # Ejecutar
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(script_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.working_dir)
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )
            
            # Limpiar archivo
            if script_file.exists():
                script_file.unlink()
            
            if process.returncode != 0:
                error_output = stderr.decode('utf-8', errors='ignore')
                raise Exception(f"Python execution failed: {error_output}")
            
            return stdout.decode('utf-8', errors='ignore')
            
        except Exception as e:
            # Limpiar archivo en caso de error
            if script_file.exists():
                script_file.unlink()
            raise
    
    async def _execute_shell(self, command: str) -> str:
        """Ejecutar comando shell"""
        # Limpiar prefijos
        command = command.replace("shell:", "").replace("sh:", "").strip()
        
        # Determinar shell según OS
        if sys.platform == "win32":
            shell_cmd = ["cmd", "/c", command]
        else:
            shell_cmd = ["/bin/bash", "-c", command]
        
        process = await asyncio.create_subprocess_exec(
            *shell_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(self.working_dir)
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=self.timeout
        )
        
        if process.returncode != 0:
            error_output = stderr.decode('utf-8', errors='ignore')
            raise Exception(f"Shell execution failed: {error_output}")
        
        return stdout.decode('utf-8', errors='ignore')
    
    async def _execute_api_call(self, url: str) -> str:
        """Ejecutar llamada API"""
        try:
            import httpx
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
                
        except ImportError:
            # Fallback a requests si httpx no está disponible
            import requests
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text



