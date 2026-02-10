"""
Data Processors
==============

Procesadores de datos funcionales.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DataProcessor:
    """Procesador base de datos."""
    
    def __init__(self):
        """Inicializar procesador."""
        self._logger = logger
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizar datos.
        
        Args:
            data: Datos a normalizar
        
        Returns:
            Datos normalizados
        """
        normalized = {}
        for key, value in data.items():
            normalized_key = key.lower().replace(" ", "_")
            normalized[normalized_key] = value
        return normalized
    
    def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Limpiar datos.
        
        Args:
            data: Datos a limpiar
        
        Returns:
            Datos limpios
        """
        cleaned = {}
        for key, value in data.items():
            if value is not None:
                if isinstance(value, str):
                    cleaned[key] = value.strip()
                else:
                    cleaned[key] = value
        return cleaned


class EventProcessor(DataProcessor):
    """Procesador de eventos."""
    
    def process_event_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesar datos de evento.
        
        Args:
            event_data: Datos del evento
        
        Returns:
            Datos procesados
        """
        # Normalizar
        normalized = self.normalize(event_data)
        
        # Limpiar
        cleaned = self.clean(normalized)
        
        # Validar y convertir fechas
        if "start_time" in cleaned and isinstance(cleaned["start_time"], str):
            cleaned["start_time"] = datetime.fromisoformat(cleaned["start_time"])
        
        if "end_time" in cleaned and isinstance(cleaned["end_time"], str):
            cleaned["end_time"] = datetime.fromisoformat(cleaned["end_time"])
        
        return cleaned
    
    def enrich_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriquecer datos de evento.
        
        Args:
            event_data: Datos del evento
        
        Returns:
            Datos enriquecidos
        """
        enriched = event_data.copy()
        
        # Calcular duración
        if "start_time" in enriched and "end_time" in enriched:
            start = enriched["start_time"]
            end = enriched["end_time"]
            if isinstance(start, datetime) and isinstance(end, datetime):
                duration = (end - start).total_seconds() / 3600
                enriched["duration_hours"] = duration
        
        # Agregar metadata
        enriched["processed_at"] = datetime.now().isoformat()
        
        return enriched


class RoutineProcessor(DataProcessor):
    """Procesador de rutinas."""
    
    def process_routine_data(self, routine_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesar datos de rutina.
        
        Args:
            routine_data: Datos de la rutina
        
        Returns:
            Datos procesados
        """
        normalized = self.normalize(routine_data)
        cleaned = self.clean(normalized)
        
        # Convertir tiempo programado
        if "scheduled_time" in cleaned and isinstance(cleaned["scheduled_time"], str):
            from datetime import time
            cleaned["scheduled_time"] = time.fromisoformat(cleaned["scheduled_time"])
        
        return cleaned




