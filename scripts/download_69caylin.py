"""
Script rápido para descargar imágenes de @69caylin
===================================================

Ejecuta este script directamente para descargar todas las imágenes
del perfil @69caylin en HD.

Uso:
    python download_69caylin.py
"""

from download_instagram_images import download_instagram_profile

if __name__ == "__main__":
    # Descargar imágenes de @69caylin
    download_instagram_profile(
        username="69caylin",
        output_dir=None,  # Se guardará en ./instagram_downloads/69caylin
        login_username=None,  # Cambia esto si el perfil es privado
        login_password=None,  # Cambia esto si el perfil es privado
        download_videos=False,  # Cambia a True si quieres videos también
        download_stories=False,
        download_highlights=False
    )








