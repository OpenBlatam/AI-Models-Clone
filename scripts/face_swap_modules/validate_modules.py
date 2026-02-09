"""
Validador de Módulos Refactorizados
====================================
Script para validar que todos los módulos funcionan correctamente.
"""

import sys
from pathlib import Path
import traceback

# Colores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    """Imprime encabezado formateado."""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")


def print_success(text):
    """Imprime mensaje de éxito."""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    """Imprime mensaje de error."""
    print(f"{RED}✗ {text}{RESET}")


def print_warning(text):
    """Imprime mensaje de advertencia."""
    print(f"{YELLOW}⚠ {text}{RESET}")


def validate_imports():
    """Valida que todos los módulos se pueden importar."""
    print_header("Validando Importaciones")
    
    modules_to_test = [
        ('base', ['BaseDetector', 'LandmarkFormatHandler', 'ImageProcessor']),
        ('face_detector', ['FaceDetector']),
        ('landmark_extractor', ['LandmarkExtractor']),
        ('face_analyzer', ['FaceAnalyzer']),
        ('color_corrector', ['ColorCorrector']),
        ('blending_engine', ['BlendingEngine']),
        ('quality_enhancer', ['QualityEnhancer']),
        ('post_processor', ['PostProcessor']),
    ]
    
    all_passed = True
    
    for module_name, classes in modules_to_test:
        try:
            module = __import__(f'face_swap_modules.{module_name}', fromlist=classes)
            for class_name in classes:
                if hasattr(module, class_name):
                    print_success(f"{module_name}.{class_name} - OK")
                else:
                    print_error(f"{module_name}.{class_name} - NO ENCONTRADO")
                    all_passed = False
        except ImportError as e:
            print_error(f"{module_name} - ERROR DE IMPORTACIÓN: {e}")
            all_passed = False
        except Exception as e:
            print_error(f"{module_name} - ERROR: {e}")
            all_passed = False
    
    return all_passed


def validate_base_classes():
    """Valida funcionalidad de clases base."""
    print_header("Validando Clases Base")
    
    try:
        import numpy as np
        from face_swap_modules.base import LandmarkFormatHandler, ImageProcessor
        
        # Test LandmarkFormatHandler
        landmarks_106 = np.random.rand(106, 2) * 100
        format_detected = LandmarkFormatHandler.get_landmark_format(landmarks_106)
        assert format_detected == 106, f"Formato detectado incorrecto: {format_detected}"
        print_success("LandmarkFormatHandler.get_landmark_format() - OK")
        
        is_valid = LandmarkFormatHandler.is_valid_landmarks(landmarks_106)
        assert is_valid, "Validación de landmarks falló"
        print_success("LandmarkFormatHandler.is_valid_landmarks() - OK")
        
        left_eye = LandmarkFormatHandler.get_feature_region(landmarks_106, 'left_eye')
        assert left_eye is not None, "get_feature_region falló"
        print_success("LandmarkFormatHandler.get_feature_region() - OK")
        
        # Test ImageProcessor
        mask_2d = np.ones((50, 50), dtype=np.float32) * 0.5
        mask_3d = ImageProcessor.create_3d_mask(mask_2d)
        assert mask_3d.shape == (50, 50, 3), f"Shape incorrecto: {mask_3d.shape}"
        print_success("ImageProcessor.create_3d_mask() - OK")
        
        mask_uint8 = ImageProcessor.convert_to_uint8(mask_2d)
        assert mask_uint8.dtype == np.uint8, "Conversión a uint8 falló"
        print_success("ImageProcessor.convert_to_uint8() - OK")
        
        x, y = ImageProcessor.ensure_bounds(50, 50, 100, 100)
        assert x == 50 and y == 50, "ensure_bounds falló"
        print_success("ImageProcessor.ensure_bounds() - OK")
        
        return True
        
    except Exception as e:
        print_error(f"Error validando clases base: {e}")
        traceback.print_exc()
        return False


def validate_detectors():
    """Valida que los detectores se pueden inicializar."""
    print_header("Validando Detectores")
    
    try:
        from face_swap_modules import FaceDetector, LandmarkExtractor
        
        # Test FaceDetector
        detector = FaceDetector()
        print_success("FaceDetector inicializado - OK")
        
        # Test LandmarkExtractor
        extractor = LandmarkExtractor()
        print_success("LandmarkExtractor inicializado - OK")
        
        return True
        
    except Exception as e:
        print_error(f"Error validando detectores: {e}")
        traceback.print_exc()
        return False


def validate_processors():
    """Valida que los procesadores se pueden inicializar."""
    print_header("Validando Procesadores")
    
    try:
        from face_swap_modules import (
            FaceAnalyzer, ColorCorrector, BlendingEngine,
            QualityEnhancer, PostProcessor
        )
        
        analyzer = FaceAnalyzer()
        print_success("FaceAnalyzer inicializado - OK")
        
        color_corrector = ColorCorrector()
        print_success("ColorCorrector inicializado - OK")
        
        blending_engine = BlendingEngine()
        print_success("BlendingEngine inicializado - OK")
        
        quality_enhancer = QualityEnhancer()
        print_success("QualityEnhancer inicializado - OK")
        
        post_processor = PostProcessor()
        print_success("PostProcessor inicializado - OK")
        
        return True
        
    except Exception as e:
        print_error(f"Error validando procesadores: {e}")
        traceback.print_exc()
        return False


def validate_backward_compatibility():
    """Valida compatibilidad hacia atrás."""
    print_header("Validando Compatibilidad Hacia Atrás")
    
    try:
        from face_swap_modules import FaceDetector, LandmarkExtractor
        
        detector = FaceDetector()
        # Verificar que detect_face() existe (alias)
        assert hasattr(detector, 'detect_face'), "detect_face() no encontrado"
        print_success("FaceDetector.detect_face() (alias) - OK")
        
        extractor = LandmarkExtractor()
        # Verificar que get_landmarks() existe (alias)
        assert hasattr(extractor, 'get_landmarks'), "get_landmarks() no encontrado"
        print_success("LandmarkExtractor.get_landmarks() (alias) - OK")
        
        return True
        
    except Exception as e:
        print_error(f"Error validando compatibilidad: {e}")
        traceback.print_exc()
        return False


def validate_constants():
    """Valida que las constantes están definidas."""
    print_header("Validando Constantes")
    
    try:
        from face_swap_modules.base import (
            LandmarkFormatHandler
        )
        
        # Verificar constantes de formato
        assert hasattr(LandmarkFormatHandler, 'INSIGHTFACE_106')
        assert hasattr(LandmarkFormatHandler, 'FACE_ALIGNMENT_68')
        assert hasattr(LandmarkFormatHandler, 'MEDIAPIPE_468')
        print_success("Constantes de formato definidas - OK")
        
        return True
        
    except Exception as e:
        print_error(f"Error validando constantes: {e}")
        traceback.print_exc()
        return False


def main():
    """Ejecuta todas las validaciones."""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{'Validador de Módulos Refactorizados':^60}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")
    
    results = []
    
    # Ejecutar validaciones
    results.append(("Importaciones", validate_imports()))
    results.append(("Clases Base", validate_base_classes()))
    results.append(("Detectores", validate_detectors()))
    results.append(("Procesadores", validate_processors()))
    results.append(("Compatibilidad", validate_backward_compatibility()))
    results.append(("Constantes", validate_constants()))
    
    # Resumen
    print_header("Resumen de Validación")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"{name:20} {status}")
    
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"Total: {passed}/{total} validaciones pasadas")
    
    if passed == total:
        print(f"{GREEN}✓ TODAS LAS VALIDACIONES PASARON{RESET}")
        return 0
    else:
        print(f"{RED}✗ ALGUNAS VALIDACIONES FALLARON{RESET}")
        return 1


if __name__ == '__main__':
    sys.exit(main())








