"""
Batch Face Swap: Bunny caras a 69caylin cuerpos
================================================
Intercambia las caras de bunny a todas las imágenes de 69caylin
"""

import cv2
import numpy as np
from pathlib import Path
from face_swap_simple import SimpleFaceSwapPipeline
import random
import os
import sys
import io

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
    """Obtiene todas las imágenes de 69caylin."""
    caylin_dir = Path("instagram_downloads/69caylin")
    if not caylin_dir.exists():
        return []
    
    return list(caylin_dir.glob("*.jpg"))

def main():
    print("=" * 70)
    print("BATCH FACE SWAP: BUNNY CARAS -> 69CAYLIN CUERPOS")
    print("=" * 70)
    
    # Obtener imágenes
    print("\n📦 Cargando imágenes...")
    bunny_faces = get_bunny_faces()
    caylin_images = get_69caylin_images()
    
    if len(bunny_faces) == 0:
        print("❌ Error: No se encontraron imágenes de bunny")
        print("   Asegúrate de haber descargado las imágenes primero")
        return
    
    if len(caylin_images) == 0:
        print("❌ Error: No se encontraron imágenes de 69caylin")
        print("   Asegúrate de haber descargado las imágenes primero")
        return
    
    print(f"✓ Encontradas {len(bunny_faces)} caras de bunny")
    print(f"✓ Encontradas {len(caylin_images)} imágenes de 69caylin")
    
    # Crear carpeta de salida
    output_dir = Path("face_swap_results_bunny_to_69caylin")
    output_dir.mkdir(exist_ok=True)
    print(f"\n📁 Los resultados se guardarán en: {output_dir}")
    
    # Inicializar pipeline
    print("\n🔧 Inicializando pipeline de face swap...")
    model_path = "face_swap_simple_model.pth"
    pipeline = SimpleFaceSwapPipeline(
        model_path=model_path if Path(model_path).exists() else None
    )
    
    # Procesar cada imagen de 69caylin
    print(f"\n🔄 Procesando {len(caylin_images)} imágenes...")
    print("-" * 70)
    
    successful = 0
    failed = 0
    
    for idx, caylin_img_path in enumerate(caylin_images, 1):
        try:
            # Seleccionar una cara de bunny aleatoria
            bunny_face_path = random.choice(bunny_faces)
            
            # Cargar imágenes
            bunny_img = cv2.imread(str(bunny_face_path))
            caylin_img = cv2.imread(str(caylin_img_path))
            
            if bunny_img is None or caylin_img is None:
                print(f"⚠ [{idx}/{len(caylin_images)}] Error cargando imágenes: {caylin_img_path.name}")
                failed += 1
                continue
            
            # Hacer face swap
            result = pipeline.swap_faces(bunny_img, caylin_img)
            
            # Guardar resultado
            output_filename = f"bunny_face_on_{caylin_img_path.stem}.jpg"
            output_path = output_dir / output_filename
            cv2.imwrite(str(output_path), result)
            
            successful += 1
            print(f"[{idx}/{len(caylin_images)}] {caylin_img_path.name} -> {output_filename}")
            
        except Exception as e:
            print(f"❌ [{idx}/{len(caylin_images)}] Error procesando {caylin_img_path.name}: {e}")
            failed += 1
            continue
    
    # Resumen
    print("\n" + "=" * 70)
    print("✅ PROCESO COMPLETADO")
    print("=" * 70)
    print(f"✓ Imágenes procesadas exitosamente: {successful}")
    print(f"⚠ Imágenes con errores: {failed}")
    print(f"📁 Resultados guardados en: {output_dir.absolute()}")
    print("\n💡 Tip: Para mejores resultados, entrena el modelo primero:")
    print("   python face_swap_simple.py --mode train --image-dir instagram_downloads/bunnyrose.me --epochs 30")

if __name__ == "__main__":
    main()








