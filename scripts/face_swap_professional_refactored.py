"""
Face Swap Professional - Versión Refactorizada
===============================================
Versión refactorizada usando los módulos refactorizados de face_swap_modules.
Elimina duplicación y usa la arquitectura mejorada.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, List
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Importar módulos refactorizados
try:
    from face_swap_modules import (
        FaceDetector,
        LandmarkExtractor,
        FaceAnalyzer,
        ColorCorrector,
        BlendingEngine,
        QualityEnhancer,
        PostProcessor,
        FaceSwapPipeline,
        AdvancedEnhancements,
        LandmarkFormatHandler,
        ImageProcessor
    )
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    print("⚠ face_swap_modules no disponible. Ejecutar desde directorio scripts/")
    print("   O instalar: pip install -e scripts/")


class ProfessionalFaceSwapRefactored:
    """
    Face swap profesional usando módulos refactorizados.
    
    Esta versión refactorizada:
    - Usa los módulos refactorizados (elimina duplicación)
    - Mantiene compatibilidad con la API original
    - Aprovecha optimizaciones y mejoras avanzadas
    """
    
    def __init__(self, use_advanced_enhancements: bool = True, quality_mode: str = 'high'):
        """
        Inicializa face swap profesional refactorizado.
        
        Args:
            use_advanced_enhancements: Si True, usa AdvancedEnhancements
            quality_mode: 'fast', 'high', 'ultra'
        """
        if not MODULES_AVAILABLE:
            raise ImportError("face_swap_modules no está disponible. Instalar dependencias.")
        
        # Inicializar componentes refactorizados
        self.detector = FaceDetector()
        self.extractor = LandmarkExtractor()
        self.analyzer = FaceAnalyzer()
        self.color_corrector = ColorCorrector()
        self.blending_engine = BlendingEngine()
        self.quality_enhancer = QualityEnhancer()
        self.post_processor = PostProcessor()
        
        # Pipeline completo (opcional, para uso directo)
        self.pipeline = FaceSwapPipeline(
            use_advanced_enhancements=use_advanced_enhancements,
            quality_mode=quality_mode
        )
        
        # Mejoras avanzadas (opcional)
        if use_advanced_enhancements:
            self.advanced_enhancer = AdvancedEnhancements()
        else:
            self.advanced_enhancer = None
        
        self.use_advanced = use_advanced_enhancements
        self.quality_mode = quality_mode
        
        print("✓ Face Swap Professional Refactorizado inicializado")
        print(f"  Modo de calidad: {quality_mode}")
        print(f"  Mejoras avanzadas: {'Sí' if use_advanced_enhancements else 'No'}")
    
    def detect_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detecta cara usando módulos refactorizados.
        
        Args:
            image: Imagen de entrada (BGR)
        
        Returns:
            Bounding box (x, y, width, height) o None
        """
        return self.detector.detect(image)
    
    def get_face_landmarks(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Obtiene landmarks faciales usando módulos refactorizados.
        
        Args:
            image: Imagen de entrada (BGR)
        
        Returns:
            Landmarks como np.ndarray o None
        """
        return self.extractor.detect(image)
    
    def swap_faces_professional(
        self, 
        source_image: np.ndarray, 
        target_image: np.ndarray,
        use_pipeline: bool = True
    ) -> Optional[np.ndarray]:
        """
        Intercambia caras usando método profesional refactorizado.
        
        Args:
            source_image: Imagen con cara fuente
            target_image: Imagen donde se colocará la cara
            use_pipeline: Si True, usa FaceSwapPipeline completo
        
        Returns:
            Imagen resultante o None si falla
        """
        if use_pipeline:
            # Usar pipeline completo (más simple y optimizado)
            try:
                return self.pipeline.process(source_image, target_image)
            except Exception as e:
                print(f"Error en pipeline: {e}")
                return None
        else:
            # Proceso manual paso a paso (más control)
            return self._swap_faces_manual(source_image, target_image)
    
    def _swap_faces_manual(
        self,
        source_image: np.ndarray,
        target_image: np.ndarray
    ) -> Optional[np.ndarray]:
        """
        Proceso manual de face swap (paso a paso).
        
        Args:
            source_image: Imagen fuente
            target_image: Imagen objetivo
        
        Returns:
            Imagen resultante o None
        """
        try:
            # 1. Detección
            source_bbox = self.detector.detect(source_image)
            target_bbox = self.detector.detect(target_image)
            
            if source_bbox is None or target_bbox is None:
                print("⚠ No se detectaron caras en una o ambas imágenes")
                return None
            
            # 2. Extracción de landmarks
            source_landmarks = self.extractor.detect(source_image)
            target_landmarks = self.extractor.detect(target_image)
            
            if source_landmarks is None or target_landmarks is None:
                print("⚠ No se pudieron extraer landmarks")
                return None
            
            # 3. Análisis facial (opcional)
            source_regions = self.analyzer.analyze_face_regions(source_image, source_landmarks)
            target_regions = self.analyzer.analyze_face_regions(target_image, target_landmarks)
            
            # 4. Extraer caras
            source_face = self._extract_face_region(source_image, source_bbox)
            target_face = self._extract_face_region(target_image, target_bbox)
            
            # 5. Redimensionar
            source_face_resized = cv2.resize(
                source_face, 
                (target_face.shape[1], target_face.shape[0]),
                interpolation=cv2.INTER_LANCZOS4
            )
            
            # 6. Crear máscara
            mask = self._create_face_mask(target_face.shape[:2])
            
            # 7. Corrección de color
            source_corrected = self.color_corrector.correct_color_dual(
                source_face_resized, target_face, mask
            )
            
            # 8. Blending
            if self.quality_mode == 'ultra':
                blended = self.blending_engine.blend_ultra_advanced(
                    source_corrected, target_face, mask
                )
            else:
                blended = self.blending_engine.blend_advanced(
                    source_corrected, target_face, mask
                )
            
            # 9. Mejora de calidad
            if self.quality_mode != 'fast':
                enhanced = self.quality_enhancer.enhance_facial_features(
                    blended, target_landmarks
                )
            else:
                enhanced = blended
            
            # 10. Post-procesamiento
            if self.quality_mode == 'ultra':
                final = self.post_processor.ultra_final_enhancement(enhanced, mask)
            else:
                final = self.post_processor.advanced_post_processing(
                    enhanced, target_face, mask
                )
            
            # 11. Mejoras avanzadas (si está habilitado)
            if self.use_advanced and self.advanced_enhancer:
                final = self.advanced_enhancer.apply_all_enhancements(
                    source_face_resized, final, source_landmarks,
                    target_landmarks, mask
                )
            
            # 12. Integrar en imagen original
            result = self._integrate_face(target_image, final, target_bbox)
            
            return result
            
        except Exception as e:
            print(f"Error en swap manual: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_face_region(
        self, 
        image: np.ndarray, 
        bbox: Tuple[int, int, int, int]
    ) -> np.ndarray:
        """Extrae región facial con padding."""
        x, y, w, h = bbox
        
        # Padding del 20%
        padding = int(min(w, h) * 0.2)
        x_start = max(0, x - padding)
        y_start = max(0, y - padding)
        x_end = min(image.shape[1], x + w + padding)
        y_end = min(image.shape[0], y + h + padding)
        
        return image[y_start:y_end, x_start:x_end]
    
    def _create_face_mask(self, shape: Tuple[int, int]) -> np.ndarray:
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
    
    def _integrate_face(
        self,
        target_image: np.ndarray,
        face: np.ndarray,
        bbox: Tuple[int, int, int, int]
    ) -> np.ndarray:
        """Integra cara procesada en imagen objetivo."""
        result = target_image.copy()
        x, y, w, h = bbox
        
        # Ajustar tamaño si es necesario
        if face.shape[:2] != (h, w):
            face = cv2.resize(face, (w, h), interpolation=cv2.INTER_LANCZOS4)
        
        # Crear máscara de integración
        mask_integration = self._create_integration_mask((h, w))
        mask_3d = ImageProcessor.create_3d_mask(mask_integration)
        
        # Integrar con blending suave
        result[y:y+h, x:x+w] = (
            result[y:y+h, x:x+w].astype(np.float32) * (1 - mask_3d) +
            face.astype(np.float32) * mask_3d
        ).astype(np.uint8)
        
        return result
    
    def _create_integration_mask(self, shape: Tuple[int, int]) -> np.ndarray:
        """Crea máscara para integración suave."""
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
    
    def final_save_enhancement(self, image: np.ndarray) -> np.ndarray:
        """
        Mejora final antes de guardar (compatibilidad con API original).
        
        Args:
            image: Imagen a mejorar
        
        Returns:
            Imagen mejorada
        """
        return self.post_processor.final_save_enhancement(image)


def batch_professional_swap_refactored(
    source_dir: str,
    target_dir: str,
    output_dir: str = "face_swap_results_refactored",
    quality_mode: str = 'high',
    use_advanced: bool = True
):
    """
    Procesa imágenes en lote usando versión refactorizada.
    
    Args:
        source_dir: Directorio con imágenes fuente
        target_dir: Directorio con imágenes objetivo
        output_dir: Directorio de salida
        quality_mode: 'fast', 'high', 'ultra'
        use_advanced: Si True, usa mejoras avanzadas
    """
    if not MODULES_AVAILABLE:
        print("❌ face_swap_modules no disponible")
        return
    
    print("=" * 70)
    print("FACE SWAP PROFESIONAL REFACTORIZADO - PROCESAMIENTO POR LOTES")
    print("=" * 70)
    
    # Obtener imágenes
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    if not source_path.exists():
        print(f"❌ Directorio fuente no existe: {source_dir}")
        return
    
    if not target_path.exists():
        print(f"❌ Directorio objetivo no existe: {target_dir}")
        return
    
    source_images = list(source_path.glob("*.jpg")) + list(source_path.glob("*.png"))
    target_images = list(target_path.glob("*.jpg")) + list(target_path.glob("*.png"))
    
    if len(source_images) == 0:
        print(f"❌ No se encontraron imágenes en: {source_dir}")
        return
    
    if len(target_images) == 0:
        print(f"❌ No se encontraron imágenes en: {target_dir}")
        return
    
    print(f"✓ Encontradas {len(source_images)} imágenes fuente")
    print(f"✓ Encontradas {len(target_images)} imágenes objetivo")
    
    # Crear carpeta de salida
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Inicializar face swap refactorizado
    print(f"\nInicializando face swap (modo: {quality_mode})...")
    face_swapper = ProfessionalFaceSwapRefactored(
        use_advanced_enhancements=use_advanced,
        quality_mode=quality_mode
    )
    
    print(f"\nProcesando {len(target_images)} imágenes...")
    print("-" * 70)
    
    successful = 0
    failed = 0
    
    import random
    
    for idx, target_img_path in enumerate(target_images, 1):
        try:
            # Seleccionar imagen fuente aleatoria
            source_img_path = random.choice(source_images)
            
            source_img = cv2.imread(str(source_img_path))
            target_img = cv2.imread(str(target_img_path))
            
            if source_img is None or target_img is None:
                print(f"⚠ Error cargando imágenes: {target_img_path.name}")
                failed += 1
                continue
            
            # Face swap usando pipeline
            result = face_swapper.swap_faces_professional(
                source_img, 
                target_img,
                use_pipeline=True
            )
            
            if result is None:
                print(f"⚠ Falló procesamiento: {target_img_path.name}")
                failed += 1
                continue
            
            # Mejora final
            result = face_swapper.final_save_enhancement(result)
            
            # Guardar
            output_filename = f"swapped_{target_img_path.stem}.jpg"
            output_file = output_path / output_filename
            
            cv2.imwrite(
                str(output_file),
                result,
                [cv2.IMWRITE_JPEG_QUALITY, 100, cv2.IMWRITE_JPEG_OPTIMIZE, 1]
            )
            
            successful += 1
            
            if idx % 10 == 0:
                print(f"  Procesadas: {idx}/{len(target_images)} (✓ {successful}, ✗ {failed})")
                
        except Exception as e:
            print(f"✗ Error procesando {target_img_path.name}: {e}")
            failed += 1
    
    print("-" * 70)
    print(f"✅ Completado: {successful} exitosas, {failed} fallidas")
    print(f"📁 Resultados guardados en: {output_dir}")
    print("=" * 70)


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Face Swap Professional Refactorizado'
    )
    parser.add_argument('source', type=str, help='Ruta a imagen fuente')
    parser.add_argument('target', type=str, help='Ruta a imagen objetivo')
    parser.add_argument('-o', '--output', type=str, default='result_refactored.jpg',
                       help='Ruta de salida (default: result_refactored.jpg)')
    parser.add_argument('-q', '--quality', type=str, choices=['fast', 'high', 'ultra'],
                       default='high', help='Modo de calidad (default: high)')
    parser.add_argument('--no-advanced', action='store_true',
                       help='Deshabilitar mejoras avanzadas')
    parser.add_argument('--batch', action='store_true',
                       help='Modo batch: procesar directorios')
    parser.add_argument('--source-dir', type=str,
                       help='Directorio con imágenes fuente (modo batch)')
    parser.add_argument('--target-dir', type=str,
                       help='Directorio con imágenes objetivo (modo batch)')
    parser.add_argument('--output-dir', type=str, default='face_swap_results_refactored',
                       help='Directorio de salida (modo batch)')
    
    args = parser.parse_args()
    
    if not MODULES_AVAILABLE:
        print("❌ face_swap_modules no disponible")
        print("   Asegúrate de estar en el directorio scripts/ o instalar módulos")
        sys.exit(1)
    
    if args.batch:
        # Modo batch
        if not args.source_dir or not args.target_dir:
            print("❌ Modo batch requiere --source-dir y --target-dir")
            sys.exit(1)
        
        batch_professional_swap_refactored(
            args.source_dir,
            args.target_dir,
            args.output_dir,
            quality_mode=args.quality,
            use_advanced=not args.no_advanced
        )
    else:
        # Modo single
        source_image = cv2.imread(args.source)
        target_image = cv2.imread(args.target)
        
        if source_image is None:
            print(f"❌ No se pudo cargar imagen fuente: {args.source}")
            sys.exit(1)
        
        if target_image is None:
            print(f"❌ No se pudo cargar imagen objetivo: {args.target}")
            sys.exit(1)
        
        print(f"Procesando face swap (modo: {args.quality})...")
        
        face_swapper = ProfessionalFaceSwapRefactored(
            use_advanced_enhancements=not args.no_advanced,
            quality_mode=args.quality
        )
        
        result = face_swapper.swap_faces_professional(source_image, target_image)
        
        if result is None:
            print("❌ Error en procesamiento")
            sys.exit(1)
        
        # Mejora final
        result = face_swapper.final_save_enhancement(result)
        
        # Guardar
        cv2.imwrite(
            args.output,
            result,
            [cv2.IMWRITE_JPEG_QUALITY, 100, cv2.IMWRITE_JPEG_OPTIMIZE, 1]
        )
        
        print(f"✅ Resultado guardado en: {args.output}")


if __name__ == '__main__':
    main()







