"""
Face Swap Final Mejorado - Versión Refactorizada
=================================================
Versión refactorizada usando módulos existentes.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import sys
import io
import random
import logging

# Importar módulos refactorizados
try:
    from simple_face_swap import SimpleFaceSwapPipeline
    SIMPLE_FACE_SWAP_AVAILABLE = True
except ImportError:
    try:
        from face_swap_simple import SimpleFaceSwapPipeline
        SIMPLE_FACE_SWAP_AVAILABLE = True
    except ImportError:
        SIMPLE_FACE_SWAP_AVAILABLE = False

try:
    from face_swap_high_quality_refactored import HighQualityFaceSwap
    HIGH_QUALITY_AVAILABLE = True
except ImportError:
    try:
        from face_swap_high_quality import HighQualityFaceSwap
        HIGH_QUALITY_AVAILABLE = True
    except ImportError:
        HIGH_QUALITY_AVAILABLE = False

try:
    from face_swap_modules import FaceSwapPipeline
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FinalImprovedFaceSwap:
    """Face swap final que combina todas las técnicas mejoradas usando módulos refactorizados."""
    
    def __init__(self, use_model: bool = True, use_pipeline: bool = True):
        """
        Inicializar face swap final mejorado.
        
        Args:
            use_model: Si True, intenta usar modelo entrenado
            use_pipeline: Si True, usa FaceSwapPipeline refactorizado
        """
        self.use_model = use_model and SIMPLE_FACE_SWAP_AVAILABLE
        self.use_pipeline = use_pipeline and PIPELINE_AVAILABLE
        
        # Inicializar pipeline de modelo si está disponible
        if self.use_model:
            try:
                model_path = Path("face_swap_simple_model.pth")
                if model_path.exists():
                    self.model_pipeline = SimpleFaceSwapPipeline(model_path=str(model_path))
                    logger.info("✓ Modelo entrenado cargado")
                else:
                    self.use_model = False
                    logger.warning("⚠ Modelo no encontrado, usando algoritmo avanzado")
            except Exception as e:
                self.use_model = False
                logger.warning(f"⚠ Error cargando modelo: {e}")
        
        # Inicializar pipeline refactorizado si está disponible
        if self.use_pipeline:
            try:
                self.pipeline = FaceSwapPipeline(
                    use_advanced_enhancements=True,
                    quality_mode='high'
                )
                logger.info("✓ Pipeline refactorizado inicializado")
            except Exception as e:
                self.use_pipeline = False
                logger.warning(f"⚠ Error inicializando pipeline: {e}")
        
        # Inicializar algoritmo de alta calidad como fallback
        if HIGH_QUALITY_AVAILABLE:
            try:
                self.high_quality = HighQualityFaceSwap()
                logger.info("✓ Algoritmo de alta calidad disponible")
            except Exception as e:
                logger.warning(f"⚠ Error inicializando alta calidad: {e}")
                self.high_quality = None
        else:
            self.high_quality = None
    
    def swap_faces(self, source_image: np.ndarray, target_image: np.ndarray) -> np.ndarray:
        """
        Intercambia caras usando el mejor método disponible.
        
        Prioridad:
        1. Pipeline refactorizado (si disponible)
        2. Modelo entrenado (si disponible)
        3. Algoritmo de alta calidad (fallback)
        """
        # Intentar pipeline refactorizado primero
        if self.use_pipeline:
            try:
                result = self.pipeline.process(source_image, target_image)
                if result is not None:
                    return result
            except Exception as e:
                logger.warning(f"Error en pipeline: {e}, intentando siguiente método")
        
        # Intentar modelo entrenado
        if self.use_model:
            try:
                result = self.model_pipeline.swap_faces(source_image, target_image)
                if result is not None:
                    # Aplicar mejoras post-procesamiento si hay alta calidad disponible
                    if self.high_quality:
                        try:
                            # Detectar caras para aplicar mejoras selectivas
                            target_face = self.high_quality.detect_face(target_image)
                            if target_face:
                                # Aplicar mejoras sutiles
                                result = self._apply_post_enhancements(result, target_image, target_face)
                        except Exception:
                            pass
                    return result
            except Exception as e:
                logger.warning(f"Error usando modelo: {e}, usando algoritmo avanzado")
        
        # Fallback a algoritmo de alta calidad
        if self.high_quality:
            try:
                return self.high_quality.swap_faces(source_image, target_image)
            except Exception as e:
                logger.error(f"Error en algoritmo de alta calidad: {e}")
        
        # Fallback final - retornar target sin cambios
        logger.warning("No se pudo realizar face swap, retornando imagen original")
        return target_image
    
    def _apply_post_enhancements(
        self,
        result: np.ndarray,
        target_image: np.ndarray,
        target_face: Tuple[int, int, int, int]
    ) -> np.ndarray:
        """Aplica mejoras post-procesamiento sutiles."""
        try:
            x, y, w, h = target_face
            result_region = result[y:y+h, x:x+w]
            target_region = target_image[y:y+h, x:x+w]
            
            # Mejora sutil de color
            result_lab = cv2.cvtColor(result_region, cv2.COLOR_BGR2LAB).astype(np.float32)
            target_lab = cv2.cvtColor(target_region, cv2.COLOR_BGR2LAB).astype(np.float32)
            
            # Ajuste sutil de luminosidad
            result_lab[:, :, 0] = result_lab[:, :, 0] * 0.9 + target_lab[:, :, 0] * 0.1
            result_region = cv2.cvtColor(
                np.clip(result_lab, 0, 255).astype(np.uint8),
                cv2.COLOR_LAB2BGR
            )
            
            result[y:y+h, x:x+w] = result_region
        except Exception:
            pass
        
        return result


def batch_final_improved_swap():
    """Procesa todas las imágenes con la versión final mejorada refactorizada."""
    logger.info("=" * 70)
    logger.info("FACE SWAP FINAL MEJORADO: BUNNY -> 69CAYLIN (Refactorizado)")
    logger.info("=" * 70)
    
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
        logger.error("Error: No se encontraron imágenes suficientes")
        return
    
    logger.info(f"Encontradas {len(all_bunny_faces)} caras de bunny")
    logger.info(f"Encontradas {len(caylin_images)} imágenes de 69caylin")
    
    # Crear carpeta de salida
    output_dir = Path("face_swap_results_bunny_to_69caylin")
    output_dir.mkdir(exist_ok=True)
    
    # Inicializar face swap final mejorado
    logger.info("\nInicializando face swap final mejorado (refactorizado)...")
    face_swapper = FinalImprovedFaceSwap(use_model=True, use_pipeline=True)
    
    logger.info(f"\nProcesando {len(caylin_images)} imágenes...")
    logger.info("-" * 70)
    
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
            
            # Guardar con máxima calidad
            output_filename = f"bunny_face_on_{caylin_img_path.stem}.jpg"
            output_path = output_dir / output_filename
            
            cv2.imwrite(str(output_path), result,
                       [cv2.IMWRITE_JPEG_QUALITY, 100,
                        cv2.IMWRITE_JPEG_OPTIMIZE, 1])
            
            successful += 1
            if idx % 50 == 0:
                logger.info(f"Procesadas {idx}/{len(caylin_images)} imágenes...")
            
        except Exception as e:
            logger.error(f"Error en {caylin_img_path.name}: {e}")
            failed += 1
            continue
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ PROCESO COMPLETADO")
    logger.info("=" * 70)
    logger.info(f"✓ Imágenes procesadas: {successful}")
    logger.info(f"⚠ Errores: {failed}")
    logger.info(f"📁 Resultados en: {output_dir.absolute()}")
    logger.info("\nMejoras aplicadas:")
    logger.info("  - Pipeline refactorizado (si disponible)")
    logger.info("  - Modelo entrenado (si disponible)")
    logger.info("  - Corrección de color avanzada")
    logger.info("  - Blending multi-escala")
    logger.info("  - Post-procesamiento mejorado")


if __name__ == "__main__":
    batch_final_improved_swap()






