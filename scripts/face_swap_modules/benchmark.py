"""
Benchmark de Rendimiento - Face Swap Modules
============================================
Script para medir y comparar el rendimiento de los módulos refactorizados.
"""

import cv2
import numpy as np
import time
from pathlib import Path
from typing import Dict, List, Tuple
import sys

from face_swap_modules import (
    FaceDetector, LandmarkExtractor, FaceAnalyzer,
    ColorCorrector, BlendingEngine, QualityEnhancer,
    PostProcessor, AdvancedEnhancements, FaceSwapPipeline
)
from face_swap_modules.optimizations import is_numba_available


class PerformanceBenchmark:
    """Benchmark de rendimiento para módulos de face swap."""
    
    def __init__(self, test_image_path: str = None):
        """
        Inicializa el benchmark.
        
        Args:
            test_image_path: Ruta a imagen de prueba (opcional)
        """
        self.test_image = None
        if test_image_path and Path(test_image_path).exists():
            self.test_image = cv2.imread(test_image_path)
        else:
            # Crear imagen de prueba sintética
            self.test_image = self._create_test_image()
        
        self.results = {}
    
    def _create_test_image(self, size: Tuple[int, int] = (640, 480)) -> np.ndarray:
        """Crea una imagen de prueba sintética."""
        image = np.random.randint(0, 255, (*size, 3), dtype=np.uint8)
        # Agregar un "rostro" simulado (rectángulo)
        cv2.rectangle(image, (200, 150), (440, 350), (200, 180, 160), -1)
        return image
    
    def benchmark_detection(self, iterations: int = 10) -> Dict:
        """Benchmark de detección facial."""
        print("🔍 Benchmarking FaceDetector...")
        detector = FaceDetector()
        
        times = []
        for i in range(iterations):
            start = time.time()
            bbox = detector.detect(self.test_image)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = np.mean(times)
        std_time = np.std(times)
        min_time = np.min(times)
        max_time = np.max(times)
        
        result = {
            'module': 'FaceDetector',
            'iterations': iterations,
            'avg_time_ms': avg_time * 1000,
            'std_time_ms': std_time * 1000,
            'min_time_ms': min_time * 1000,
            'max_time_ms': max_time * 1000,
            'fps': 1.0 / avg_time if avg_time > 0 else 0
        }
        
        self.results['detection'] = result
        return result
    
    def benchmark_landmark_extraction(self, iterations: int = 10) -> Dict:
        """Benchmark de extracción de landmarks."""
        print("📍 Benchmarking LandmarkExtractor...")
        extractor = LandmarkExtractor()
        
        times = []
        for i in range(iterations):
            start = time.time()
            landmarks = extractor.detect(self.test_image)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = np.mean(times)
        std_time = np.std(times)
        
        result = {
            'module': 'LandmarkExtractor',
            'iterations': iterations,
            'avg_time_ms': avg_time * 1000,
            'std_time_ms': std_time * 1000,
            'fps': 1.0 / avg_time if avg_time > 0 else 0
        }
        
        self.results['landmark_extraction'] = result
        return result
    
    def benchmark_color_correction(self, iterations: int = 10) -> Dict:
        """Benchmark de corrección de color."""
        print("🎨 Benchmarking ColorCorrector...")
        corrector = ColorCorrector()
        
        # Crear imágenes de prueba
        source = self.test_image.copy()
        target = cv2.flip(self.test_image, 1)
        mask = np.ones((source.shape[0], source.shape[1]), dtype=np.float32) * 0.8
        
        times = []
        for i in range(iterations):
            start = time.time()
            corrected = corrector.correct_color_dual(source, target, mask)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = np.mean(times)
        
        result = {
            'module': 'ColorCorrector',
            'iterations': iterations,
            'avg_time_ms': avg_time * 1000,
            'fps': 1.0 / avg_time if avg_time > 0 else 0
        }
        
        self.results['color_correction'] = result
        return result
    
    def benchmark_blending(self, iterations: int = 10) -> Dict:
        """Benchmark de blending."""
        print("🔄 Benchmarking BlendingEngine...")
        blender = BlendingEngine()
        
        source = self.test_image.copy()
        target = cv2.flip(self.test_image, 1)
        mask = np.ones((source.shape[0], source.shape[1]), dtype=np.float32) * 0.8
        
        methods = {
            'multi_scale': lambda: blender.multi_scale_blending(source, target, mask),
            'advanced': lambda: blender.blend_advanced(source, target, mask),
            'ultra_advanced': lambda: blender.blend_ultra_advanced(source, target, mask)
        }
        
        results = {}
        for method_name, method_func in methods.items():
            times = []
            for i in range(iterations):
                start = time.time()
                result = method_func()
                elapsed = time.time() - start
                times.append(elapsed)
            
            avg_time = np.mean(times)
            results[method_name] = {
                'avg_time_ms': avg_time * 1000,
                'fps': 1.0 / avg_time if avg_time > 0 else 0
            }
        
        result = {
            'module': 'BlendingEngine',
            'iterations': iterations,
            'methods': results
        }
        
        self.results['blending'] = result
        return result
    
    def benchmark_pipeline(self, iterations: int = 5) -> Dict:
        """Benchmark del pipeline completo."""
        print("🚀 Benchmarking FaceSwapPipeline...")
        
        source = self.test_image.copy()
        target = cv2.flip(self.test_image, 1)
        
        modes = ['fast', 'high', 'ultra']
        results = {}
        
        for mode in modes:
            pipeline = FaceSwapPipeline(quality_mode=mode, use_advanced_enhancements=(mode == 'ultra'))
            
            times = []
            for i in range(iterations):
                try:
                    start = time.time()
                    result = pipeline.process(source, target)
                    elapsed = time.time() - start
                    times.append(elapsed)
                except Exception as e:
                    print(f"  ⚠ Error en modo {mode}: {e}")
                    break
            
            if times:
                avg_time = np.mean(times)
                results[mode] = {
                    'avg_time_ms': avg_time * 1000,
                    'fps': 1.0 / avg_time if avg_time > 0 else 0
                }
        
        result = {
            'module': 'FaceSwapPipeline',
            'iterations': iterations,
            'modes': results
        }
        
        self.results['pipeline'] = result
        return result
    
    def run_all_benchmarks(self, iterations: int = 10) -> Dict:
        """Ejecuta todos los benchmarks."""
        print("=" * 60)
        print("🚀 INICIANDO BENCHMARK DE RENDIMIENTO")
        print("=" * 60)
        print(f"Imagen de prueba: {self.test_image.shape}")
        print(f"Iteraciones por test: {iterations}")
        print(f"Numba disponible: {is_numba_available()}")
        print("=" * 60)
        print()
        
        # Ejecutar benchmarks
        self.benchmark_detection(iterations)
        self.benchmark_landmark_extraction(iterations)
        self.benchmark_color_correction(iterations)
        self.benchmark_blending(iterations)
        self.benchmark_pipeline(iterations=min(iterations, 5))  # Pipeline es más lento
        
        return self.results
    
    def print_results(self):
        """Imprime resultados formateados."""
        print()
        print("=" * 60)
        print("📊 RESULTADOS DEL BENCHMARK")
        print("=" * 60)
        print()
        
        # Detección
        if 'detection' in self.results:
            r = self.results['detection']
            print(f"🔍 {r['module']}:")
            print(f"   Tiempo promedio: {r['avg_time_ms']:.2f} ms")
            print(f"   FPS: {r['fps']:.2f}")
            print()
        
        # Landmarks
        if 'landmark_extraction' in self.results:
            r = self.results['landmark_extraction']
            print(f"📍 {r['module']}:")
            print(f"   Tiempo promedio: {r['avg_time_ms']:.2f} ms")
            print(f"   FPS: {r['fps']:.2f}")
            print()
        
        # Color correction
        if 'color_correction' in self.results:
            r = self.results['color_correction']
            print(f"🎨 {r['module']}:")
            print(f"   Tiempo promedio: {r['avg_time_ms']:.2f} ms")
            print(f"   FPS: {r['fps']:.2f}")
            print()
        
        # Blending
        if 'blending' in self.results:
            r = self.results['blending']
            print(f"🔄 {r['module']}:")
            for method, stats in r['methods'].items():
                print(f"   {method}: {stats['avg_time_ms']:.2f} ms ({stats['fps']:.2f} FPS)")
            print()
        
        # Pipeline
        if 'pipeline' in self.results:
            r = self.results['pipeline']
            print(f"🚀 {r['module']}:")
            for mode, stats in r['modes'].items():
                print(f"   {mode}: {stats['avg_time_ms']:.2f} ms ({stats['fps']:.2f} FPS)")
            print()
        
        print("=" * 60)
    
    def save_results(self, output_path: str = "benchmark_results.txt"):
        """Guarda resultados en archivo."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("BENCHMARK DE RENDIMIENTO - Face Swap Modules\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Numba disponible: {is_numba_available()}\n")
            f.write(f"Imagen de prueba: {self.test_image.shape}\n\n")
            
            for key, result in self.results.items():
                f.write(f"{key.upper()}:\n")
                f.write(str(result))
                f.write("\n\n")
        
        print(f"✓ Resultados guardados en: {output_path}")


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Benchmark de rendimiento de Face Swap Modules')
    parser.add_argument('-i', '--image', type=str, help='Ruta a imagen de prueba')
    parser.add_argument('-n', '--iterations', type=int, default=10, 
                       help='Número de iteraciones (default: 10)')
    parser.add_argument('-o', '--output', type=str, default='benchmark_results.txt',
                       help='Archivo de salida (default: benchmark_results.txt)')
    
    args = parser.parse_args()
    
    # Crear benchmark
    benchmark = PerformanceBenchmark(test_image_path=args.image)
    
    # Ejecutar benchmarks
    benchmark.run_all_benchmarks(iterations=args.iterations)
    
    # Mostrar resultados
    benchmark.print_results()
    
    # Guardar resultados
    benchmark.save_results(args.output)


if __name__ == '__main__':
    main()








