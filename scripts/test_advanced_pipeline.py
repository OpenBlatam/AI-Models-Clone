"""
Test del Pipeline Avanzado con Todas las Mejoras
==================================================
Prueba el pipeline completo con todas las 37 tecnicas avanzadas.
"""

import cv2
import numpy as np
from pathlib import Path
import random
import sys
import io

# Configurar codificacion UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar el directorio al path
sys.path.insert(0, str(Path(__file__).parent))

from face_swap_modules.face_swap_pipeline import FaceSwapPipeline

def get_bunny_faces():
    """Obtiene todas las caras de bunny disponibles."""
    bunny_dirs = [
        "instagram_downloads/bunnyrose.me",
        "instagram_downloads/bunnyrose.uwu",
        "instagram_downloads/bunnyy.rose_"
    ]
    
    all_faces = []
    for dir_path in bunny_dirs:
        dir_obj = Path(dir_path)
        if dir_obj.exists():
            jpg_files = list(dir_obj.glob("*.jpg"))
            all_faces.extend(jpg_files)
    
    return all_faces

def get_69caylin_images():
    """Obtiene todas las imagenes de 69caylin."""
    caylin_dir = Path("instagram_downloads/69caylin")
    if not caylin_dir.exists():
        return []
    
    return list(caylin_dir.glob("*.jpg"))

def main():
    print("=" * 70)
    print("TEST PIPELINE AVANZADO - TODAS LAS 37 TECNICAS")
    print("=" * 70)
    
    # Obtener imagenes
    print("\nCargando imagenes...")
    bunny_faces = get_bunny_faces()
    caylin_images = get_69caylin_images()
    
    if len(bunny_faces) == 0:
        print("Error: No se encontraron imagenes de bunny")
        return
    
    if len(caylin_images) == 0:
        print("Error: No se encontraron imagenes de 69caylin")
        return
    
    print(f"Encontradas {len(bunny_faces)} caras de bunny")
    print(f"Encontradas {len(caylin_images)} imagenes de 69caylin")
    
    # Seleccionar imagenes aleatorias
    bunny_img_path = random.choice(bunny_faces)
    caylin_img_path = random.choice(caylin_images)
    
    print(f"\nProcesando:")
    print(f"   Source (bunny): {bunny_img_path.name}")
    print(f"   Target (69caylin): {caylin_img_path.name}")
    
    # Cargar imagenes
    source_img = cv2.imread(str(bunny_img_path))
    target_img = cv2.imread(str(caylin_img_path))
    
    if source_img is None or target_img is None:
        print("Error cargando imagenes")
        return
    
    # Inicializar pipeline ULTRA con todas las mejoras
    print("\nInicializando pipeline ULTRA (37 tecnicas, 31 pasos)...")
    pipeline = FaceSwapPipeline(
        use_advanced_enhancements=True,
        quality_mode='ultra'  # Usa blend_ultra_advanced + AdvancedEnhancements
    )
    
    # Procesar
    print("\nProcesando con pipeline completo...")
    print("   - Deteccion facial")
    print("   - Extraccion de landmarks")
    print("   - Analisis facial")
    print("   - Correccion de color")
    print("   - Blending ultra-avanzado")
    print("   - 31 pasos de mejoras avanzadas")
    print("   - Post-procesamiento ultra-final")
    
    try:
        result = pipeline.process(source_img, target_img)
        
        # Guardar resultado
        output_dir = Path("face_swap_results_advanced")
        output_dir.mkdir(exist_ok=True)
        
        output_filename = f"advanced_{caylin_img_path.stem}.jpg"
        output_path = output_dir / output_filename
        cv2.imwrite(str(output_path), result)
        
        print(f"\nProcesamiento completado!")
        print(f"Resultado guardado en: {output_path}")
        print(f"\nTecnicas aplicadas:")
        print(f"   - Blending ultra-avanzado (4 tecnicas combinadas)")
        print(f"   - 31 pasos de mejoras avanzadas")
        print(f"   - Post-procesamiento ultra-final (5 pasos)")
        print(f"   - Total: 37 tecnicas avanzadas")
        print(f"\nAbre la imagen para ver el resultado con maxima calidad!")
        
    except Exception as e:
        print(f"\nError durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()








