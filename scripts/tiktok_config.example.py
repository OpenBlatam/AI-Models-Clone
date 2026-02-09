"""
Configuración de TikTok Scheduler
=================================

Copia este archivo a 'tiktok_config.py' y completa con tus credenciales.
"""

# Credenciales de TikTok API
# Obtén estas credenciales en: https://developers.tiktok.com/
TIKTOK_CLIENT_KEY = 'TU_CLIENT_KEY_AQUI'
TIKTOK_CLIENT_SECRET = 'TU_CLIENT_SECRET_AQUI'

# URI de redirección (debe coincidir con el configurado en TikTok Developer Portal)
TIKTOK_REDIRECT_URI = 'http://localhost:8000/callback'

# Configuración del servidor
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000
DEBUG_MODE = True

# Configuración de programación por defecto
DEFAULT_POSTS_PER_DAY = 4
DEFAULT_TIME_RANGE = '09:00-22:00'
DEFAULT_RANDOM_TIMES = True

# Carpeta de contenido
CONTENT_FOLDER = 'instagram_downloads/69caylin'








