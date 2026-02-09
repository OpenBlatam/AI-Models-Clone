"""
Script para descargar imágenes de Instagram - Versión Refactorizada
======================================================================
Versión refactorizada con mejor organización y manejo de errores.
"""

import sys
import logging
from pathlib import Path
from typing import Optional
import argparse

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import instaloader

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InstagramDownloader:
    """Descargador de contenido de Instagram."""
    
    def __init__(
        self,
        output_dir: Path,
        download_videos: bool = False,
        download_stories: bool = False,
        download_highlights: bool = False
    ):
        """
        Inicializar descargador.
        
        Args:
            output_dir: Directorio de salida
            download_videos: Si True, descargar videos
            download_stories: Si True, descargar stories
            download_highlights: Si True, descargar highlights
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear instancia de Instaloader
        self.loader = instaloader.Instaloader(
            download_videos=download_videos,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=True,
            compress_json=False,
            post_metadata_txt_pattern='',
            storyitem_metadata_txt_pattern='',
            max_connection_attempts=3,
            dirname_pattern=str(self.output_dir),
            filename_pattern='{date_utc}_UTC_{shortcode}',
        )
        
        # Configurar para descargar en HD
        self.loader.download_pictures = True
        self.loader.download_videos = download_videos
        self.loader.download_video_thumbnails = False
    
    def login(self, username: str, password: str) -> bool:
        """
        Iniciar sesión en Instagram.
        
        Args:
            username: Usuario de Instagram
            password: Contraseña
        
        Returns:
            True si el login fue exitoso
        """
        try:
            logger.info(f"🔐 Iniciando sesión como @{username}...")
            self.loader.login(username, password)
            logger.info("✅ Sesión iniciada correctamente")
            return True
        except instaloader.exceptions.BadCredentialsException:
            logger.error("❌ Error: Credenciales incorrectas")
            return False
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            logger.error("❌ Error: Se requiere autenticación de dos factores")
            logger.info("   Por favor, inicia sesión manualmente usando: instaloader --login")
            return False
        except Exception as e:
            logger.error(f"❌ Error iniciando sesión: {e}")
            return False
    
    def download_profile(
        self,
        username: str,
        download_stories: bool = False,
        download_highlights: bool = False
    ) -> bool:
        """
        Descargar perfil de Instagram.
        
        Args:
            username: Nombre de usuario (sin @)
            download_stories: Si True, descargar stories
            download_highlights: Si True, descargar highlights
        
        Returns:
            True si se descargó exitosamente
        """
        try:
            logger.info(f"📥 Descargando perfil @{username}...")
            
            # Obtener perfil
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            logger.info(f"📊 Perfil: {profile.full_name}")
            logger.info(f"   Posts: {profile.mediacount}")
            logger.info(f"   Seguidores: {profile.followers}")
            
            # Descargar posts
            logger.info("📸 Descargando posts...")
            self.loader.download_profile(profile.username)
            
            # Descargar stories si está habilitado
            if download_stories:
                try:
                    logger.info("📱 Descargando stories...")
                    for story in self.loader.get_stories([profile.userid]):
                        for item in story.get_items():
                            self.loader.download_storyitem(item, target=str(self.output_dir))
                except Exception as e:
                    logger.warning(f"⚠ Error descargando stories: {e}")
            
            # Descargar highlights si está habilitado
            if download_highlights:
                try:
                    logger.info("⭐ Descargando highlights...")
                    for highlight in self.loader.get_highlights(profile):
                        for item in highlight.get_items():
                            self.loader.download_storyitem(item, target=str(self.output_dir))
                except Exception as e:
                    logger.warning(f"⚠ Error descargando highlights: {e}")
            
            logger.info(f"✅ Descarga completada: {self.output_dir.absolute()}")
            return True
            
        except instaloader.exceptions.ProfileNotExistsException:
            logger.error(f"❌ Error: El perfil @{username} no existe")
            return False
        except instaloader.exceptions.PrivateProfileNotFollowedException:
            logger.error(f"❌ Error: El perfil @{username} es privado y no lo sigues")
            logger.info("   Inicia sesión para acceder a perfiles privados")
            return False
        except Exception as e:
            logger.error(f"❌ Error descargando perfil: {e}")
            return False


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Descarga todas las imágenes de un perfil de Instagram en HD",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Descargar perfil público
  python download_instagram_images_refactored.py username
  
  # Descargar con login (para perfiles privados)
  python download_instagram_images_refactored.py username --login-user tu_usuario --login-password tu_password
  
  # También descargar videos
  python download_instagram_images_refactored.py username --download-videos
  
  # Descargar stories (requiere login)
  python download_instagram_images_refactored.py username --login-user tu_usuario --download-stories
        """
    )
    
    parser.add_argument(
        "username",
        type=str,
        help="Nombre de usuario de Instagram (sin @)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directorio donde guardar las imágenes (default: ./instagram_downloads/{username})"
    )
    
    parser.add_argument(
        "--login-user",
        type=str,
        default=None,
        help="Usuario de Instagram para login (opcional)"
    )
    
    parser.add_argument(
        "--login-password",
        type=str,
        default=None,
        help="Contraseña de Instagram (opcional)"
    )
    
    parser.add_argument(
        "--download-videos",
        action="store_true",
        help="También descargar videos"
    )
    
    parser.add_argument(
        "--download-stories",
        action="store_true",
        help="Descargar stories (requiere login)"
    )
    
    parser.add_argument(
        "--download-highlights",
        action="store_true",
        help="Descargar highlights (requiere login)"
    )
    
    args = parser.parse_args()
    
    # Configurar directorio de salida
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path("instagram_downloads") / args.username
    
    logger.info(f"📥 Iniciando descarga de imágenes de @{args.username}")
    logger.info(f"📁 Las imágenes se guardarán en: {output_dir.absolute()}")
    
    # Inicializar descargador
    downloader = InstagramDownloader(
        output_dir=output_dir,
        download_videos=args.download_videos,
        download_stories=args.download_stories,
        download_highlights=args.download_highlights
    )
    
    # Iniciar sesión si se proporcionan credenciales
    if args.login_user and args.login_password:
        if not downloader.login(args.login_user, args.login_password):
            logger.error("❌ No se pudo iniciar sesión")
            sys.exit(1)
    
    # Descargar perfil
    success = downloader.download_profile(
        username=args.username,
        download_stories=args.download_stories,
        download_highlights=args.download_highlights
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()







