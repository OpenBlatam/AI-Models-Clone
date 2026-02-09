"""
Face Swap de Alta Calidad - Versi?n Refactorizada
==================================================
Versi?n refactorizada usando m?dulos existentes.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import sys
import io
import logging

# Importar módulos refactorizados
try:
    from face_swap_modules import (
        FaceDetector,
        LandmarkExtractor,
        ColorCorrector,
        BlendingEngine
    )
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    print("? M?dulos face_swap_modules no disponibles")

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


class HighQualityFaceSwap:
    """Face swap de alta calidad usando m?dulos refactorizados."""
    
    def __init__(self):
        """Inicializar face swap de alta calidad."""
        if not MODULES_AVAILABLE:
            logger.warning("M?dulos refactorizados no disponibles, usando fallback")
            # Fallback a OpenCV b?sico
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            self.eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_eye.xml'
            )
            self.use_modules = False
        else:
            self.detector = FaceDetector()
            self.landmark_extractor = LandmarkExtractor()
            self.color_corrector = ColorCorrector()
            self.blending_engine = BlendingEngine()
            self.use_modules = True
    
    def detect_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detecta cara usando el mejor m?todo disponible."""
        if self.use_modules:
            face_rect = self.detector.detect(image)
            if face_rect is not None:
                return face_rect
        else:
            # Fallback b?sico
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
            if len(faces) > 0:
                faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
                return tuple(faces[0])
        return None
    
    def get_face_landmarks(self, image: np.ndarray, face_rect) -> Optional[np.ndarray]:
        """Obtiene landmarks faciales."""
        if self.use_modules:
            landmarks = self.landmark_extractor.get_landmarks(image)
            return landmarks
        else:
            # Fallback b?sico - estimaci?n simple
            x, y, w, h = face_rect
            points = np.array([
                [x + w * 0.35, y + h * 0.35],  # Ojo izquierdo
                [x + w * 0.65, y + h * 0.35],  # Ojo derecho
                [x + w * 0.5, y + h * 0.6],    # Nariz
                [x + w * 0.3, y + h * 0.75],   # Boca izquierda
                [x + w * 0.7, y + h * 0.75],   # Boca derecha
            ])
            return points
    
    def swap_faces(self, source_image: np.ndarray, target_image: np.ndarray) -> np.ndarray:
        """Intercambia caras con alta calidad."""
        # Detectar caras
        source_face = self.detect_face(source_image)
        target_face = self.detect_face(target_image)
        
        if source_face is None or target_face is None:
            logger.warning("No se detectaron caras")
            return target_image
        
        # Obtener landmarks
        source_landmarks = self.get_face_landmarks(source_image, source_face)
        target_landmarks = self.get_face_landmarks(target_image, target_face)
        
        # Extraer regiones
        x, y, w, h = source_face
        source_region = source_image[y:y+h, x:x+w].copy()
        
        x, y, w, h = target_face
        target_region = target_image[y:y+h, x:x+w].copy()
        
        # Redimensionar source a target
        source_resized = cv2.resize(source_region, (target_region.shape[1], target_region.shape[0]),
                                   interpolation=cv2.INTER_LANCZOS4)
        
        # Crear m?scara
        h_mask, w_mask = target_region.shape[:2]
        mask = np.zeros((h_mask, w_mask), dtype=np.float32)
        cv2.ellipse(mask, (w_mask//2, h_mask//2), (int(w_mask*0.45), int(h_mask*0.55)), 0, 0, 360, 1.0, -1)
        mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=15, sigmaY=15)
        mask = np.clip(mask, 0, 1)
        
        # Corrección de color
        if self.use_modules:
            source_corrected = self.color_corrector.correct_color_dual(source_resized, target_region, mask)
        else:
            # Fallback b?sico
            source_lab = cv2.cvtColor(source_resized, cv2.COLOR_BGR2LAB).astype(np.float32)
            target_lab = cv2.cvtColor(target_region, cv2.COLOR_BGR2LAB).astype(np.float32)
            mask_3d = np.stack([mask] * 3, axis=2)
            
            source_mean = np.sum(source_lab * mask_3d, axis=(0, 1)) / (np.sum(mask) + 1e-6)
            target_mean = np.sum(target_lab * mask_3d, axis=(0, 1)) / (np.sum(mask) + 1e-6)
            
            source_corrected_lab = source_lab - source_mean + target_mean
            source_corrected = cv2.cvtColor(
                np.clip(source_corrected_lab, 0, 255).astype(np.uint8),
                cv2.COLOR_LAB2BGR
            )
        
        # Blending
        if self.use_modules:
            blended = self.blending_engine.blend_advanced(source_corrected, target_region, mask)
        else:
            # Fallback b?sico
            mask_3d = np.stack([mask] * 3, axis=2)
            blended = (source_corrected.astype(np.float32) * mask_3d + 
                      target_region.astype(np.float32) * (1 - mask_3d))
            blended = np.clip(blended, 0, 255).astype(np.uint8)
        
        # Insertar resultado
        result = target_image.copy()
        x, y, w, h = target_face
        result[y:y+h, x:x+w] = blended
        
        return result


def batch_high_quality_swap():
    """Procesa im?genes usando versi?n de alta calidad refactorizada."""
    logger.info("=" * 70)
    logger.info("FACE SWAP ALTA CALIDAD: BUNNY -> 69CAYLIN (Refactorizado)")
    logger.info("=" * 70)
    
    # Obtener im?genes
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
        logger.error("Error: No se encontraron im?genes suficientes")
        return
    
    logger.info(f"Encontradas {len(all_bunny_faces)} caras de bunny")
    logger.info(f"Encontradas {len(caylin_images)} im?genes de 69caylin")
    
    # Crear carpeta de salida
    output_dir = Path("face_swap_results_bunny_to_69caylin")
    output_dir.mkdir(exist_ok=True)
    
    # Inicializar face swap
    logger.info("\nInicializando face swap de alta calidad...")
    face_swapper = HighQualityFaceSwap()
    
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
            
            # Face swap
            result = face_swapper.swap_faces(bunny_img, caylin_img)
            
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
            logger.error(f"Error en {caylin_img_path.name}: {e}")
            failed += 1
            continue
    
    logger.info("\n" + "=" * 70)
    logger.info("? PROCESO COMPLETADO")
    logger.info("=" * 70)
    logger.info(f"? Im?genes procesadas: {successful}")
    logger.info(f"? Errores: {failed}")
    logger.info(f"?? Resultados en: {output_dir.absolute()}")


if __name__ == "__main__":
    batch_high_quality_swap()






