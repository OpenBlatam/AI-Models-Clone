"""
Instagram Utils - Módulo Refactorizado
=======================================
Utilidades para manejo de carpetas y archivos de Instagram.
"""

from .folder_cleaner import InstagramFolderCleaner
from .download_checker import InstagramDownloadChecker

__version__ = '2.0.0'
__all__ = [
    'InstagramFolderCleaner',
    'InstagramDownloadChecker'
]






