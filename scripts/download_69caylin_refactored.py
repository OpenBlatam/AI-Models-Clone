"""
Script rápido para descargar imágenes de @69caylin - Versión Refactorizada
============================================================================
Versión refactorizada usando módulos refactorizados.
"""

import sys
from pathlib import Path

# Importar módulo refactorizado
try:
    from download_instagram_images_refactored import InstagramDownloader
    MODULE_AVAILABLE = True
except ImportError:
    MODULE_AVAILABLE = False
    print("⚠ download_instagram_images_refactored no disponible")


def main():
    """Función principal."""
    if not MODULE_AVAILABLE:
        print("❌ Error: Módulo refactorizado no disponible")
        print("   Asegúrate de que download_instagram_images_refactored.py existe")
        sys.exit(1)
    
    # Configurar directorio de salida
    output_dir = Path("instagram_downloads") / "69caylin"
    
    print("📥 Descargando imágenes de @69caylin")
    print(f"📁 Las imágenes se guardarán en: {output_dir.absolute()}")
    
    # Inicializar descargador
    downloader = InstagramDownloader(
        output_dir=output_dir,
        download_videos=False,
        download_stories=False,
        download_highlights=False
    )
    
    # Descargar perfil
    success = downloader.download_profile(
        username="69caylin",
        download_stories=False,
        download_highlights=False
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()






