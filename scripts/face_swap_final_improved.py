"""
Face Swap Final Mejorado - Versión Definitiva
==============================================
Combina todas las mejoras para resultados de máxima calidad
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import sys
import io
import random

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Intentar importar el modelo entrenado
try:
    from face_swap_simple import SimpleFaceSwapPipeline
    MODEL_AVAILABLE = True
except:
    MODEL_AVAILABLE = False

from face_swap_ultra_quality import UltraQualityFaceSwap


class FinalImprovedFaceSwap:
    """Face swap final que combina todas las técnicas mejoradas."""
    
    def __init__(self, use_model: bool = True):
        self.use_model = use_model and MODEL_AVAILABLE
        
        # Inicializar pipeline de modelo si está disponible
        if self.use_model:
            try:
                model_path = Path("face_swap_simple_model.pth")
                if model_path.exists():
                    self.model_pipeline = SimpleFaceSwapPipeline(model_path=str(model_path))
                    print("✓ Modelo entrenado cargado")
                else:
                    self.use_model = False
                    print("⚠ Modelo no encontrado, usando algoritmo avanzado")
            except:
                self.use_model = False
        
        # Inicializar algoritmo ultra calidad
        self.ultra_quality = UltraQualityFaceSwap()
    
    def swap_faces(self, source_image: np.ndarray, target_image: np.ndarray) -> np.ndarray:
        """Intercambia caras usando el mejor método disponible."""
        if self.use_model:
            try:
                # Usar modelo entrenado primero
                result = self.model_pipeline.swap_faces(source_image, target_image)
                
                # Mejorar resultado con algoritmo ultra calidad
                # Detectar caras para aplicar mejoras selectivas
                source_rect = self.ultra_quality.detect_face(source_image)
                target_rect = self.ultra_quality.detect_face(target_image)
                
                if source_rect and target_rect:
                    # Aplicar mejoras de color y blending del algoritmo ultra
                    target_region, _ = self.ultra_quality.extract_face_region(
                        target_image, target_rect, expand=0.5
                    )
                    result_region, _ = self.ultra_quality.extract_face_region(
                        result, target_rect, expand=0.5
                    )
                    
                    # Crear máscara
                    mask_rect = (
                        int(target_region.shape[1] * 0.1),
                        int(target_region.shape[0] * 0.1),
                        int(target_region.shape[1] * 0.8),
                        int(target_region.shape[0] * 0.8)
                    )
                    mask = self.ultra_quality.create_advanced_mask(
                        target_region.shape[:2], mask_rect
                    )
                    
                    # Aplicar corrección de color avanzada
                    corrected = self.ultra_quality.advanced_color_correction(
                        result_region, target_region, mask
                    )
                    
                    # Blending mejorado
                    blended = self.ultra_quality.multi_scale_blending(
                        corrected, target_region, mask
                    )
                    
                    # Insertar de vuelta
                    x_exp = max(0, target_rect[0] - int(target_rect[2] * 0.5))
                    y_exp = max(0, target_rect[1] - int(target_rect[3] * 0.5))
                    h, w = blended.shape[:2]
                    result[y_exp:y_exp+h, x_exp:x_exp+w] = blended
                
                return result
            except Exception as e:
                print(f"⚠ Error usando modelo: {e}, usando algoritmo ultra calidad")
        
        # Fallback a algoritmo ultra calidad
        return self.ultra_quality.swap_faces(source_image, target_image)


def batch_final_improved_swap():
    """Procesa todas las imágenes con la versión final mejorada."""
    print("=" * 70)
    print("FACE SWAP FINAL MEJORADO: BUNNY -> 69CAYLIN")
    print("=" * 70)
    
    # Obtener imágenes
    bunny_dirs = [
        "instagram_downloads/bunnyrose.me",
        "instagram_downloads/bunnyrose.uwu",
        "instagram_downloads/bunnyy.rose_"
    ]
    
    all_bunny_faces = []
    for dir_path in bunny_dirs:
        dir_obj = Path(dir_path)
        if dir_obj.exists():
            jpg_files = list(dir_obj.glob("*.jpg"))
            all_bunny_faces.extend(jpg_files)
    
    caylin_dir = Path("instagram_downloads/69caylin")
    caylin_images = list(caylin_dir.glob("*.jpg")) if caylin_dir.exists() else []
    
    if len(all_bunny_faces) == 0 or len(caylin_images) == 0:
        print("Error: No se encontraron imagenes suficientes")
        return
    
    print(f"Encontradas {len(all_bunny_faces)} caras de bunny")
    print(f"Encontradas {len(caylin_images)} imagenes de 69caylin")
    
    # Crear carpeta de salida
    output_dir = Path("face_swap_results_bunny_to_69caylin")
    output_dir.mkdir(exist_ok=True)
    
    # Inicializar face swap final mejorado
    print("\nInicializando face swap final mejorado...")
    face_swapper = FinalImprovedFaceSwap(use_model=True)
    
    print(f"\nProcesando {len(caylin_images)} imagenes...")
    print("-" * 70)
    
    successful = 0
    failed = 0
    
    for idx, caylin_img_path in enumerate(caylin_images, 1):
        try:
            bunny_face_path = random.choice(all_bunny_faces)
            
            bunny_img = cv2.imread(str(bunny_face_path))
            caylin_img = cv2.imread(str(caylin_img_path))
            
            if bunny_img is None or caylin_img is None:
                failed += 1
                continue
            
            # Face swap con versión final mejorada
            result = face_swapper.swap_faces(bunny_img, caylin_img)
            
            # Post-procesamiento final adicional
            from batch_face_swap_improved import improve_face_swap_result
            result = improve_face_swap_result(result, bunny_img, caylin_img)
            
            # Guardar con máxima calidad
            output_filename = f"bunny_face_on_{caylin_img_path.stem}.jpg"
            output_path = output_dir / output_filename
            
            cv2.imwrite(str(output_path), result, 
                       [cv2.IMWRITE_JPEG_QUALITY, 100,
                        cv2.IMWRITE_JPEG_OPTIMIZE, 1])
            
            successful += 1
            if idx % 50 == 0:
                print(f"[{idx}/{len(caylin_images)}] Procesadas...")
            
        except Exception as e:
            print(f"Error en {caylin_img_path.name}: {e}")
            failed += 1
            continue
    
    print("\n" + "=" * 70)
    print("PROCESO COMPLETADO")
    print("=" * 70)
    print(f"Imagenes procesadas: {successful}")
    print(f"Errores: {failed}")
    print(f"Resultados en: {output_dir.absolute()}")
    print("\nMejoras aplicadas:")
    print("  - Modelo entrenado (si disponible)")
    print("  - Corrección de color avanzada")
    print("  - Blending multi-escala")
    print("  - Seamless cloning")
    print("  - Post-procesamiento mejorado")


if __name__ == "__main__":
    batch_final_improved_swap()








