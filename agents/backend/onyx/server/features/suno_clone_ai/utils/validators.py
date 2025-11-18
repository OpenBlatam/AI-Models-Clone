"""
Validadores para inputs del sistema
"""

import re
from typing import Optional, List
from pydantic import validator


class InputValidators:
    """Clase con validadores reutilizables"""
    
    @staticmethod
    def validate_prompt(prompt: str, max_length: int = 500) -> str:
        """Valida y sanitiza un prompt"""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        prompt = prompt.strip()
        
        if len(prompt) > max_length:
            raise ValueError(f"Prompt too long. Maximum {max_length} characters.")
        
        # Eliminar caracteres peligrosos
        prompt = re.sub(r'[<>"\']', '', prompt)
        
        return prompt
    
    @staticmethod
    def validate_duration(duration: Optional[int], max_duration: int = 300) -> int:
        """Valida la duración de una canción"""
        if duration is None:
            return 30  # Default
        
        if duration < 1:
            raise ValueError("Duration must be at least 1 second")
        
        if duration > max_duration:
            raise ValueError(f"Duration cannot exceed {max_duration} seconds")
        
        return duration
    
    @staticmethod
    def validate_genre(genre: Optional[str]) -> Optional[str]:
        """Valida el género musical"""
        if genre is None:
            return None
        
        valid_genres = [
            "rock", "pop", "jazz", "classical", "electronic", "hip hop", "rap",
            "country", "blues", "reggae", "metal", "folk", "latin", "r&b",
            "soul", "funk", "disco", "techno", "house", "ambient", "indie"
        ]
        
        genre_lower = genre.lower().strip()
        if genre_lower not in valid_genres:
            # Si no está en la lista, permitirlo pero loguear
            return genre_lower
        
        return genre_lower
    
    @staticmethod
    def validate_song_ids(song_ids: List[str], max_count: int = 10) -> List[str]:
        """Valida una lista de IDs de canciones"""
        if not song_ids:
            raise ValueError("At least one song ID is required")
        
        if len(song_ids) > max_count:
            raise ValueError(f"Cannot mix more than {max_count} songs")
        
        # Validar formato UUID básico
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        
        for song_id in song_ids:
            if not uuid_pattern.match(song_id):
                raise ValueError(f"Invalid song ID format: {song_id}")
        
        return song_ids
    
    @staticmethod
    def validate_volumes(volumes: Optional[List[float]], 
                        count: int) -> Optional[List[float]]:
        """Valida una lista de volúmenes"""
        if volumes is None:
            return None
        
        if len(volumes) != count:
            raise ValueError(f"Number of volumes ({len(volumes)}) must match number of songs ({count})")
        
        for i, volume in enumerate(volumes):
            if volume < 0 or volume > 2.0:
                raise ValueError(f"Volume {i} must be between 0 and 2.0")
        
        return volumes
    
    @staticmethod
    def validate_fade_time(fade_time: Optional[float], max_time: float = 10.0) -> Optional[float]:
        """Valida el tiempo de fade"""
        if fade_time is None:
            return None
        
        if fade_time < 0:
            raise ValueError("Fade time cannot be negative")
        
        if fade_time > max_time:
            raise ValueError(f"Fade time cannot exceed {max_time} seconds")
        
        return fade_time

