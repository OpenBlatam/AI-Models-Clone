"""
Cursor Agent 24/7 - Main Entry Point
=====================================

Punto de entrada principal para el agente persistente.
"""

import asyncio
import logging
import sys
import argparse
from pathlib import Path

from .core.agent import CursorAgent, AgentConfig
from .core.persistent_service import PersistentService
from .api.agent_api import AgentAPI

# Setup logging avanzado
try:
    from .core.logger_config import setup_logging
    log_file = Path(__file__).parent / "logs" / "agent.log"
    setup_logging(
        log_level="INFO",
        log_file=str(log_file),
        use_json=False,
        use_colors=True
    )
except ImportError:
    # Fallback a logging básico
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )

logger = logging.getLogger(__name__)


async def run_service():
    """Ejecutar como servicio persistente"""
    config = AgentConfig(
        persistent_storage=True,
        auto_restart=True
    )
    
    agent = CursorAgent(config)
    service = PersistentService(agent)
    
    logger.info("🚀 Starting Cursor Agent 24/7 as persistent service...")
    await service.run()


async def run_api():
    """Ejecutar API REST"""
    parser = argparse.ArgumentParser(description="Cursor Agent 24/7 API")
    parser.add_argument("--host", default="0.0.0.0", help="Host para el servidor")
    parser.add_argument("--port", type=int, default=8024, help="Puerto para el servidor")
    args = parser.parse_args()
    
    config = AgentConfig(
        persistent_storage=True,
        auto_restart=True
    )
    
    agent = CursorAgent(config)
    api = AgentAPI(agent, host=args.host, port=args.port)
    
    logger.info(f"🌐 Starting API server on http://{args.host}:{args.port}")
    await api.run()


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Cursor Agent 24/7")
    parser.add_argument(
        "--mode",
        choices=["service", "api"],
        default="api",
        help="Modo de ejecución: service (servicio persistente) o api (API REST)"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host para API (solo modo api)")
    parser.add_argument("--port", type=int, default=8024, help="Puerto para API (solo modo api)")
    
    args = parser.parse_args()
    
    try:
        if args.mode == "service":
            asyncio.run(run_service())
        else:
            # Modificar sys.argv para pasar host y port a run_api
            import sys
            original_argv = sys.argv
            sys.argv = ["main.py", "--host", args.host, "--port", str(args.port)]
            try:
                asyncio.run(run_api())
            finally:
                sys.argv = original_argv
                
    except KeyboardInterrupt:
        logger.info("⛔ Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

