"""
Face Swap Pipeline Completo - Usando Módulos Refactorizados
============================================================
Pipeline completo de face swap usando todos los módulos refactorizados.
Demuestra la integración completa de todos los componentes.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict
import sys

# Importar todos los módulos refactorizados (imports relativos para evitar circular)
from .face_detector import FaceDetector
from .landmark_extractor import LandmarkExtractor
from .face_analyzer import FaceAnalyzer
from .color_corrector import ColorCorrector
from .blending_engine import BlendingEngine
from .quality_enhancer import QualityEnhancer
from .post_processor import PostProcessor
from .advanced_enhancements import AdvancedEnhancements
from .base import LandmarkFormatHandler, ImageProcessor


class FaceSwapPipeline:
    """
    Pipeline completo de face swap usando módulos refactorizados.
    
    Características:
    - Detección automática con fallback
    - Extracción de landmarks con fallback
    - Análisis facial completo
    - Corrección de color avanzada
    - Blending ultra-avanzado
    - Mejora de calidad perceptual
    - Post-procesamiento completo
    - Mejoras avanzadas opcionales
    """
    
    def __init__(self, use_advanced_enhancements: bool = True, 
                 quality_mode: str = 'high'):
        """
        Inicializa el pipeline.
        
        Args:
            use_advanced_enhancements: Si True, usa AdvancedEnhancements
            quality_mode: 'fast', 'high', 'ultra'
        """
        # Inicializar componentes principales
        self.detector = FaceDetector()
        self.extractor = LandmarkExtractor()
        self.analyzer = FaceAnalyzer()
        self.color_corrector = ColorCorrector()
        self.blending_engine = BlendingEngine()
        self.quality_enhancer = QualityEnhancer()
        self.post_processor = PostProcessor()
        
        # Mejoras avanzadas (opcional)
        self.use_advanced = use_advanced_enhancements
        if use_advanced_enhancements:
            self.advanced_enhancer = AdvancedEnhancements()
        else:
            self.advanced_enhancer = None
        
        # Configuración de calidad
        self.quality_mode = quality_mode
        self._setup_quality_config()
    
    def _setup_quality_config(self):
        """Configura parámetros según modo de calidad."""
        if self.quality_mode == 'fast':
            self.blend_method = 'multi_scale_blending'
            self.use_quality_enhancement = False
            self.use_post_processing = True
            self.use_advanced_enhancements = False
        elif self.quality_mode == 'high':
            self.blend_method = 'blend_advanced'
            self.use_quality_enhancement = True
            self.use_post_processing = True
            self.use_advanced_enhancements = False
        else:  # ultra
            self.blend_method = 'blend_ultra_advanced'
            self.use_quality_enhancement = True
            self.use_post_processing = True
            self.use_advanced_enhancements = True
    
    def process(self, source_image: np.ndarray, target_image: np.ndarray,
               source_face_bbox: Optional[Tuple[int, int, int, int]] = None,
               target_face_bbox: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        Procesa face swap completo.
        
        Args:
            source_image: Imagen con cara fuente
            target_image: Imagen donde se colocará la cara
            source_face_bbox: Bounding box de cara fuente (opcional, se detecta si None)
            target_face_bbox: Bounding box de cara objetivo (opcional, se detecta si None)
        
        Returns:
            Imagen resultante con face swap
        """
        # Validación de inputs
        if not isinstance(source_image, np.ndarray):
            raise TypeError("source_image debe ser np.ndarray")
        if not isinstance(target_image, np.ndarray):
            raise TypeError("target_image debe ser np.ndarray")
        
        if source_image.dtype != np.uint8:
            raise ValueError("source_image debe ser uint8")
        if target_image.dtype != np.uint8:
            raise ValueError("target_image debe ser uint8")
        
        if len(source_image.shape) != 3 or source_image.shape[2] != 3:
            raise ValueError("source_image debe ser imagen BGR (H, W, 3)")
        if len(target_image.shape) != 3 or target_image.shape[2] != 3:
            raise ValueError("target_image debe ser imagen BGR (H, W, 3)")
        
        if source_image.size == 0:
            raise ValueError("source_image no puede estar vacío")
        if target_image.size == 0:
            raise ValueError("target_image no puede estar vacío")
        
        try:
            # 1. Detección de caras
            if source_face_bbox is None:
                source_face_bbox = self.detector.detect(source_image)
            if target_face_bbox is None:
                target_face_bbox = self.detector.detect(target_image)
            
            if source_face_bbox is None or target_face_bbox is None:
                raise ValueError("No se detectaron caras en una o ambas imágenes")
            
            # 2. Extracción de landmarks
            source_landmarks = self.extractor.detect(source_image)
            target_landmarks = self.extractor.detect(target_image)
            
            if source_landmarks is None or target_landmarks is None:
                raise ValueError("No se pudieron extraer landmarks")
            
            # 3. Análisis facial (opcional pero recomendado)
            source_regions = self.analyzer.analyze_face_regions(source_image, source_landmarks)
            target_regions = self.analyzer.analyze_face_regions(target_image, target_landmarks)
            
            # 4. Extracción y alineación de caras
            source_face = self._extract_face_region(source_image, source_face_bbox)
            target_face = self._extract_face_region(target_image, target_face_bbox)
            
            # 5. Redimensionamiento
            source_face_resized = self._resize_face(source_face, target_face.shape)
            
            # 6. Creación de máscara
            mask = self._create_mask(source_face_resized.shape[:2])
            
            # 7. Corrección de color
            source_corrected = self.color_corrector.correct_color_dual(
                source_face_resized, target_face, mask
            )
            
            # 8. Blending
            blended = self._apply_blending(source_corrected, target_face, mask)
            
            # 9. Mejora de calidad (si está habilitado)
            if self.use_quality_enhancement:
                enhanced = self.quality_enhancer.enhance_facial_features(
                    blended, target_landmarks
                )
            else:
                enhanced = blended
            
            # 10. Post-procesamiento
            if self.use_post_processing:
                if self.quality_mode == 'ultra':
                    final = self.post_processor.ultra_final_enhancement(
                        enhanced, mask
                    )
                else:
                    final = self.post_processor.advanced_post_processing(
                        enhanced, target_face, mask
                    )
            else:
                final = enhanced
            
            # 11. Mejoras avanzadas (si está habilitado)
            if self.use_advanced_enhancements and self.advanced_enhancer:
                final = self.advanced_enhancer.apply_all_enhancements(
                    source_face_resized, final, source_landmarks, 
                    target_landmarks, mask
                )
            
            # 12. Integración en imagen original
            result = self._integrate_face(target_image, final, target_face_bbox)
            
            return result
            
        except Exception as e:
            print(f"Error en pipeline: {e}")
            raise
    
    def _extract_face_region(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """Extrae región facial de la imagen con padding."""
        x, y, w, h = bbox
        
        # Expandir región ligeramente (20% padding)
        padding = int(min(w, h) * 0.2)
        x_start = max(0, x - padding)
        y_start = max(0, y - padding)
        x_end = min(image.shape[1], x + w + padding)
        y_end = min(image.shape[0], y + h + padding)
        
        return image[y_start:y_end, x_start:x_end]
    
    def _resize_face(self, source_face: np.ndarray, target_shape: Tuple[int, int]) -> np.ndarray:
        """Redimensiona cara fuente al tamaño de la cara objetivo."""
        return cv2.resize(source_face, (target_shape[1], target_shape[0]), 
                         interpolation=cv2.INTER_LANCZOS4)
    
    def _create_mask(self, shape: Tuple[int, int]) -> np.ndarray:
        """Crea máscara elíptica para blending."""
        mask = np.zeros(shape, dtype=np.float32)
        center = (shape[1] // 2, shape[0] // 2)
        axes = (int(shape[1] * 0.45), int(shape[0] * 0.45))
        
        cv2.ellipse(mask, center, axes, 0, 0, 360, 1.0, -1)
        
        # Suavizar bordes progresivamente
        mask = cv2.GaussianBlur(mask, (21, 21), 0)
        mask = cv2.GaussianBlur(mask, (15, 15), 0)
        mask = cv2.GaussianBlur(mask, (9, 9), 0)
        
        return mask
    
    def _apply_blending(self, source: np.ndarray, target: np.ndarray, 
                       mask: np.ndarray) -> np.ndarray:
        """Aplica blending según método configurado."""
        if self.blend_method == 'multi_scale_blending':
            return self.blending_engine.multi_scale_blending(source, target, mask)
        elif self.blend_method == 'blend_advanced':
            return self.blending_engine.blend_advanced(source, target, mask)
        elif self.blend_method == 'blend_ultra_advanced':
            return self.blending_engine.blend_ultra_advanced(source, target, mask)
        else:
            return self.blending_engine.blend_advanced(source, target, mask)
    
    def _integrate_face(self, target_image: np.ndarray, face: np.ndarray, 
                       bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """Integra cara procesada en imagen objetivo."""
        result = target_image.copy()
        x, y, w, h = bbox
        
        # Ajustar tamaño si es necesario
        if face.shape[:2] != (h, w):
            face = cv2.resize(face, (w, h), interpolation=cv2.INTER_LANCZOS4)
        
        # Integrar con blending suave en bordes
        mask_integration = self._create_integration_mask((h, w))
        mask_3d = ImageProcessor.create_3d_mask(mask_integration)
        
        result[y:y+h, x:x+w] = (
            result[y:y+h, x:x+w].astype(np.float32) * (1 - mask_3d) +
            face.astype(np.float32) * mask_3d
        ).astype(np.uint8)
        
        return result
    
    def _create_integration_mask(self, shape: Tuple[int, int]) -> np.ndarray:
        """Crea máscara para integración suave en imagen original."""
        mask = np.ones(shape, dtype=np.float32)
        
        # Reducir opacidad en bordes
        border_size = min(shape) // 10
        for i in range(border_size):
            alpha = 1.0 - (i / border_size) * 0.3
            mask[i, :] = alpha
            mask[-i-1, :] = alpha
            mask[:, i] = alpha
            mask[:, -i-1] = alpha
        
        return mask
    
    def process_batch(self, source_image: np.ndarray, 
                     target_images: list, output_dir: Path) -> Dict[str, bool]:
        """
        Procesa múltiples imágenes objetivo con una cara fuente.
        
        Args:
            source_image: Imagen con cara fuente
            target_images: Lista de imágenes objetivo
            output_dir: Directorio de salida
        
        Returns:
            Dict con resultados: {filename: success}
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        results = {}
        
        for i, target_image in enumerate(target_images):
            try:
                result = self.process(source_image, target_image)
                
                output_path = output_dir / f"swapped_{i:04d}.jpg"
                cv2.imwrite(str(output_path), result, [cv2.IMWRITE_JPEG_QUALITY, 100])
                
                results[str(output_path)] = True
                print(f"✓ Procesado: {output_path.name}")
                
            except Exception as e:
                results[f"image_{i}"] = False
                print(f"✗ Error procesando imagen {i}: {e}")
        
        return results


def main():
    """Función principal para uso desde línea de comandos."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Face Swap Pipeline usando módulos refactorizados')
    parser.add_argument('source', type=str, help='Ruta a imagen fuente')
    parser.add_argument('target', type=str, help='Ruta a imagen objetivo')
    parser.add_argument('-o', '--output', type=str, default='output.jpg', 
                       help='Ruta de salida (default: output.jpg)')
    parser.add_argument('-q', '--quality', type=str, choices=['fast', 'high', 'ultra'],
                       default='high', help='Modo de calidad (default: high)')
    parser.add_argument('--no-advanced', action='store_true',
                       help='Deshabilitar mejoras avanzadas')
    
    args = parser.parse_args()
    
    # Cargar imágenes
    source_image = cv2.imread(args.source)
    target_image = cv2.imread(args.target)
    
    if source_image is None:
        print(f"Error: No se pudo cargar imagen fuente: {args.source}")
        return
    
    if target_image is None:
        print(f"Error: No se pudo cargar imagen objetivo: {args.target}")
        return
    
    # Crear pipeline
    pipeline = FaceSwapPipeline(
        use_advanced_enhancements=not args.no_advanced,
        quality_mode=args.quality
    )
    
    print(f"Procesando face swap (modo: {args.quality})...")
    
    # Procesar
    try:
        result = pipeline.process(source_image, target_image)
        
        # Guardar resultado
        cv2.imwrite(args.output, result, [cv2.IMWRITE_JPEG_QUALITY, 100])
        print(f"✓ Resultado guardado en: {args.output}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()








