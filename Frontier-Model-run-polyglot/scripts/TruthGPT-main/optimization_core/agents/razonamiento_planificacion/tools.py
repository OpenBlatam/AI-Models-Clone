import os
import sys
import asyncio
import subprocess
import logging
import httpx
from typing import Callable, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseTool(ABC):
    """
    Clase base para herramientas automatizadas. 
    Permite que el agente obtenga la descripción automáticamente del docstring.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre único de la herramienta."""
        pass

    @property
    def description(self) -> str:
        """Descripción extraída del docstring para el LLM."""
        return self.__doc__.strip() if self.__doc__ else "No description available."

    @abstractmethod
    async def run(self, arg: str) -> str:
        """Ejecución asíncrona de la herramienta."""
        pass

# --- Herramientas de Sistema ---

class SystemBashTool(BaseTool):
    """
    Ejecuta comandos de terminal de forma segura (bash/shell). 
    Útil para listar archivos, comprobar procesos o leer información del sistema.
    """
    name = "system_bash"

    async def run(self, cmd: str) -> str:
        # Guardrail básico: prevenir comandos destructivos
        forbidden = ["rm ", "format ", "> /dev/", "chmod ", ":(){ :|:& };:"]
        if any(f in cmd.lower() for f in forbidden):
            return "Error: Comando prohibido por políticas de seguridad."
            
        try:
            # Ejecutar en proceso separado
            process = await subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=10)
            return process.decode('utf-8')
        except subprocess.CalledProcessError as e:
            return f"Error al ejecutar: {e.output.decode('utf-8')}"
        except Exception as e:
            return f"Excepción de sistema: {str(e)}"

# --- Herramientas Web ---

class WebSearchTool(BaseTool):
    """
    Realiza una búsqueda web y extrae información relevante. 
    Acepta una consulta (query) y devuelve un resumen de los resultados.
    """
    name = "web_search"

    async def run(self, query: str) -> str:
        # Mock de búsqueda (en prod usar DuckDuckGo API o similar)
        logger.info(f"Buscando en la web: {query}")
        if "bitcoin" in query.lower():
            return "Resumen Web: El precio de Bitcoin sigue volátil, rondando los $60k-$70k USD según los últimos reportes de CoinMarketCap."
        return f"No se encontraron resultados específicos para '{query}'."

class WebReaderTool(BaseTool):
    """
    Lee el contenido textual de una URL específica. 
    Útil para resumir artículos o leer documentación online.
    """
    name = "web_reader"

    async def run(self, url: str) -> str:
        if not url.startswith("http"):
            return "Error: URL inválida."
            
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                response.raise_for_status()
                # Extraer texto básico (en prod usar BeautifulSoup para limpiar)
                return response.text[:2000] # Limitar a los primeros 2000 chars
        except Exception as e:
            return f"Error al leer URL: {str(e)}"

# --- Herramientas de Sistema de Archivos y Código ---

class FileReadTool(BaseTool):
    """
    Lee el contenido de un archivo local.
    Acepta la ruta absoluta o relativa del archivo y devuelve su contenido.
    """
    name = "file_read"

    async def run(self, filepath: str) -> str:
        try:
            if not os.path.exists(filepath):
                return f"Error: El archivo '{filepath}' no existe."
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()[:5000]  # Limitar a 5000 caracteres
        except Exception as e:
            return f"Error al leer archivo: {str(e)}"

class FileWriteTool(BaseTool):
    """
    Escribe contenido en un archivo local.
    Acepta un formato específico: ruta:::contenido
    Ejemplo: /ruta/al/archivo.txt:::Este es el contenido.
    """
    name = "file_write"

    async def run(self, cmd: str) -> str:
        try:
            parts = cmd.split(":::", 1)
            if len(parts) != 2:
                return "Error: Formato inválido. Use 'ruta:::contenido'."
            filepath, content = parts
            filepath = filepath.strip()
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Éxito: Contenido escrito en '{filepath}'."
        except Exception as e:
            return f"Error al escribir archivo: {str(e)}"

class PythonExecutionTool(BaseTool):
    """
    Ejecuta código Python localmente de forma asíncrona.
    Acepta código fuente en Python y devuelve la salida (stdout/stderr).
    """
    name = "python_execute"

    async def run(self, code: str) -> str:
        # Guardrail básico: prevenir código destructivo obvio
        forbidden = ["os.system", "subprocess", "os.remove", "shutil.rmtree"]
        if any(f in code for f in forbidden):
            return "Error: Uso de módulos prohibidos detectado."
            
        try:
            # En producción se debería usar un entorno aislado (e.g. docker)
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-c", code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            output = ""
            if stdout:
                output += stdout.decode()
            if stderr:
                output += "\\nERROR:\\n" + stderr.decode()
            return output[:5000] if output else "Ejecutado sin salida."
        except Exception as e:
            return f"Error en ejecución de Python: {str(e)}"
