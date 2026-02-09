"""
Instagram Folder Cleaner
========================
Limpia carpetas de descarga de Instagram eliminando metadatos.
"""

import logging
from pathlib import Path
from typing import Set, Optional

logger = logging.getLogger(__name__)


class InstagramFolderCleaner:
    """Limpia carpetas de descarga de Instagram."""
    
    def __init__(
        self,
        keep_extensions: Optional[Set[str]] = None,
        remove_extensions: Optional[Set[str]] = None
    ):
        """
        Inicializar limpiador.
        
        Args:
            keep_extensions: Extensiones de archivos a mantener
            remove_extensions: Extensiones de archivos a eliminar
        """
        self.keep_extensions = keep_extensions or {
            '.jpg', '.jpeg', '.png', '.gif', '.webp',
            '.mp4', '.mov', '.avi', '.mkv', '.webm'
        }
        self.remove_extensions = remove_extensions or {
            '.json', '.txt', '.xml', '.csv'
        }
    
    def clean_folder(self, folder_path: str, recursive: bool = True) -> dict:
        """
        Limpia un folder de descarga de Instagram.
        
        Args:
            folder_path: Ruta al folder a limpiar
            recursive: Si True, busca recursivamente
        
        Returns:
            Diccionario con estadísticas de limpieza
        """
        folder = Path(folder_path)
        
        if not folder.exists():
            logger.error(f"El folder {folder_path} no existe")
            return {
                'deleted': 0,
                'kept': 0,
                'unknown': 0,
                'errors': 0
            }
        
        logger.info(f"Limpiando folder: {folder_path}")
        
        deleted_count = 0
        kept_count = 0
        unknown_count = 0
        error_count = 0
        
        # Buscar archivos
        if recursive:
            files = list(folder.rglob('*'))
        else:
            files = list(folder.glob('*'))
        
        for file_path in files:
            if not file_path.is_file():
                continue
            
            ext = file_path.suffix.lower()
            
            if ext in self.remove_extensions:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    logger.debug(f"  Eliminado: {file_path.name}")
                except Exception as e:
                    error_count += 1
                    logger.error(f"  Error al eliminar {file_path.name}: {e}")
            elif ext in self.keep_extensions:
                kept_count += 1
            else:
                unknown_count += 1
                logger.debug(f"  Archivo con extensión desconocida: {file_path.name} ({ext})")
        
        logger.info(f"Limpieza completada:")
        logger.info(f"   Archivos mantenidos: {kept_count}")
        logger.info(f"   Archivos eliminados: {deleted_count}")
        logger.info(f"   Archivos desconocidos: {unknown_count}")
        logger.info(f"   Errores: {error_count}")
        
        return {
            'deleted': deleted_count,
            'kept': kept_count,
            'unknown': unknown_count,
            'errors': error_count
        }






