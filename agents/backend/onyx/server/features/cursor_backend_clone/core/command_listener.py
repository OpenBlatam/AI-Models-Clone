"""
Command Listener - Escucha comandos desde Cursor
=================================================

Escucha comandos desde la ventana de Cursor y los envía al agente.
"""

import asyncio
import logging
from typing import Optional, Callable, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CommandListener:
    """Escucha comandos desde Cursor"""
    
    def __init__(self, callback: Optional[Callable] = None):
        self.callback = callback
        self.running = False
        self._listen_task: Optional[asyncio.Task] = None
        self._cursor_api_client = None
        
    async def start(self) -> None:
        """Iniciar listener"""
        if self.running:
            logger.warning("Listener is already running")
            return
            
        logger.info("👂 Starting command listener...")
        self.running = True
        
        # Inicializar cliente de Cursor API
        # TODO: Inicializar cliente real de Cursor API
        # self._cursor_api_client = CursorAPIClient()
        
        self._listen_task = asyncio.create_task(self._listen_loop())
        
    async def stop(self) -> None:
        """Detener listener"""
        if not self.running:
            return
            
        logger.info("🛑 Stopping command listener...")
        self.running = False
        
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
                
    async def _listen_loop(self) -> None:
        """Loop principal de escucha"""
        while self.running:
            try:
                # TODO: Integrar con Cursor API
                # Por ahora, simulamos escuchando comandos
                
                # Ejemplo de integración:
                # command = await self._cursor_api_client.get_next_command()
                # if command:
                #     await self._handle_command(command)
                
                await asyncio.sleep(1.0)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in listen loop: {e}")
                await asyncio.sleep(5)
                
    async def _handle_command(self, command: str) -> None:
        """Manejar comando recibido"""
        logger.info(f"📨 Command received: {command[:50]}...")
        
        if self.callback:
            try:
                if asyncio.iscoroutinefunction(self.callback):
                    await self.callback(command)
                else:
                    self.callback(command)
            except Exception as e:
                logger.error(f"Error in command callback: {e}")


