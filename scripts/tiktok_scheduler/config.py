"""
Configuración del TikTok Scheduler
==================================
Centraliza toda la configuración del sistema.
"""

import os
from pathlib import Path
from typing import Optional

# Directorio base
BASE_DIR = Path(__file__).parent.parent

# Configuración de TikTok API
try:
    from tiktok_config import (
        TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET,
        TIKTOK_REDIRECT_URI, SERVER_HOST, SERVER_PORT, DEBUG_MODE
    )
except ImportError:
    TIKTOK_CLIENT_KEY = os.getenv('TIKTOK_CLIENT_KEY', 'TU_CLIENT_KEY_AQUI')
    TIKTOK_CLIENT_SECRET = os.getenv('TIKTOK_CLIENT_SECRET', 'TU_CLIENT_SECRET_AQUI')
    TIKTOK_REDIRECT_URI = os.getenv('TIKTOK_REDIRECT_URI', 'http://localhost:8000/callback')
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', '8000'))
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() == 'true'

# API Base URL
TIKTOK_API_BASE = 'https://open-api.tiktok.com'

# Directorios
CONTENT_DIR = BASE_DIR / 'instagram_downloads' / '69caylin'
VIDEOS_DIR = BASE_DIR / 'videos_ai_69caylin' / 'individual'
SCHEDULE_FILE = BASE_DIR / 'tiktok_schedule.json'
TOKEN_FILE = BASE_DIR / 'tiktok_tokens.json'
STATUS_FILE = BASE_DIR / 'tiktok_status.json'

# Configuración de contenido
USE_VIDEOS = True  # Cambiar a False para usar imágenes

# Cuenta objetivo
TARGET_TIKTOK_USERNAME = 'kassy_138'


class Config:
    """Clase de configuración centralizada."""
    
    # API
    CLIENT_KEY: str = TIKTOK_CLIENT_KEY
    CLIENT_SECRET: str = TIKTOK_CLIENT_SECRET
    REDIRECT_URI: str = TIKTOK_REDIRECT_URI
    API_BASE: str = TIKTOK_API_BASE
    
    # Servidor
    HOST: str = SERVER_HOST
    PORT: int = SERVER_PORT
    DEBUG: bool = DEBUG_MODE
    
    # Directorios
    BASE_DIR: Path = BASE_DIR
    CONTENT_DIR: Path = CONTENT_DIR
    VIDEOS_DIR: Path = VIDEOS_DIR
    SCHEDULE_FILE: Path = SCHEDULE_FILE
    TOKEN_FILE: Path = TOKEN_FILE
    STATUS_FILE: Path = STATUS_FILE
    
    # Contenido
    USE_VIDEOS: bool = USE_VIDEOS
    
    # Cuenta
    TARGET_USERNAME: str = TARGET_TIKTOK_USERNAME
    
    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        """
        Validar configuración.
        
        Returns:
            (is_valid, error_message)
        """
        if cls.CLIENT_KEY == 'TU_CLIENT_KEY_AQUI':
            return False, "TIKTOK_CLIENT_KEY no configurado"
        
        if not cls.CONTENT_DIR.exists() and not cls.VIDEOS_DIR.exists():
            return False, f"Directorios de contenido no existen: {cls.CONTENT_DIR}, {cls.VIDEOS_DIR}"
        
        return True, None







