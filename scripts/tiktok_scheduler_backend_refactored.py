"""
TikTok Scheduler Backend - Versión Refactorizada
=================================================
Backend refactorizado para autenticación OAuth de TikTok y programación automática de posts.

Refactorización aplicada:
- Separación de responsabilidades (SRP)
- Eliminación de duplicación (DRY)
- Módulos independientes y reutilizables
- Mejor mantenibilidad y testabilidad
"""

import logging
from pathlib import Path

from tiktok_scheduler.routes import create_app
from tiktok_scheduler.config import Config

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Función principal."""
    logger.info("Iniciando servidor TikTok Scheduler (Refactorizado)...")
    
    # Validar configuración
    is_valid, error = Config.validate()
    if not is_valid:
        logger.warning(f"⚠️  ADVERTENCIA: {error}")
        if error == "TIKTOK_CLIENT_KEY no configurado":
            logger.warning("   Crea un archivo 'tiktok_config.py' o configura variables de entorno")
    
    # Log de configuración
    logger.info(f"Contenido en: {Config.CONTENT_DIR}")
    logger.info(f"Videos en: {Config.VIDEOS_DIR}")
    logger.info(f"Usando videos: {Config.USE_VIDEOS}")
    logger.info(f"Cuenta objetivo: @{Config.TARGET_USERNAME}")
    
    # Crear y ejecutar aplicación
    app = create_app()
    
    logger.info(f"Servidor iniciado en http://{Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)


if __name__ == '__main__':
    main()







