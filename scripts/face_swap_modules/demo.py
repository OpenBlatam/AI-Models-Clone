"""
Script de Demostración Visual - Face Swap Modules
==================================================
Muestra visualmente los resultados de diferentes métodos y configuraciones.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, List, Tuple
import sys

from face_swap_modules import (
    FaceDetector, LandmarkExtractor, FaceAnalyzer,
    ColorCorrector, BlendingEngine, QualityEnhancer,
    PostProcessor, FaceSwapPipeline
)


class FaceSwapDemo:
    """Demostración visual de funcionalidades."""
    
    def __init__(self, source_path: str, target_path: str):
        """
        Inicializa la demostración.
        
        Args:
            source_path: Ruta a imagen fuente
            target_path: Ruta a imagen objetivo
        """
        self.source = cv2.imread(source_path)
        self.target = cv2.imread(target_path)
        
        if self.source is None:
            raise ValueError(f"No se pudo cargar imagen fuente: {source_path}")
        if self.target is None:
            raise ValueError(f"No se pudo cargar imagen objetivo: {target_path}")
        
        self.output_dir = Path("demo_output")
        self.output_dir.mkdir(exist_ok=True)
    
    def demo_detection(self) -> np.ndarray:
        """Demuestra detección facial."""
        print("🔍 Demostrando detección facial...")
        
        detector = FaceDetector()
        result = self.target.copy()
        
        # Detectar en ambas imágenes
        source_bbox = detector.detect(self.source)
        target_bbox = detector.detect(self.target)
        
        if source_bbox:
            x, y, w, h = source_bbox
            cv2.rectangle(self.source, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(self.source, "Source Face", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        if target_bbox:
            x, y, w, h = target_bbox
            cv2.rectangle(result, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(result, "Target Face", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Combinar imágenes
        combined = np.hstack([self.source, result])
        
        output_path = self.output_dir / "01_detection.jpg"
        cv2.imwrite(str(output_path), combined)
        print(f"  ✓ Guardado: {output_path}")
        
        return combined
    
    def demo_landmarks(self) -> np.ndarray:
        """Demuestra extracción de landmarks."""
        print("📍 Demostrando extracción de landmarks...")
        
        extractor = LandmarkExtractor()
        source_landmarks = extractor.detect(self.source)
        target_landmarks = extractor.detect(self.target)
        
        result_source = self.source.copy()
        result_target = self.target.copy()
        
        if source_landmarks is not None:
            for point in source_landmarks:
                x, y = int(point[0]), int(point[1])
                cv2.circle(result_source, (x, y), 2, (0, 255, 0), -1)
        
        if target_landmarks is not None:
            for point in target_landmarks:
                x, y = int(point[0]), int(point[1])
                cv2.circle(result_target, (x, y), 2, (0, 255, 0), -1)
        
        combined = np.hstack([result_source, result_target])
        
        output_path = self.output_dir / "02_landmarks.jpg"
        cv2.imwrite(str(output_path), combined)
        print(f"  ✓ Guardado: {output_path}")
        
        return combined
    
    def demo_color_correction(self) -> np.ndarray:
        """Demuestra corrección de color."""
        print("🎨 Demostrando corrección de color...")
        
        # Extraer caras
        detector = FaceDetector()
        source_bbox = detector.detect(self.source)
        target_bbox = detector.detect(self.target)
        
        if not source_bbox or not target_bbox:
            print("  ⚠ No se detectaron caras")
            return self.target
        
        source_face = self._extract_face(self.source, source_bbox)
        target_face = self._extract_face(self.target, target_bbox)
        
        # Redimensionar
        source_face = cv2.resize(source_face, (target_face.shape[1], target_face.shape[0]))
        
        # Crear máscara
        mask = np.ones((target_face.shape[0], target_face.shape[1]), dtype=np.float32) * 0.8
        
        # Aplicar corrección
        corrector = ColorCorrector()
        corrected_hist = corrector.correct_color_histogram(source_face, target_face, mask)
        corrected_lab = corrector.correct_color_lab(source_face, target_face, mask)
        corrected_dual = corrector.correct_color_dual(source_face, target_face, mask)
        
        # Combinar resultados
        row1 = np.hstack([source_face, target_face])
        row2 = np.hstack([corrected_hist, corrected_lab])
        row3 = np.hstack([corrected_dual, np.zeros_like(corrected_dual)])
        
        combined = np.vstack([row1, row2, row3])
        
        # Agregar etiquetas
        labels = ["Source", "Target", "Histogram", "LAB", "Dual", ""]
        h, w = combined.shape[:2]
        label_h = 30
        combined_with_labels = np.zeros((h + label_h, w, 3), dtype=np.uint8)
        combined_with_labels[label_h:, :] = combined
        
        for i, label in enumerate(labels):
            x = i * (w // 3)
            cv2.putText(combined_with_labels, label, (x + 10, 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        output_path = self.output_dir / "03_color_correction.jpg"
        cv2.imwrite(str(output_path), combined_with_labels)
        print(f"  ✓ Guardado: {output_path}")
        
        return combined_with_labels
    
    def demo_blending(self) -> np.ndarray:
        """Demuestra diferentes métodos de blending."""
        print("🔄 Demostrando métodos de blending...")
        
        # Preparar imágenes
        detector = FaceDetector()
        source_bbox = detector.detect(self.source)
        target_bbox = detector.detect(self.target)
        
        if not source_bbox or not target_bbox:
            print("  ⚠ No se detectaron caras")
            return self.target
        
        source_face = self._extract_face(self.source, source_bbox)
        target_face = self._extract_face(self.target, target_bbox)
        source_face = cv2.resize(source_face, (target_face.shape[1], target_face.shape[0]))
        
        mask = np.ones((target_face.shape[0], target_face.shape[1]), dtype=np.float32) * 0.8
        
        # Aplicar diferentes métodos
        blender = BlendingEngine()
        
        result_multiscale = blender.multi_scale_blending(source_face, target_face, mask)
        result_advanced = blender.blend_advanced(source_face, target_face, mask)
        result_ultra = blender.blend_ultra_advanced(source_face, target_face, mask)
        
        # Combinar
        row1 = np.hstack([source_face, target_face])
        row2 = np.hstack([result_multiscale, result_advanced])
        row3 = np.hstack([result_ultra, np.zeros_like(result_ultra)])
        
        combined = np.vstack([row1, row2, row3])
        
        output_path = self.output_dir / "04_blending.jpg"
        cv2.imwrite(str(output_path), combined)
        print(f"  ✓ Guardado: {output_path}")
        
        return combined
    
    def demo_pipeline_modes(self) -> List[Tuple[str, np.ndarray]]:
        """Demuestra diferentes modos del pipeline."""
        print("🚀 Demostrando modos del pipeline...")
        
        results = []
        modes = ['fast', 'high', 'ultra']
        
        for mode in modes:
            print(f"  Procesando modo: {mode}...")
            try:
                pipeline = FaceSwapPipeline(
                    quality_mode=mode,
                    use_advanced_enhancements=(mode == 'ultra')
                )
                result = pipeline.process(self.source, self.target)
                results.append((mode, result))
                
                output_path = self.output_dir / f"05_pipeline_{mode}.jpg"
                cv2.imwrite(str(output_path), result, [cv2.IMWRITE_JPEG_QUALITY, 100])
                print(f"    ✓ Guardado: {output_path}")
            except Exception as e:
                print(f"    ⚠ Error en modo {mode}: {e}")
        
        return results
    
    def _extract_face(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """Extrae región facial."""
        x, y, w, h = bbox
        padding = int(min(w, h) * 0.2)
        x_start = max(0, x - padding)
        y_start = max(0, y - padding)
        x_end = min(image.shape[1], x + w + padding)
        y_end = min(image.shape[0], y + h + padding)
        return image[y_start:y_end, x_start:x_end]
    
    def run_all_demos(self):
        """Ejecuta todas las demostraciones."""
        print("=" * 60)
        print("🎬 INICIANDO DEMOSTRACIÓN VISUAL")
        print("=" * 60)
        print(f"Imagen fuente: {self.source.shape}")
        print(f"Imagen objetivo: {self.target.shape}")
        print(f"Directorio de salida: {self.output_dir}")
        print("=" * 60)
        print()
        
        # Ejecutar demos
        self.demo_detection()
        self.demo_landmarks()
        self.demo_color_correction()
        self.demo_blending()
        self.demo_pipeline_modes()
        
        print()
        print("=" * 60)
        print("✅ DEMOSTRACIÓN COMPLETADA")
        print(f"📁 Resultados guardados en: {self.output_dir}")
        print("=" * 60)


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Demostración visual de Face Swap Modules')
    parser.add_argument('source', type=str, help='Ruta a imagen fuente')
    parser.add_argument('target', type=str, help='Ruta a imagen objetivo')
    parser.add_argument('-o', '--output', type=str, default='demo_output',
                       help='Directorio de salida (default: demo_output)')
    
    args = parser.parse_args()
    
    try:
        demo = FaceSwapDemo(args.source, args.target)
        demo.output_dir = Path(args.output)
        demo.output_dir.mkdir(exist_ok=True)
        demo.run_all_demos()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()








