"""
Schedule Manager
================
Manejo centralizado de calendarios de posts.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .config import Config

logger = logging.getLogger(__name__)


class ScheduleManager:
    """Gestor de calendarios de posts."""
    
    def __init__(self, schedule_file: Optional[str] = None):
        """
        Inicializar gestor de calendarios.
        
        Args:
            schedule_file: Ruta al archivo de calendario (opcional)
        """
        self.schedule_file = Path(schedule_file) if schedule_file else Config.SCHEDULE_FILE
    
    def load(self) -> List[Dict]:
        """
        Cargar calendario guardado.
        
        Returns:
            Lista de posts programados
        """
        if not self.schedule_file.exists():
            return []
        
        try:
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando calendario: {e}")
            return []
    
    def save(self, schedule_data: List[Dict]) -> bool:
        """
        Guardar calendario.
        
        Args:
            schedule_data: Lista de posts programados
        
        Returns:
            True si se guardó exitosamente
        """
        try:
            with open(self.schedule_file, 'w', encoding='utf-8') as f:
                json.dump(schedule_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error guardando calendario: {e}")
            return False
    
    def get_scheduled_posts(self) -> List[Dict]:
        """
        Obtener posts programados (no publicados).
        
        Returns:
            Lista de posts con status 'scheduled'
        """
        schedule_data = self.load()
        return [post for post in schedule_data if post.get('status') == 'scheduled']
    
    def get_published_posts(self) -> List[Dict]:
        """
        Obtener posts publicados.
        
        Returns:
            Lista de posts con status 'published'
        """
        schedule_data = self.load()
        return [post for post in schedule_data if post.get('status') == 'published']
    
    def get_failed_posts(self) -> List[Dict]:
        """
        Obtener posts fallidos.
        
        Returns:
            Lista de posts con status 'failed'
        """
        schedule_data = self.load()
        return [post for post in schedule_data if post.get('status') == 'failed']
    
    def get_next_post(self) -> Optional[Dict]:
        """
        Obtener próximo post programado.
        
        Returns:
            Próximo post o None
        """
        scheduled = self.get_scheduled_posts()
        if not scheduled:
            return None
        
        now = datetime.now()
        next_post = None
        next_datetime = None
        
        for post in scheduled:
            post_dt = datetime.fromisoformat(post['datetime'])
            if post_dt > now:
                if next_datetime is None or post_dt < next_datetime:
                    next_datetime = post_dt
                    next_post = post
        
        return next_post
    
    def update_post(self, post_id: str, updates: Dict) -> bool:
        """
        Actualizar un post específico.
        
        Args:
            post_id: ID del post
            updates: Diccionario con campos a actualizar
        
        Returns:
            True si se actualizó exitosamente
        """
        schedule_data = self.load()
        
        for post in schedule_data:
            if post.get('id') == post_id:
                post.update(updates)
                return self.save(schedule_data)
        
        return False
    
    def get_statistics(self) -> Dict:
        """
        Obtener estadísticas del calendario.
        
        Returns:
            Diccionario con estadísticas
        """
        schedule_data = self.load()
        
        return {
            'total': len(schedule_data),
            'scheduled': len(self.get_scheduled_posts()),
            'published': len(self.get_published_posts()),
            'failed': len(self.get_failed_posts()),
            'next_post': self.get_next_post()
        }







