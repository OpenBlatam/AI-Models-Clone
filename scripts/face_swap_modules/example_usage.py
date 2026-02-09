"""
Ejemplo de Uso - Módulos Refactorizados de Face Swap
=====================================================
Este script demuestra cómo usar los módulos refactorizados de face swap
siguiendo las mejores prácticas y aprovechando la nueva arquitectura.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple

# Importar módulos refactorizados
from face_swap_modules import (
    FaceDetector,
    LandmarkExtractor,
    FaceAnalyzer,
    ColorCorrector,
    BlendingEngine,
    QualityEnhancer,
    PostProcessor,
    LandmarkFormatHandler,
    ImageProcessor
)


class FaceSwapPipeline:
    """
    Pipeline completo de face swap usando módulos refactorizados.
    
    Demuestra cómo los módulos refactorizados facilitan la creación
    de pipelines complejos con código limpio y mantenible.
    """
    
    def __init__(self):
        """Inicializar todos los componentes del pipeline."""
        self.detector = FaceDetector()
        self.extractor = LandmarkExtractor()
        self.analyzer = FaceAnalyzer()
        self.color_corrector = ColorCorrector()
        self.blender = BlendingEngine()
        self.enhancer = QualityEnhancer()
        self.post_processor = PostProcessor()
    
    def process_face_swap(self, source_image: np.ndarray, 
                         target_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Procesa un face swap completo usando todos los módulos.
        
        Args:
            source_image: Imagen con la cara fuente
            target_image: Imagen donde se colocará la cara
            
        Returns:
            Imagen resultante con el face swap aplicado
        """
        try:
            # 1. Detectar caras
            source_bbox = self.detector.detect(source_image)
            target_bbox = self.detector.detect(target_image)
            
            if source_bbox is None or target_bbox is None:
                print("⚠ No se detectaron caras en una o ambas imágenes")
                return None
            
            # 2. Extraer landmarks
            source_landmarks = self.extractor.detect(source_image)
            target_landmarks = self.extractor.detect(target_image)
            
            if source_landmarks is None or target_landmarks is None:
                print("⚠ No se pudieron extraer landmarks")
                return None
            
            # 3. Analizar características faciales
            source_features = self.analyzer.analyze_facial_features_deep(
                source_image, source_landmarks
            )
            target_features = self.analyzer.analyze_facial_features_deep(
                target_image, target_landmarks
            )
            
            # 4. Extraer región facial de la imagen fuente
            source_face = self._extract_face_region(source_image, source_bbox)
            
            # 5. Redimensionar para que coincida con el target
            target_face_size = (target_bbox[2], target_bbox[3])
            source_face_resized = cv2.resize(
                source_face, target_face_size, interpolation=cv2.INTER_LANCZOS4
            )
            
            # 6. Crear máscara para blending
            mask = self._create_face_mask(target_landmarks, target_image.shape[:2])
            
            # 7. Corregir color
            color_corrected = self.color_corrector.correct_color_dual(
                source_face_resized, target_image, mask
            )
            
            # 8. Aplicar blending avanzado
            blended = self.blender.blend_advanced(
                color_corrected, target_image, mask
            )
            
            # 9. Mejorar calidad
            enhanced = self.enhancer.enhance_perceptual_quality(blended)
            
            # 10. Post-procesamiento final
            result = self.post_processor.advanced_post_processing(
                enhanced, target_image, mask
            )
            
            return result
            
        except Exception as e:
            print(f"❌ Error en el pipeline: {e}")
            return None
    
    def _extract_face_region(self, image: np.ndarray, 
                           bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """Extraer región facial de la imagen."""
        x, y, w, h = bbox
        x, y = ImageProcessor.ensure_bounds(x, y, image.shape[1], image.shape[0])
        return image[y:y+h, x:x+w]
    
    def _create_face_mask(self, landmarks: np.ndarray, 
                         image_shape: Tuple[int, int]) -> np.ndarray:
        """Crear máscara facial usando landmarks."""
        if not LandmarkFormatHandler.is_valid_landmarks(landmarks):
            # Fallback: máscara elíptica simple
            h, w = image_shape
            mask = np.zeros((h, w), dtype=np.float32)
            center = (w // 2, h // 2)
            radius = min(w, h) // 3
            y_coords, x_coords = np.ogrid[:h, :w]
            dist = np.sqrt((x_coords - center[0])**2 + (y_coords - center[1])**2)
            mask = np.clip(1 - dist / radius, 0, 1)
            return cv2.GaussianBlur(mask, (21, 21), 0)
        
        # Usar landmarks para crear máscara más precisa
        h, w = image_shape
        mask = np.zeros((h, w), dtype=np.float32)
        
        # Obtener puntos clave usando el handler
        face_center = LandmarkFormatHandler.get_feature_point(landmarks, 'face_center')
        if face_center is not None:
            center = (int(face_center[0]), int(face_center[1]))
            # Estimar radio basado en distancia entre ojos
            left_eye = LandmarkFormatHandler.get_feature_point(landmarks, 'left_eye_center')
            right_eye = LandmarkFormatHandler.get_feature_point(landmarks, 'right_eye_center')
            if left_eye is not None and right_eye is not None:
                eye_distance = np.linalg.norm(right_eye - left_eye)
                radius = int(eye_distance * 1.5)
            else:
                radius = min(w, h) // 3
            
            y_coords, x_coords = np.ogrid[:h, :w]
            dist = np.sqrt((x_coords - center[0])**2 + (y_coords - center[1])**2)
            mask = np.clip(1 - dist / radius, 0, 1) ** 2
        
        return cv2.GaussianBlur(mask, (21, 21), 0)


def example_basic_usage():
    """Ejemplo básico de uso de módulos individuales."""
    print("=" * 60)
    print("Ejemplo 1: Uso Básico de Módulos Individuales")
    print("=" * 60)
    
    # Cargar imagen de ejemplo
    image_path = Path("path/to/image.jpg")
    if not image_path.exists():
        print("⚠ Imagen no encontrada. Usa una ruta válida.")
        return
    
    image = cv2.imread(str(image_path))
    if image is None:
        print("❌ No se pudo cargar la imagen")
        return
    
    # 1. Detectar cara
    detector = FaceDetector()
    bbox = detector.detect(image)
    if bbox:
        print(f"✅ Cara detectada: {bbox}")
    else:
        print("❌ No se detectó cara")
        return
    
    # 2. Extraer landmarks
    extractor = LandmarkExtractor()
    landmarks = extractor.detect(image)
    if landmarks is not None:
        format_type = LandmarkFormatHandler.get_landmark_format(landmarks)
        print(f"✅ Landmarks extraídos: {len(landmarks)} puntos (formato: {format_type})")
    else:
        print("❌ No se pudieron extraer landmarks")
        return
    
    # 3. Analizar características
    analyzer = FaceAnalyzer()
    features = analyzer.analyze_facial_features_deep(image, landmarks)
    print(f"✅ Características analizadas: {list(features.keys())}")


def example_advanced_usage():
    """Ejemplo avanzado usando utilidades compartidas."""
    print("\n" + "=" * 60)
    print("Ejemplo 2: Uso Avanzado con Utilidades Compartidas")
    print("=" * 60)
    
    # Simular landmarks (en uso real vendrían del extractor)
    # landmarks = extractor.detect(image)
    
    # Ejemplo de uso de LandmarkFormatHandler
    print("\n📋 Uso de LandmarkFormatHandler:")
    print("  - Verificar formato de landmarks")
    print("  - Obtener regiones específicas (ojos, boca, etc.)")
    print("  - Obtener puntos individuales")
    
    # Ejemplo de uso de ImageProcessor
    print("\n🖼️  Uso de ImageProcessor:")
    print("  - Crear máscaras 3D desde 2D")
    print("  - Convertir tipos de datos")
    print("  - Validar coordenadas")
    
    # Ejemplo práctico
    mask_2d = np.ones((100, 100), dtype=np.float32) * 0.5
    mask_3d = ImageProcessor.create_3d_mask(mask_2d)
    print(f"  ✅ Máscara 2D {mask_2d.shape} → 3D {mask_3d.shape}")


def example_pipeline_usage():
    """Ejemplo de uso del pipeline completo."""
    print("\n" + "=" * 60)
    print("Ejemplo 3: Pipeline Completo de Face Swap")
    print("=" * 60)
    
    # Crear pipeline
    pipeline = FaceSwapPipeline()
    
    # Cargar imágenes
    source_path = Path("path/to/source.jpg")
    target_path = Path("path/to/target.jpg")
    
    if not source_path.exists() or not target_path.exists():
        print("⚠ Imágenes no encontradas. Usa rutas válidas.")
        print("   El pipeline está listo para usar cuando tengas las imágenes.")
        return
    
    source_image = cv2.imread(str(source_path))
    target_image = cv2.imread(str(target_path))
    
    if source_image is None or target_image is None:
        print("❌ No se pudieron cargar las imágenes")
        return
    
    # Procesar face swap
    result = pipeline.process_face_swap(source_image, target_image)
    
    if result is not None:
        # Guardar resultado
        output_path = Path("output/face_swap_result.jpg")
        output_path.parent.mkdir(exist_ok=True)
        cv2.imwrite(str(output_path), result)
        print(f"✅ Face swap completado. Resultado guardado en: {output_path}")
    else:
        print("❌ No se pudo completar el face swap")


def example_error_handling():
    """Ejemplo de manejo de errores mejorado."""
    print("\n" + "=" * 60)
    print("Ejemplo 4: Manejo de Errores Mejorado")
    print("=" * 60)
    
    # Los módulos refactorizados tienen manejo de errores consistente
    detector = FaceDetector()
    
    # Intentar detectar en imagen inválida
    invalid_image = np.zeros((100, 100, 3), dtype=np.uint8)
    result = detector.detect(invalid_image)
    
    if result is None:
        print("✅ Manejo de errores funcionando: retorna None en caso de error")
    else:
        print("⚠ Se detectó algo inesperado")


def main():
    """Función principal con todos los ejemplos."""
    print("\n" + "=" * 60)
    print("EJEMPLOS DE USO - MÓDULOS REFACTORIZADOS")
    print("=" * 60)
    print("\nEstos ejemplos demuestran cómo usar los módulos refactorizados")
    print("siguiendo las mejores prácticas y aprovechando la nueva arquitectura.\n")
    
    # Ejecutar ejemplos
    example_basic_usage()
    example_advanced_usage()
    example_pipeline_usage()
    example_error_handling()
    
    print("\n" + "=" * 60)
    print("✅ Todos los ejemplos completados")
    print("=" * 60)
    print("\n💡 Tips:")
    print("  - Los módulos son 100% compatibles hacia atrás")
    print("  - Puedes usar los métodos antiguos (detect_face, get_landmarks)")
    print("  - O los nuevos métodos (detect) con mejor estructura")
    print("  - Las utilidades (LandmarkFormatHandler, ImageProcessor) son opcionales")
    print("    pero muy útiles para código más limpio")


if __name__ == "__main__":
    main()








