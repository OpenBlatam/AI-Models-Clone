"""
Script para verificar todas las descargas - Versión Refactorizada
==================================================================
Versión refactorizada usando módulos separados.
"""

import logging
from instagram_utils import InstagramDownloadChecker

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Función principal."""
    base_dir = "instagram_downloads"
    profiles = ["bunnyrose.uwu", "bunnyy.rose_", "bunnyrose.x"]
    
    logger.info(f"Verificando descargas en: {base_dir}")
    logger.info(f"Perfiles a verificar: {len(profiles)}")
    logger.info("")
    
    # Crear checker
    checker = InstagramDownloadChecker(base_dir=base_dir)
    
    # Verificar todos los perfiles
    results = checker.check_all_profiles(profiles)
    
    # Imprimir resumen
    checker.print_summary(results)


if __name__ == "__main__":
    main()






