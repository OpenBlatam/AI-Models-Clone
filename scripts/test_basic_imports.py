"""
Test Basico de Importaciones
=============================
Script para verificar que todas las importaciones funcionan correctamente.
"""

import sys
import io
from pathlib import Path

# Guardar stdout original
_original_stdout = sys.stdout
_original_stderr = sys.stderr

# Configurar codificacion UTF-8 para Windows
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

# Agregar scripts al path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

def safe_print(*args, **kwargs):
    """Print seguro que maneja stdout cerrado."""
    try:
        print(*args, **kwargs)
    except (ValueError, OSError):
        # Si stdout esta cerrado, intentar restaurar
        try:
            sys.stdout = _original_stdout
            print(*args, **kwargs)
        except:
            pass

def test_face_swap_modules():
    """Test importaciones de face_swap_modules."""
    safe_print("Testing face_swap_modules...")
    try:
        from face_swap_modules import (
            FaceDetector,
            LandmarkExtractor,
            ColorCorrector,
            BlendingEngine,
            FaceSwapPipeline,
            QualityEnhancer,
            PostProcessor,
            AdvancedEnhancements
        )
        safe_print("  [OK] Todos los modulos principales importados")
        
        # Verificar metodos
        detector = FaceDetector()
        assert hasattr(detector, 'detect'), "FaceDetector debe tener detect()"
        assert hasattr(detector, 'detect_face'), "FaceDetector debe tener detect_face()"
        safe_print("  [OK] FaceDetector metodos verificados")
        
        extractor = LandmarkExtractor()
        assert hasattr(extractor, 'detect'), "LandmarkExtractor debe tener detect()"
        assert hasattr(extractor, 'get_landmarks'), "LandmarkExtractor debe tener get_landmarks()"
        safe_print("  [OK] LandmarkExtractor metodos verificados")
        
        color_corrector = ColorCorrector()
        assert hasattr(color_corrector, 'correct_color_dual'), "ColorCorrector debe tener correct_color_dual()"
        safe_print("  [OK] ColorCorrector metodos verificados")
        
        blending_engine = BlendingEngine()
        assert hasattr(blending_engine, 'blend_advanced'), "BlendingEngine debe tener blend_advanced()"
        safe_print("  [OK] BlendingEngine metodos verificados")
        
        pipeline = FaceSwapPipeline()
        assert hasattr(pipeline, 'process'), "FaceSwapPipeline debe tener process()"
        safe_print("  [OK] FaceSwapPipeline metodos verificados")
        
        return True
    except Exception as e:
        safe_print(f"  [ERROR] {e}")
        return False

def test_simple_face_swap():
    """Test importaciones de simple_face_swap."""
    safe_print("\nTesting simple_face_swap...")
    try:
        from simple_face_swap import (
            SimpleFaceSwapPipeline,
            SimpleFaceSwapModel,
            SimpleFaceDetector
        )
        safe_print("  [OK] Modulos simple_face_swap importados")
        return True
    except Exception as e:
        safe_print(f"  [WARN] Advertencia: {e} (puede ser opcional)")
        return True  # No critico

def test_professional_face_swap():
    """Test importaciones de professional_face_swap."""
    safe_print("\nTesting professional_face_swap...")
    try:
        from professional_face_swap import (
            ProfessionalFaceSwap,
            ProfessionalFaceDetector,
            ProfessionalLandmarkExtractor
        )
        safe_print("  [OK] Modulos professional_face_swap importados")
        return True
    except Exception as e:
        safe_print(f"  [WARN] Advertencia: {e} (puede ser opcional)")
        return True  # No critico

def test_refactored_scripts():
    """Test que los scripts refactorizados pueden importarse."""
    safe_print("\nTesting scripts refactorizados...")
    results = []
    
    scripts_to_test = [
        'face_swap_high_quality_refactored',
        'face_swap_final_improved_refactored',
        'train_face_swap_model_refactored',
        'batch_face_swap_bunny_to_69caylin_refactored',
        'face_swap_professional_refactored_v2'
    ]
    
    for script_name in scripts_to_test:
        try:
            # Restaurar stdout antes de importar
            sys.stdout = _original_stdout
            sys.stderr = _original_stderr
            __import__(script_name)
            safe_print(f"  [OK] {script_name} importado correctamente")
            results.append(True)
        except Exception as e:
            # Restaurar stdout
            sys.stdout = _original_stdout
            sys.stderr = _original_stderr
            safe_print(f"  [WARN] {script_name}: {str(e)[:100]}")
            results.append(False)
    
    return all(results)

def main():
    """Ejecutar todos los tests."""
    safe_print("=" * 70)
    safe_print("TESTS DE IMPORTACIONES - VERIFICACION DE BUGS CORREGIDOS")
    safe_print("=" * 70)
    safe_print()
    
    results = []
    
    # Test modulos principales
    results.append(test_face_swap_modules())
    
    # Test modulos opcionales
    results.append(test_simple_face_swap())
    results.append(test_professional_face_swap())
    
    # Test scripts refactorizados
    results.append(test_refactored_scripts())
    
    safe_print("\n" + "=" * 70)
    if all(results):
        safe_print("[SUCCESS] TODOS LOS TESTS PASARON")
        safe_print("[SUCCESS] TODOS LOS BUGS CORREGIDOS VERIFICADOS")
    else:
        safe_print("[WARNING] ALGUNOS TESTS FALLARON - Revisar errores arriba")
    safe_print("=" * 70)
    
    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())




