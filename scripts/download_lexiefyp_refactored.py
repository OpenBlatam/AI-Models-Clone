"""
Script específico para descargar imágenes y videos de @lexiefyp - Versión Refactorizada
=========================================================================================
Versión refactorizada usando módulos separados.
"""

import sys
import os
import logging
from pathlib import Path

# Agregar el directorio scripts al path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

# Importar módulos refactorizados
try:
    from download_instagram_images_refactored import InstagramDownloader
    from instagram_utils import InstagramFolderCleaner
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    print("⚠ Módulos refactorizados no disponibles")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Función principal."""
    if not MODULES_AVAILABLE:
        logger.error("❌ Error: Módulos refactorizados no disponibles")
        logger.error("   Asegúrate de que los módulos estén instalados")
        sys.exit(1)
    
    username = "lexiefyp"
    output_dir = scripts_dir.parent / "instagram_downloads" / username
    
    logger.info("=" * 60)
    logger.info(f"Descargando imágenes y videos de @{username} (Refactorizado)")
    logger.info("=" * 60)
    logger.info("\n⚠️  NOTA: Instagram puede bloquear solicitudes no autenticadas.")
    logger.info("   Si encuentras errores 401/403, intenta con credenciales:")
    logger.info("   python download_lexiefyp_refactored.py --login-username TU_USUARIO --login-password TU_PASSWORD")
    logger.info("\n" + "=" * 60 + "\n")
    
    # Parsear argumentos
    login_username = None
    login_password = None
    
    if "--login-username" in sys.argv:
        idx = sys.argv.index("--login-username")
        if idx + 1 < len(sys.argv):
            login_username = sys.argv[idx + 1]
    
    if "--login-password" in sys.argv:
        idx = sys.argv.index("--login-password")
        if idx + 1 < len(sys.argv):
            login_password = sys.argv[idx + 1]
    
    try:
        # Inicializar descargador
        downloader = InstagramDownloader(
            output_dir=output_dir,
            download_videos=True,
            download_stories=False,
            download_highlights=False
        )
        
        # Iniciar sesión si se proporcionan credenciales
        if login_username and login_password:
            if not downloader.login(login_username, login_password):
                logger.error("❌ No se pudo iniciar sesión")
                sys.exit(1)
        
        # Descargar
        success = downloader.download_profile(
            username=username,
            download_stories=False,
            download_highlights=False
        )
        
        if not success:
            logger.error("❌ Error en la descarga")
            sys.exit(1)
        
        # Limpiar folder - dejar solo imágenes y videos
        logger.info("\n" + "=" * 60)
        logger.info("Limpiando folder - eliminando archivos .json y metadatos...")
        logger.info("=" * 60 + "\n")
        
        cleaner = InstagramFolderCleaner()
        cleaner.clean_folder(str(output_dir), recursive=True)
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ Proceso completado!")
        logger.info(f"📁 Archivos guardados en: {output_dir}")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Descarga interrumpida por el usuario")
        logger.info("Limpiando archivos descargados hasta ahora...")
        if output_dir.exists():
            cleaner = InstagramFolderCleaner()
            cleaner.clean_folder(str(output_dir), recursive=True)
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        logger.info("Limpiando archivos descargados hasta ahora...")
        if output_dir.exists():
            cleaner = InstagramFolderCleaner()
            cleaner.clean_folder(str(output_dir), recursive=True)
        sys.exit(1)


if __name__ == "__main__":
    main()






