"""
Configuración de TikTok Scheduler
=================================

Configuración con tus credenciales de TikTok API.
"""

# Credenciales de TikTok API
# Obtén estas credenciales en: https://developers.tiktok.com/
TIKTOK_CLIENT_KEY = 'awdfpqe9vtflv9ht'
TIKTOK_CLIENT_SECRET = 'HupguDpxbdVdfmqbrZrtuYlNnyHKJRvC'  # ⚠️ Configura tu Client Secret aquí

# URI de redirección (debe coincidir con el configurado en TikTok Developer Portal)
TIKTOK_REDIRECT_URI = 'http://localhost:8000/'

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








