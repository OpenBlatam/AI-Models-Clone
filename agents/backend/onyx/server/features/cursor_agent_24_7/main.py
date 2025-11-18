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
from typing import Optional

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
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )

logger = logging.getLogger(__name__)


async def run_service() -> None:
    """
    Ejecutar como servicio persistente.
    
    Raises:
        RuntimeError: Si hay error al iniciar el servicio.
    """
    config = AgentConfig(
        persistent_storage=True,
        auto_restart=True
    )
    
    agent = CursorAgent(config)
    service = PersistentService(agent)
    
    logger.info("🚀 Starting Cursor Agent 24/7 as persistent service...")
    try:
        await service.run()
    except Exception as e:
        logger.error(f"Service error: {e}", exc_info=True)
        raise RuntimeError(f"Failed to run service: {e}") from e


async def run_api(host: str = "0.0.0.0", port: int = 8024) -> None:
    """
    Ejecutar API REST.
    
    Args:
        host: Host para el servidor (default: "0.0.0.0").
        port: Puerto para el servidor (default: 8024).
    
    Raises:
        RuntimeError: Si hay error al iniciar la API.
        ValueError: Si el puerto es inválido.
    """
    if not (1 <= port <= 65535):
        raise ValueError(f"Invalid port: {port}. Must be between 1 and 65535")
    
    config = AgentConfig(
        persistent_storage=True,
        auto_restart=True
    )
    
    agent = CursorAgent(config)
    api = AgentAPI(agent, host=host, port=port)
    
    logger.info(f"🌐 Starting API server on http://{host}:{port}")
    try:
        await api.run()
    except Exception as e:
        logger.error(f"API error: {e}", exc_info=True)
        raise RuntimeError(f"Failed to run API: {e}") from e


def main() -> None:
    """
    Función principal del agente.
    
    Parsea argumentos de línea de comandos e inicia el agente en el modo
    especificado (service o api).
    """
    parser = argparse.ArgumentParser(
        description="Cursor Agent 24/7 - Agente persistente para ejecutar comandos",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--mode",
        choices=["service", "api"],
        default="api",
        help="Modo de ejecución: service (servicio persistente) o api (API REST)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host para API (solo modo api, default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8024,
        help="Puerto para API (solo modo api, default: 8024)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "service":
            asyncio.run(run_service())
        else:
            asyncio.run(run_api(host=args.host, port=args.port))
                
    except KeyboardInterrupt:
        logger.info("⛔ Interrupted by user")
        sys.exit(0)
    except ValueError as e:
        logger.error(f"❌ Invalid argument: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

