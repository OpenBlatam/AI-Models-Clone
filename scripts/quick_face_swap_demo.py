"""
Demo Rápido de Face Swap
========================
Script para probar rápidamente el face swap con las imágenes descargadas.
"""

import cv2
import sys
from pathlib import Path
from face_swap_simple import SimpleFaceSwapPipeline

def main():
    print("=" * 60)
    print("DEMO RÁPIDO DE FACE SWAP")
    print("=" * 60)
    
    # Buscar imágenes en las carpetas descargadas
    download_dirs = [
        "instagram_downloads/bunnyrose.me",
        "instagram_downloads/bunnyrose.uwu",
        "instagram_downloads/bunnyy.rose_"
    ]
    
    images = []
    for dir_path in download_dirs:
        dir_obj = Path(dir_path)
        if dir_obj.exists():
            jpg_files = list(dir_obj.glob("*.jpg"))
            images.extend(jpg_files[:5])  # Tomar primeras 5 de cada carpeta
    
    if len(images) < 2:
        print("❌ Error: No se encontraron suficientes imágenes")
        print("   Descarga algunas imágenes primero con download_instagram_images.py")
        return
    
    print(f"\n✓ Encontradas {len(images)} imágenes")
    
    # Seleccionar dos imágenes aleatorias
    import random
    source_path = random.choice(images)
    target_path = random.choice(images)
    
    while source_path == target_path:
        target_path = random.choice(images)
    
    print(f"\n📸 Imagen fuente: {source_path.name}")
    print(f"📸 Imagen destino: {target_path.name}")
    
    # Inicializar pipeline
    print("\n🔧 Inicializando pipeline...")
    model_path = "face_swap_simple_model.pth"
    pipeline = SimpleFaceSwapPipeline(
        model_path=model_path if Path(model_path).exists() else None
    )
    
    # Cargar imágenes
    print("📥 Cargando imágenes...")
    source_img = cv2.imread(str(source_path))
    target_img = cv2.imread(str(target_path))
    
    if source_img is None or target_img is None:
        print("❌ Error: No se pudieron cargar las imágenes")
        return
    
    # Hacer face swap
    print("🔄 Realizando face swap...")
    result = pipeline.swap_faces(source_img, target_img)
    
    # Guardar resultado
    output_path = "face_swap_demo_result.jpg"
    cv2.imwrite(output_path, result)
    
    print(f"\n✅ ¡Completado!")
    print(f"💾 Resultado guardado en: {output_path}")
    print("\n💡 Tip: Para mejores resultados, entrena el modelo primero:")
    print("   python face_swap_simple.py --mode train --image-dir instagram_downloads/bunnyrose.me --epochs 30")

if __name__ == "__main__":
    main()








