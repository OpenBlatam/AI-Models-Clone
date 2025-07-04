#!/usr/bin/env python3
"""
Start Production Script - LinkedIn Posts Ultra Optimized
=======================================================

Script para iniciar el sistema ultra optimizado en producción.
"""

import asyncio
import os
import sys
import signal
import logging
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import ultra fast components
from optimized_core.ultra_fast_engine import UltraFastEngine, get_ultra_fast_engine
from optimized_core.ultra_fast_api import UltraFastAPI, app
import uvicorn


class ProductionRunner:
    """Runner para producción ultra optimizado."""
    
    def __init__(self):
        self.engine = None
        self.api = None
        self.server = None
        self.shutdown_event = asyncio.Event()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/app/logs/production.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Inicializar sistema para producción."""
        self.logger.info("🚀 Inicializando Sistema de Producción Ultra Optimizado...")
        
        try:
            # Initialize engine
            self.engine = await get_ultra_fast_engine()
            self.logger.info("✅ Motor Ultra Rápido inicializado")
            
            # Initialize API
            self.api = UltraFastAPI()
            self.logger.info("✅ API Ultra Rápida inicializada")
            
            # Health check
            health = await self.engine.health_check()
            self.logger.info(f"✅ Health check: {health}")
            
            self.logger.info("🎉 Sistema de Producción listo!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en inicialización: {e}")
            return False
    
    async def start_server(self):
        """Iniciar servidor de producción."""
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=8000,
            loop="asyncio",
            workers=4,
            log_level="info",
            access_log=True,
            reload=False,
            server_header=False,
            date_header=False,
            forwarded_allow_ips="*"
        )
        
        self.server = uvicorn.Server(config)
        await self.server.serve()
    
    async def shutdown(self):
        """Apagar sistema de producción."""
        self.logger.info("🛑 Apagando sistema de producción...")
        
        if self.server:
            self.server.should_exit = True
        
        self.shutdown_event.set()
        
        self.logger.info("✅ Sistema apagado correctamente")
    
    def signal_handler(self, signum, frame):
        """Manejador de señales para apagado graceful."""
        self.logger.info(f"📡 Señal recibida: {signum}")
        asyncio.create_task(self.shutdown())
    
    async def run(self):
        """Ejecutar sistema de producción."""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Initialize system
        if not await self.initialize():
            sys.exit(1)
        
        try:
            # Start server
            await self.start_server()
        except Exception as e:
            self.logger.error(f"❌ Error en servidor: {e}")
            sys.exit(1)
        finally:
            await self.shutdown()


async def main():
    """Función principal."""
    runner = ProductionRunner()
    await runner.run()


if __name__ == "__main__":
    # Set up asyncio with uvloop if available
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        print("🚀 Usando uvloop para máxima performance")
    except ImportError:
        print("⚠️  uvloop no disponible, usando event loop estándar")
    
    # Run production system
    asyncio.run(main()) 