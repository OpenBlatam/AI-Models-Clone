"""
Script para descargar todas las imágenes de un perfil de Instagram en HD
==========================================================================

Este script utiliza instaloader para descargar todas las imágenes públicas
de un perfil de Instagram en alta resolución.

Requisitos:
    pip install instaloader

Uso:
    python download_instagram_images.py

Notas importantes:
    - Instagram puede requerir inicio de sesión para algunos perfiles
    - Los perfiles privados requieren seguir al usuario primero
    - Respeta los términos de servicio de Instagram
    - El script respeta los límites de velocidad de Instagram
"""

import instaloader
import os
import sys
from pathlib import Path
from typing import Optional
import argparse
import time

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def download_instagram_profile(
    username: str,
    output_dir: Optional[str] = None,
    login_username: Optional[str] = None,
    login_password: Optional[str] = None,
    download_videos: bool = False,
    download_stories: bool = False,
    download_highlights: bool = False
) -> None:
    """
    Descarga todas las imágenes de un perfil de Instagram en HD.
    
    Args:
        username: Nombre de usuario de Instagram (sin @)
        output_dir: Directorio donde guardar las imágenes (default: ./instagram_downloads/{username})
        login_username: Usuario de Instagram para login (opcional, recomendado para perfiles privados)
        login_password: Contraseña de Instagram (opcional)
        download_videos: Si True, también descarga videos
        download_stories: Si True, descarga stories (requiere login)
        download_highlights: Si True, descarga highlights (requiere login)
    """
    # Configurar directorio de salida
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "instagram_downloads", username)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"📥 Iniciando descarga de imágenes de @{username}")
    print(f"📁 Las imágenes se guardarán en: {output_path.absolute()}")
    
    # Crear instancia de Instaloader
    loader = instaloader.Instaloader(
        download_videos=download_videos,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=True,
        compress_json=False,
        post_metadata_txt_pattern='',
        storyitem_metadata_txt_pattern='',
        max_connection_attempts=3,
        dirname_pattern=str(output_path),
        filename_pattern='{date_utc}_UTC_{shortcode}',
    )
    
    # Configurar para descargar en HD
    loader.download_pictures = True
    loader.download_videos = download_videos
    loader.download_video_thumbnails = False
    
    # Iniciar sesión si se proporcionan credenciales
    if login_username and login_password:
        try:
            print(f"🔐 Iniciando sesión como @{login_username}...")
            loader.login(login_username, login_password)
            print("✅ Sesión iniciada correctamente")
        except instaloader.exceptions.BadCredentialsException:
            print("❌ Error: Credenciales incorrectas")
            sys.exit(1)
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            print("❌ Error: Se requiere autenticación de dos factores")
            print("   Por favor, inicia sesión manualmente usando: instaloader --login")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error al iniciar sesión: {e}")
            sys.exit(1)
    
    try:
        # Obtener perfil
        print(f"🔍 Obteniendo información del perfil @{username}...")
        profile = instaloader.Profile.from_username(loader.context, username)
        
        print(f"📊 Perfil encontrado: {profile.full_name}")
        print(f"📸 Total de posts: {profile.mediacount}")
        print(f"👥 Seguidores: {profile.followers}")
        
        # Verificar si el perfil es privado
        if profile.is_private:
            if not login_username:
                print("⚠️  ADVERTENCIA: Este perfil es privado.")
                print("   Necesitas iniciar sesión y seguir al usuario para descargar sus imágenes.")
                print("   Usa --login-username y --login-password para iniciar sesión.")
                sys.exit(1)
            else:
                print("🔒 Perfil privado detectado. Verificando acceso...")
        
        # Descargar posts
        print(f"\n📥 Descargando posts de @{username}...")
        post_count = 0
        
        for post in profile.get_posts():
            try:
                loader.download_post(post, target=username)
                post_count += 1
                print(f"✅ Descargado post {post_count}/{profile.mediacount} - {post.shortcode}")
                # Agregar delay para evitar rate limiting (2 segundos entre posts)
                if post_count < profile.mediacount:
                    time.sleep(2)
            except instaloader.exceptions.PrivateProfileNotFollowedException:
                print(f"❌ No puedes acceder a este post. Necesitas seguir a @{username}")
                break
            except Exception as e:
                print(f"⚠️  Error al descargar post {post.shortcode}: {e}")
                # Si hay un error, esperar un poco más antes de continuar
                time.sleep(5)
                continue
        
        print(f"\n✅ Descarga completada: {post_count} posts descargados")
        
        # Descargar stories si está habilitado
        if download_stories and login_username:
            try:
                print(f"\n📱 Descargando stories de @{username}...")
                loader.download_stories(userids=[profile.userid])
                print("✅ Stories descargados")
            except Exception as e:
                print(f"⚠️  Error al descargar stories: {e}")
        
        # Descargar highlights si está habilitado
        if download_highlights and login_username:
            try:
                print(f"\n⭐ Descargando highlights de @{username}...")
                for highlight in loader.get_highlights(profile):
                    loader.download_highlight(highlight, profile.username)
                print("✅ Highlights descargados")
            except Exception as e:
                print(f"⚠️  Error al descargar highlights: {e}")
        
        print(f"\n🎉 ¡Descarga completada!")
        print(f"📁 Imágenes guardadas en: {output_path.absolute()}")
        
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"❌ Error: El perfil @{username} no existe")
        sys.exit(1)
    except instaloader.exceptions.ConnectionException as e:
        print(f"❌ Error de conexión: {e}")
        print("   Verifica tu conexión a internet o intenta más tarde")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Función principal con argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Descarga todas las imágenes de un perfil de Instagram en HD",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Descarga básica (solo imágenes públicas)
  python download_instagram_images.py 69caylin
  
  # Con inicio de sesión (para perfiles privados)
  python download_instagram_images.py 69caylin --login-username tu_usuario --login-password tu_contraseña
  
  # Descargar también videos
  python download_instagram_images.py 69caylin --download-videos
  
  # Descargar todo (posts, videos, stories, highlights)
  python download_instagram_images.py 69caylin --login-username tu_usuario --login-password tu_contraseña --download-videos --download-stories --download-highlights
  
  # Especificar directorio de salida
  python download_instagram_images.py 69caylin --output-dir ./mis_descargas
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
        "--login-username",
        type=str,
        default=None,
        help="Usuario de Instagram para iniciar sesión (opcional, necesario para perfiles privados)"
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
    
    # Validar que si se descargan stories o highlights, haya login
    if (args.download_stories or args.download_highlights) and not args.login_username:
        print("❌ Error: --download-stories y --download-highlights requieren --login-username")
        sys.exit(1)
    
    download_instagram_profile(
        username=args.username,
        output_dir=args.output_dir,
        login_username=args.login_username,
        login_password=args.login_password,
        download_videos=args.download_videos,
        download_stories=args.download_stories,
        download_highlights=args.download_highlights
    )


if __name__ == "__main__":
    main()








