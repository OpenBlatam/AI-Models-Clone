"""
Script para verificar imágenes descargadas - Versión Refactorizada
===================================================================
Versión refactorizada usando módulos separados.
"""

import sys
import logging
from instagram_utils import InstagramDownloadChecker

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Función principal."""
    # Perfil a verificar (puede pasarse como argumento)
    if len(sys.argv) > 1:
        profile_name = sys.argv[1]
    else:
        profile_name = "bunnyrose.me"
    
    base_dir = "instagram_downloads"
    
    logger.info(f"Verificando descargas de @{profile_name}")
    logger.info(f"Directorio base: {base_dir}")
    logger.info("")
    
    # Crear checker
    checker = InstagramDownloadChecker(base_dir=base_dir)
    
    # Verificar perfil
    result = checker.check_profile_downloads(profile_name)
    
    if result['exists']:
        logger.info(f"Total de imágenes descargadas: {result['images']}")
        logger.info(f"Resoluciones únicas encontradas: {result['resolutions']}")
        if result['max_resolution']:
            logger.info(f"Resolución máxima: {result['max_resolution']}")
        logger.info(f"Tamaño total: {result['total_size_mb']:.2f} MB")
    else:
        logger.error(f"El perfil @{profile_name} no existe en {base_dir}")


if __name__ == "__main__":
    main()






