"""
Scheduler
=========
Programador de posts automático.
"""

import time
import logging
from datetime import datetime
from typing import Optional

from .schedule_manager import ScheduleManager
from .post_publisher import PostPublisher

logger = logging.getLogger(__name__)


class Scheduler:
    """Programador automático de posts."""
    
    def __init__(
        self,
        schedule_manager: Optional[ScheduleManager] = None,
        post_publisher: Optional[PostPublisher] = None
    ):
        """
        Inicializar programador.
        
        Args:
            schedule_manager: Gestor de calendarios (opcional)
            post_publisher: Publicador de posts (opcional)
        """
        self.schedule_manager = schedule_manager or ScheduleManager()
        self.post_publisher = post_publisher or PostPublisher()
        self.running = False
    
    def start(self):
        """Iniciar el programador."""
        if self.running:
            logger.warning("El programador ya está corriendo")
            return
        
        self.running = True
        logger.info("Programador iniciado")
    
    def stop(self):
        """Detener el programador."""
        self.running = False
        logger.info("Programador detenido")
    
    def run(self):
        """Ejecutar el programador (loop principal)."""
        while self.running:
            try:
                now = datetime.now()
                schedule_data = self.schedule_manager.load()
                
                for post in schedule_data:
                    if post.get('status') != 'scheduled':
                        continue
                    
                    post_dt = datetime.fromisoformat(post['datetime'])
                    
                    # Publicar si es el momento
                    if now >= post_dt:
                        logger.info(f"Publicando post programado: {post['id']}")
                        success = self.post_publisher.publish(post)
                        
                        if success:
                            logger.info(f"✅ Post {post['id']} publicado exitosamente")
                        else:
                            logger.error(f"❌ Error publicando post {post['id']}")
                
                # Guardar calendario actualizado
                self.schedule_manager.save(schedule_data)
                
                # Esperar 1 minuto antes de revisar de nuevo
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error en scheduler: {e}")
                time.sleep(60)
    
    def is_running(self) -> bool:
        """
        Verificar si el programador está corriendo.
        
        Returns:
            True si está corriendo
        """
        return self.running







