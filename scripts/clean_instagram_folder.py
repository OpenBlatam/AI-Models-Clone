"""
Script para limpiar folders de descarga de Instagram, dejando solo imágenes y videos.
Elimina archivos .json, .txt y otros metadatos.
"""

import os
import sys
from pathlib import Path

def clean_instagram_folder(folder_path: str):
    """
    Limpia un folder de descarga de Instagram, dejando solo imágenes y videos.
    
    Args:
        folder_path: Ruta al folder a limpiar
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"ERROR: El folder {folder_path} no existe")
        return
    
    print(f"Limpiando folder: {folder_path}")
    
    # Extensiones de archivos a mantener (imágenes y videos)
    keep_extensions = {'.jpg', '.jpeg', '.png', '.mp4', '.mov', '.avi', '.mkv', '.webm'}
    
    # Extensiones de archivos a eliminar
    remove_extensions = {'.json', '.txt', '.xml'}
    
    deleted_count = 0
    kept_count = 0
    
    for file_path in folder.rglob('*'):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            
            if ext in remove_extensions:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    print(f"  Eliminado: {file_path.name}")
                except Exception as e:
                    print(f"  Error al eliminar {file_path.name}: {e}")
            elif ext in keep_extensions:
                kept_count += 1
            else:
                # Archivos con extensiones desconocidas - preguntar o mantener
                print(f"  Archivo con extension desconocida: {file_path.name} ({ext})")
    
    print(f"\nLimpieza completada:")
    print(f"   Archivos mantenidos: {kept_count}")
    print(f"   Archivos eliminados: {deleted_count}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python clean_instagram_folder.py <ruta_al_folder>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    clean_instagram_folder(folder_path)

