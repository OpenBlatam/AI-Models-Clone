"""
Guía de Integración - Módulos Refactorizados
============================================
Este script muestra cómo migrar scripts existentes para usar los módulos refactorizados.
"""

import cv2
import numpy as np
from pathlib import Path

# Importar módulos refactorizados
from face_swap_modules import (
    FaceDetector,
    LandmarkExtractor,
    FaceAnalyzer,
    ColorCorrector,
    BlendingEngine,
    QualityEnhancer,
    PostProcessor
)


class FaceSwapPipeline:
    """
    Pipeline completo de face swap usando módulos refactorizados.
    Ejemplo de cómo integrar los módulos en un script principal.
    """
    
    def __init__(self):
        """Inicializa todos los componentes del pipeline."""
        self.detector = FaceDetector()
        self.extractor = LandmarkExtractor()
        self.analyzer = FaceAnalyzer()
        self.color_corrector = ColorCorrector()
        self.blending_engine = BlendingEngine()
        self.quality_enhancer = QualityEnhancer()
        self.post_processor = PostProcessor()
    
    def process(self, source_image: np.ndarray, target_image: np.ndarray) -> np.ndarray:
        """
        Procesa face swap completo usando módulos refactorizados.
        
        Args:
            source_image: Imagen con cara fuente
            target_image: Imagen donde se colocará la cara
            
        Returns:
            Imagen resultante con face swap
        """
        # 1. Detección de caras
        source_face = self.detector.detect(source_image)
        target_face = self.detector.detect(target_image)
        
        if source_face is None or target_face is None:
            raise ValueError("No se detectaron caras en una o ambas imágenes")
        
        # 2. Extracción de landmarks
        source_landmarks = self.extractor.detect(source_image)
        target_landmarks = self.extractor.detect(target_image)
        
        if source_landmarks is None or target_landmarks is None:
            raise ValueError("No se pudieron extraer landmarks")
        
        # 3. Análisis facial (opcional, para mejor calidad)
        source_regions = self.analyzer.analyze_face_regions(source_image, source_landmarks)
        target_regions = self.analyzer.analyze_face_regions(target_image, target_landmarks)
        
        # 4. Extracción y alineación de caras
        source_face_aligned = self._extract_face_region(source_image, source_face)
        target_face_aligned = self._extract_face_region(target_image, target_face)
        
        # 5. Redimensionamiento
        source_face_resized = self._resize_face(source_face_aligned, target_face_aligned.shape)
        
        # 6. Creación de máscara
        mask = self._create_mask(source_face_resized.shape[:2])
        
        # 7. Corrección de color
        source_corrected = self.color_corrector.correct_color_dual(
            source_face_resized, target_face_aligned, mask
        )
        
        # 8. Blending
        blended = self.blending_engine.blend_advanced(
            source_corrected, target_face_aligned, mask
        )
        
        # 9. Mejora de calidad
        enhanced = self.quality_enhancer.enhance_facial_features(
            blended, target_landmarks
        )
        
        # 10. Post-procesamiento
        final = self.post_processor.advanced_post_processing(
            enhanced, target_face_aligned, mask
        )
        
        # 11. Integración en imagen original
        result = self._integrate_face(target_image, final, target_face)
        
        return result
    
    def _extract_face_region(self, image: np.ndarray, face_bbox: tuple) -> np.ndarray:
        """Extrae región facial de la imagen."""
        x, y, w, h = face_bbox
        # Expandir región ligeramente
        padding = int(min(w, h) * 0.2)
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(image.shape[1] - x, w + 2 * padding)
        h = min(image.shape[0] - y, h + 2 * padding)
        return image[y:y+h, x:x+w]
    
    def _resize_face(self, source_face: np.ndarray, target_shape: tuple) -> np.ndarray:
        """Redimensiona cara fuente al tamaño de la cara objetivo."""
        return cv2.resize(source_face, (target_shape[1], target_shape[0]), 
                         interpolation=cv2.INTER_LANCZOS4)
    
    def _create_mask(self, shape: tuple) -> np.ndarray:
        """Crea máscara elíptica para blending."""
        mask = np.zeros(shape, dtype=np.float32)
        center = (shape[1] // 2, shape[0] // 2)
        axes = (shape[1] // 2, shape[0] // 2)
        cv2.ellipse(mask, center, axes, 0, 0, 360, 1.0, -1)
        # Suavizar bordes
        mask = cv2.GaussianBlur(mask, (21, 21), 0)
        return mask
    
    def _integrate_face(self, target_image: np.ndarray, face: np.ndarray, 
                       bbox: tuple) -> np.ndarray:
        """Integra cara procesada en imagen objetivo."""
        result = target_image.copy()
        x, y, w, h = bbox
        # Ajustar tamaño si es necesario
        if face.shape[:2] != (h, w):
            face = cv2.resize(face, (w, h), interpolation=cv2.INTER_LANCZOS4)
        result[y:y+h, x:x+w] = face
        return result


def migrate_old_script_example():
    """
    Ejemplo de cómo migrar código antiguo a módulos refactorizados.
    """
    
    # ============================================
    # ANTES: Código antiguo (duplicado, sin estructura)
    # ============================================
    
    # Código antiguo típico:
    # - Detección manual con múltiples métodos
    # - Verificación de formatos de landmarks repetida
    # - Números mágicos dispersos
    # - Manejo de errores inconsistente
    
    # ============================================
    # DESPUÉS: Código refactorizado (limpio, modular)
    # ============================================
    
    # Inicializar componentes
    detector = FaceDetector()
    extractor = LandmarkExtractor()
    color_corrector = ColorCorrector()
    blending_engine = BlendingEngine()
    
    # Usar componentes
    image = cv2.imread("source.jpg")
    
    # Detección (con fallback automático)
    face = detector.detect(image)  # Antes: detector.detect_face(image)
    
    # Extracción (con fallback automático)
    landmarks = extractor.detect(image)  # Antes: extractor.get_landmarks(image)
    
    # Corrección de color (métodos mejorados)
    corrected = color_corrector.correct_color_dual(source, target, mask)
    
    # Blending (múltiples métodos disponibles)
    result = blending_engine.blend_advanced(source, target, mask)
    
    print("Migración completada!")


def batch_process_example():
    """
    Ejemplo de procesamiento por lotes usando módulos refactorizados.
    """
    pipeline = FaceSwapPipeline()
    
    source_dir = Path("source_faces")
    target_dir = Path("target_images")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    source_image = cv2.imread(str(source_dir / "source.jpg"))
    
    for target_path in target_dir.glob("*.jpg"):
        try:
            target_image = cv2.imread(str(target_path))
            result = pipeline.process(source_image, target_image)
            
            output_path = output_dir / f"swapped_{target_path.name}"
            cv2.imwrite(str(output_path), result)
            print(f"Procesado: {target_path.name}")
            
        except Exception as e:
            print(f"Error procesando {target_path.name}: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Guía de Integración - Módulos Refactorizados")
    print("=" * 60)
    print("\n1. Ejemplo de Pipeline Completo:")
    print("   pipeline = FaceSwapPipeline()")
    print("   result = pipeline.process(source_img, target_img)")
    print("\n2. Ejemplo de Migración:")
    print("   Ver función migrate_old_script_example()")
    print("\n3. Ejemplo de Procesamiento por Lotes:")
    print("   Ver función batch_process_example()")
    print("\n" + "=" * 60)








