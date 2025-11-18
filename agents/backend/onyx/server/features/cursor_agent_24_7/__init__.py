"""
Cursor Agent 24/7
=================

Agente persistente que escucha comandos desde Cursor y los ejecuta
continuamente, incluso cuando la computadora está apagada (como servicio).

Características:
- Escucha comandos desde la ventana de Cursor
- Ejecuta tareas de forma continua sin parar
- Control simple con botón de start/stop
- Servicio persistente que puede correr en background
"""

__version__ = "1.0.0"
__author__ = "Blatam Academy"

from .core.agent import CursorAgent
from .core.task_executor import TaskExecutor
from .api.agent_api import AgentAPI

__all__ = [
    "CursorAgent",
    "TaskExecutor",
    "AgentAPI",
]



