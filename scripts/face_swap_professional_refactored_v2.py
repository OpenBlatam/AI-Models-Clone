"""
Face Swap Professional - Versión Refactorizada V2
==================================================
Versión refactorizada usando módulos separados.
"""

import cv2
import numpy as np
from pathlib import Path
import sys
import io
import logging

# Importar módulos refactorizados
from professional_face_swap import ProfessionalFaceSwap

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def batch_professional_swap():
    """Procesa imágenes usando versión profesional refactorizada."""
    logger.info("=" * 70)
    logger.info("FACE SWAP PROFESIONAL: BUNNY -> 69CAYLIN (Refactorizado V2)")
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
    
    # Inicializar face swap profesional refactorizado
    logger.info("\nInicializando face swap profesional (refactorizado)...")
    face_swapper = ProfessionalFaceSwap()
    
    logger.info(f"\nProcesando {len(caylin_images)} imágenes...")
    logger.info("-" * 70)
    
    successful = 0
    failed = 0
    
    import random
    for idx, caylin_img_path in enumerate(caylin_images, 1):
        try:
            bunny_face_path = random.choice(all_bunny_faces)
            
            bunny_img = cv2.imread(str(bunny_face_path))
            caylin_img = cv2.imread(str(caylin_img_path))
            
            if bunny_img is None or caylin_img is None:
                failed += 1
                continue
            
            # Face swap profesional
            result = face_swapper.swap_faces_professional(bunny_img, caylin_img)
            
            # Guardar
            output_filename = f"bunny_face_on_{caylin_img_path.stem}.jpg"
            output_path = output_dir / output_filename
            
            cv2.imwrite(str(output_path), result,
                       [cv2.IMWRITE_JPEG_QUALITY, 100,
                        cv2.IMWRITE_JPEG_OPTIMIZE, 1])
            
            successful += 1
            if idx % 50 == 0:
                logger.info(f"Procesadas {idx}/{len(caylin_images)} imágenes...")
            
        except Exception as e:
            logger.error(f"Error procesando {caylin_img_path.name}: {e}")
            failed += 1
            continue
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ PROCESO COMPLETADO")
    logger.info("=" * 70)
    logger.info(f"✓ Imágenes procesadas exitosamente: {successful}")
    logger.info(f"⚠ Imágenes con errores: {failed}")
    logger.info(f"📁 Resultados guardados en: {output_dir.absolute()}")


if __name__ == "__main__":
    batch_professional_swap()






