"""
Script específico para descargar imágenes y videos de @lexiefyp
Con opción de usar credenciales de login para evitar rate limiting
"""

import sys
import os
from pathlib import Path

# Agregar el directorio scripts al path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from download_instagram_images import download_instagram_profile
from clean_instagram_folder import clean_instagram_folder

def main():
    username = "lexiefyp"
    output_dir = str(scripts_dir.parent / "instagram_downloads" / username)
    
    print("=" * 60)
    print(f"Descargando imágenes y videos de @{username}")
    print("=" * 60)
    print("\n⚠️  NOTA: Instagram puede bloquear solicitudes no autenticadas.")
    print("   Si encuentras errores 401/403, intenta con credenciales:")
    print("   python download_lexiefyp.py --login-username TU_USUARIO --login-password TU_PASSWORD")
    print("\n" + "=" * 60 + "\n")
    
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
        # Descargar
        download_instagram_profile(
            username=username,
            output_dir=output_dir,
            login_username=login_username,
            login_password=login_password,
            download_videos=True,
            download_stories=False,
            download_highlights=False
        )
        
        # Limpiar folder - dejar solo imágenes y videos
        print("\n" + "=" * 60)
        print("Limpiando folder - eliminando archivos .json y metadatos...")
        print("=" * 60 + "\n")
        clean_instagram_folder(output_dir)
        
        print("\n" + "=" * 60)
        print("✅ Proceso completado!")
        print(f"📁 Archivos guardados en: {output_dir}")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Descarga interrumpida por el usuario")
        print("Limpiando archivos descargados hasta ahora...")
        if os.path.exists(output_dir):
            clean_instagram_folder(output_dir)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Limpiando archivos descargados hasta ahora...")
        if os.path.exists(output_dir):
            clean_instagram_folder(output_dir)
        sys.exit(1)

if __name__ == "__main__":
    main()








