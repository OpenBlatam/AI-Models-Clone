"""
Ejemplo de uso del modelo Face Swap
===================================
Script simple para hacer face swap entre dos imágenes.
"""

import cv2
import sys
from pathlib import Path
from face_swap_model import FaceSwapPipeline

def main():
    # Rutas de ejemplo (puedes cambiarlas)
    source_image = "instagram_downloads/bunnyrose.me/2025-12-13_18-46-43_UTC_DSNtaPeDKLt.jpg"
    target_image = "instagram_downloads/bunnyy.rose_/2025-12-13_19-27-33_UTC_DSNyFSNAHcf.jpg"
    output_image = "face_swap_result.jpg"
    model_path = "face_swap_model.pth"  # None si no tienes modelo entrenado
    
    # Verificar que las imágenes existan
    if not Path(source_image).exists():
        print(f"Error: No se encontró la imagen fuente: {source_image}")
        print("Usa imágenes de la carpeta instagram_downloads o especifica otras rutas")
        return
    
    if not Path(target_image).exists():
        print(f"Error: No se encontró la imagen destino: {target_image}")
        return
    
    print("Inicializando pipeline de face swap...")
    pipeline = FaceSwapPipeline(model_path=model_path if Path(model_path).exists() else None)
    
    print(f"Cargando imágenes...")
    source_img = cv2.imread(source_image)
    target_img = cv2.imread(target_image)
    
    if source_img is None or target_img is None:
        print("Error: No se pudieron cargar las imágenes")
        return
    
    print("Realizando face swap...")
    result = pipeline.swap_faces(source_img, target_img, use_blending=True)
    
    print(f"Guardando resultado en {output_image}...")
    cv2.imwrite(output_image, result)
    
    print("¡Face swap completado!")
    print(f"Resultado guardado en: {output_image}")

if __name__ == "__main__":
    main()








