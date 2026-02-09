"""
Post Publisher
==============
Publicación de posts a TikTok.
"""

import logging
from datetime import datetime
from typing import Dict, Optional

from .tiktok_api import TikTokAPI
from .token_manager import TokenManager
from .config import Config

logger = logging.getLogger(__name__)


class PostPublisher:
    """Publicador de posts a TikTok."""
    
    def __init__(self, token_manager: Optional[TokenManager] = None):
        """
        Inicializar publicador.
        
        Args:
            token_manager: Gestor de tokens (opcional)
        """
        self.token_manager = token_manager or TokenManager()
    
    def _get_api(self) -> Optional[TikTokAPI]:
        """
        Obtener instancia de API con token válido.
        
        Returns:
            Instancia de TikTokAPI o None si no hay token válido
        """
        access_token = self.token_manager.get_access_token()
        
        if not access_token:
            logger.error("No hay token de acceso disponible")
            return None
        
        api = TikTokAPI(access_token)
        
        # Verificar token
        if not api.verify_token():
            # Intentar refrescar
            refresh_token = self.token_manager.get_refresh_token()
            if refresh_token:
                new_tokens = api.refresh_access_token(refresh_token)
                if new_tokens:
                    self.token_manager.save(new_tokens)
                    access_token = new_tokens.get('access_token')
                    api = TikTokAPI(access_token)
                else:
                    logger.error("No se pudo refrescar el token")
                    return None
            else:
                logger.error("Token inválido y no hay refresh token")
                return None
        
        return api
    
    def _verify_account(self, api: TikTokAPI) -> tuple[bool, Optional[str]]:
        """
        Verificar que la cuenta sea la correcta.
        
        Args:
            api: Instancia de TikTokAPI
        
        Returns:
            (es_valida, username)
        """
        is_target_account, username = api.verify_target_account()
        
        if not is_target_account:
            logger.error(
                f"⚠️  CUENTA INCORRECTA: Se intentó publicar en @{username} "
                f"pero debe ser @{Config.TARGET_USERNAME}"
            )
        else:
            logger.info(f"✅ Cuenta verificada: @{username} (correcta)")
        
        return is_target_account, username
    
    def publish(self, post: Dict) -> bool:
        """
        Publicar un post programado.
        
        Args:
            post: Diccionario con información del post
        
        Returns:
            True si se publicó exitosamente
        """
        try:
            api = self._get_api()
            if not api:
                post['status'] = 'failed'
                post['error'] = 'No hay token de acceso disponible'
                return False
            
            # Validar cuenta
            is_valid, username = self._verify_account(api)
            if not is_valid:
                post['status'] = 'failed'
                post['error'] = f'Cuenta incorrecta: @{username}. Debe ser @{Config.TARGET_USERNAME}'
                return False
            
            # Obtener información del post
            content_path = post.get('content_path') or post.get('image_path')
            content_type = post.get('content_type', 'image')
            caption = post.get('caption', '')
            
            logger.info(
                f"📤 Publicando en @{Config.TARGET_USERNAME}: {content_path} "
                f"a las {post.get('datetime')}"
            )
            logger.info(f"Tipo: {content_type}, Caption: {caption[:50]}...")
            
            # Publicar según el tipo
            if content_type == 'video' or (content_path and content_path.endswith(('.mp4', '.mov', '.avi'))):
                result = api.upload_video(content_path, caption)
                if result:
                    logger.info("✅ Video publicado exitosamente")
                    post['status'] = 'published'
                    post['published_at'] = datetime.now().isoformat()
                    post['published_to'] = Config.TARGET_USERNAME
                    post['video_id'] = result.get('data', {}).get('item_id') or result.get('video_id', '')
                    return True
                else:
                    logger.error("❌ Error al publicar video")
                    post['status'] = 'failed'
                    post['error'] = 'Error al subir video a TikTok'
                    return False
            else:
                logger.warning("⚠️  Publicando imagen (TikTok requiere videos)")
                result = api.publish_image(content_path, caption)
                if result:
                    logger.info("✅ Imagen programada para publicación")
                    post['status'] = 'published'
                    post['published_at'] = datetime.now().isoformat()
                    post['published_to'] = Config.TARGET_USERNAME
                    return True
                else:
                    logger.error("❌ Error al publicar imagen")
                    post['status'] = 'failed'
                    post['error'] = 'Error al publicar imagen'
                    return False
                    
        except Exception as e:
            logger.error(f"Error publicando post: {e}")
            post['status'] = 'failed'
            post['error'] = str(e)
            return False







