"""
Script para limpiar folders de descarga de Instagram - Versión Refactorizada
============================================================================
Versión refactorizada usando módulos separados.
"""

import sys
import logging
from instagram_utils import InstagramFolderCleaner

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Función principal."""
    if len(sys.argv) < 2:
        logger.error("Uso: python clean_instagram_folder_refactored.py <ruta_al_folder> [--no-recursive]")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    recursive = '--no-recursive' not in sys.argv
    
    # Crear limpiador
    cleaner = InstagramFolderCleaner()
    
    # Limpiar folder
    stats = cleaner.clean_folder(folder_path, recursive=recursive)
    
    logger.info("")
    logger.info(f"Estadísticas finales: {stats}")


if __name__ == "__main__":
    main()






