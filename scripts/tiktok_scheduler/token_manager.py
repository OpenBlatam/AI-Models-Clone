"""
Token Manager
=============
Manejo centralizado de tokens de autenticación.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional

from .config import Config

logger = logging.getLogger(__name__)


class TokenManager:
    """Gestor de tokens de autenticación."""
    
    def __init__(self, token_file: Optional[str] = None):
        """
        Inicializar gestor de tokens.
        
        Args:
            token_file: Ruta al archivo de tokens (opcional)
        """
        self.token_file = Path(token_file) if token_file else Config.TOKEN_FILE
    
    def load(self) -> Dict:
        """
        Cargar tokens guardados.
        
        Returns:
            Diccionario con tokens o diccionario vacío
        """
        if not self.token_file.exists():
            return {}
        
        try:
            with open(self.token_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando tokens: {e}")
            return {}
    
    def save(self, tokens: Dict) -> bool:
        """
        Guardar tokens.
        
        Args:
            tokens: Diccionario con tokens
        
        Returns:
            True si se guardó exitosamente
        """
        try:
            # Agregar timestamp si no existe
            if 'created_at' not in tokens:
                tokens['created_at'] = datetime.now().isoformat()
            
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(tokens, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error guardando tokens: {e}")
            return False
    
    def get_access_token(self) -> Optional[str]:
        """
        Obtener token de acceso.
        
        Returns:
            Token de acceso o None
        """
        tokens = self.load()
        return tokens.get('access_token')
    
    def get_refresh_token(self) -> Optional[str]:
        """
        Obtener refresh token.
        
        Returns:
            Refresh token o None
        """
        tokens = self.load()
        return tokens.get('refresh_token')
    
    def has_tokens(self) -> bool:
        """
        Verificar si hay tokens guardados.
        
        Returns:
            True si hay tokens
        """
        tokens = self.load()
        return bool(tokens.get('access_token'))
    
    def clear(self) -> bool:
        """
        Limpiar tokens guardados.
        
        Returns:
            True si se limpiaron exitosamente
        """
        try:
            if self.token_file.exists():
                self.token_file.unlink()
            return True
        except Exception as e:
            logger.error(f"Error limpiando tokens: {e}")
            return False







