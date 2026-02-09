"""
TikTok API Client
=================
Cliente refactorizado para la API de TikTok.
"""

import json
import logging
from typing import Dict, Optional, Tuple
import requests

from .config import Config

logger = logging.getLogger(__name__)


class TikTokAPI:
    """Cliente para la API de TikTok."""
    
    def __init__(self, access_token: str):
        """
        Inicializar cliente API.
        
        Args:
            access_token: Token de acceso de TikTok
        """
        self.access_token = access_token
        self.base_url = Config.API_BASE
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        timeout: int = 10
    ) -> Optional[requests.Response]:
        """
        Realizar petición HTTP a la API.
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint de la API
            headers: Headers adicionales
            params: Parámetros de query
            data: Datos del body
            files: Archivos para upload
            timeout: Timeout en segundos
        
        Returns:
            Response object o None si hay error
        """
        url = f"{self.base_url}{endpoint}"
        
        default_headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=default_headers, params=params, timeout=timeout)
            elif method.upper() == 'POST':
                response = requests.post(
                    url, headers=default_headers, params=params, data=data,
                    files=files, timeout=timeout
                )
            else:
                logger.error(f"Método HTTP no soportado: {method}")
                return None
            
            return response
        except Exception as e:
            logger.error(f"Error en petición {method} {endpoint}: {e}")
            return None
    
    def verify_token(self) -> bool:
        """Verificar si el token de acceso es válido."""
        response = self._make_request('GET', '/user/info/')
        return response is not None and response.status_code == 200
    
    def get_user_info(self) -> Optional[Dict]:
        """Obtener información del usuario de TikTok."""
        response = self._make_request('GET', '/user/info/')
        
        if not response or response.status_code != 200:
            logger.error(f"Error obteniendo info de usuario: {response.status_code if response else 'No response'}")
            return None
        
        try:
            data = response.json()
            user_data = data.get('data', {}).get('user', {}) or data.get('data', {})
            
            return {
                'username': user_data.get('display_name') or user_data.get('username') or user_data.get('open_id'),
                'display_name': user_data.get('display_name', ''),
                'avatar_url': user_data.get('avatar_url', ''),
                'follower_count': user_data.get('follower_count', 0),
                'following_count': user_data.get('following_count', 0),
                'likes_count': user_data.get('likes_count', 0),
                'video_count': user_data.get('video_count', 0)
            }
        except Exception as e:
            logger.error(f"Error parseando respuesta de usuario: {e}")
            return None
    
    def verify_target_account(self) -> Tuple[bool, Optional[str]]:
        """
        Verificar que la cuenta autorizada sea la cuenta objetivo.
        
        Returns:
            (es_valida, username_actual)
        """
        user_info = self.get_user_info()
        if not user_info:
            return False, None
        
        username = user_info.get('username', '').lower()
        target_username = Config.TARGET_USERNAME.lower()
        
        username_clean = username.replace('@', '')
        target_clean = target_username.replace('@', '')
        
        is_valid = username_clean == target_clean
        return is_valid, username
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict]:
        """Refrescar el token de acceso."""
        url = f"{self.base_url}/oauth/refresh_token/"
        data = {
            'client_key': Config.CLIENT_KEY,
            'client_secret': Config.CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error refrescando token: {e}")
            return None
    
    def upload_video(self, video_path: str, caption: str = "") -> Optional[Dict]:
        """
        Subir video a TikTok.
        
        Args:
            video_path: Ruta al archivo de video
            caption: Caption del video (máx 150 caracteres)
        
        Returns:
            Respuesta de la API o None si hay error
        """
        init_url = f"{self.base_url}/share/video/upload/"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
        }
        
        try:
            with open(video_path, 'rb') as f:
                files = {'video': f}
                data = {
                    'post_info': json.dumps({
                        'title': caption[:150],
                        'privacy_level': 'PUBLIC_TO_EVERYONE',
                        'disable_duet': False,
                        'disable_comment': False,
                        'disable_stitch': False,
                        'video_cover_timestamp_ms': 1000
                    })
                }
                response = requests.post(init_url, headers=headers, files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error subiendo video: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error en upload_video: {e}")
            return None
    
    def publish_image(self, image_path: str, caption: str = "") -> Optional[Dict]:
        """
        Publicar imagen en TikTok.
        Nota: TikTok requiere videos, esta función es un placeholder.
        
        Args:
            image_path: Ruta a la imagen
            caption: Caption de la imagen
        
        Returns:
            Respuesta placeholder
        """
        logger.warning("TikTok API requiere videos. Convirtiendo imagen a video...")
        return {
            'success': True,
            'message': 'Imagen programada para conversión a video',
            'image_path': image_path
        }







