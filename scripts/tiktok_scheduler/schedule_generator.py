"""
Schedule Generator
==================
Generación de calendarios de posts.
"""

import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict

from .content_manager import ContentManager
from .config import Config

logger = logging.getLogger(__name__)


class ScheduleGenerator:
    """Generador de calendarios de posts."""
    
    def __init__(self, content_manager: Optional[ContentManager] = None):
        """
        Inicializar generador de calendarios.
        
        Args:
            content_manager: Gestor de contenido (opcional)
        """
        self.content_manager = content_manager or ContentManager()
    
    def generate_random_times(
        self,
        count: int,
        start_hour: int,
        start_min: int,
        end_hour: int,
        end_min: int,
        random_times: bool = True
    ) -> List[str]:
        """
        Generar horarios aleatorios o distribuidos.
        
        Args:
            count: Número de horarios a generar
            start_hour: Hora de inicio
            start_min: Minuto de inicio
            end_hour: Hora de fin
            end_min: Minuto de fin
            random_times: Si True, horarios aleatorios; si False, distribuidos
        
        Returns:
            Lista de horarios en formato HH:MM
        """
        times = []
        start_minutes = start_hour * 60 + start_min
        end_minutes = end_hour * 60 + end_min
        interval = (end_minutes - start_minutes) / count if count > 0 else 0
        
        for i in range(count):
            if random_times:
                min_minutes = start_minutes + i * interval
                max_minutes = start_minutes + (i + 1) * interval
                minutes = random.randint(int(min_minutes), int(max_minutes))
            else:
                minutes = start_minutes + i * interval
            
            hours = minutes // 60
            mins = minutes % 60
            times.append(f"{hours:02d}:{mins:02d}")
        
        return sorted(times)
    
    def generate_schedule(
        self,
        posts_per_day: int,
        start_date: str,
        random_times: bool,
        time_range: str
    ) -> List[Dict]:
        """
        Generar calendario de posts.
        
        Args:
            posts_per_day: Posts por día
            start_date: Fecha de inicio (YYYY-MM-DD)
            random_times: Si True, horarios aleatorios
            time_range: Rango de horarios (HH:MM-HH:MM)
        
        Returns:
            Lista de posts programados
        """
        schedule_data = []
        content_files = self.content_manager.get_content_files()
        
        if not content_files:
            logger.error("No se encontraron archivos de contenido")
            return []
        
        # Parsear rango de horarios
        start_time, end_time = time_range.split('-')
        start_hour, start_min = map(int, start_time.split(':'))
        end_hour, end_min = map(int, end_time.split(':'))
        
        # Calcular días necesarios
        total_posts = len(content_files)
        days_needed = (total_posts + posts_per_day - 1) // posts_per_day
        
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        file_index = 0
        
        for day in range(days_needed):
            current_date = start_dt + timedelta(days=day)
            times = self.generate_random_times(
                posts_per_day, start_hour, start_min,
                end_hour, end_min, random_times
            )
            
            for time_str in times:
                if file_index >= len(content_files):
                    break
                
                hour, minute = map(int, time_str.split(':'))
                post_datetime = current_date.replace(hour=hour, minute=minute, second=0)
                
                content_path = content_files[file_index]
                caption = self.content_manager.get_caption_from_json(content_path)
                content_type = self.content_manager.get_content_type(content_path)
                
                schedule_data.append({
                    'id': f"post_{file_index}_{int(post_datetime.timestamp())}",
                    'datetime': post_datetime.isoformat(),
                    'content_path': str(content_path),
                    'content_type': content_type,
                    'caption': caption,
                    'status': 'scheduled',
                    'created_at': datetime.now().isoformat()
                })
                
                file_index += 1
        
        return schedule_data







