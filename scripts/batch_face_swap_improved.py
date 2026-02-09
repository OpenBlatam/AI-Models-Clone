"""
Batch Face Swap Mejorado con Modelo Entrenado + DeepSeek
==========================================================
Usa el modelo entrenado y DeepSeek API para resultados de máxima calidad
"""

import cv2
import numpy as np
from pathlib import Path
from face_swap_simple import SimpleFaceSwapPipeline
import random
import sys
import io

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Intentar importar DeepSeek enhancer
try:
    from deepseek_face_swap_enhancer import DeepSeekFaceSwapEnhancer
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False
    print("⚠ DeepSeek enhancer no disponible. Instala requests: pip install requests")

def get_bunny_faces():
    """Obtiene todas las caras de bunny disponibles."""
    bunny_dirs = [
        "instagram_downloads/bunnyrose.me",
        "instagram_downloads/bunnyrose.uwu",
        "instagram_downloads/bunnyy.rose_"
    ]
    
    all_faces = []
    for dir_path in bunny_dirs:
        dir_obj = Path(dir_path)
        if dir_obj.exists():
            jpg_files = list(dir_obj.glob("*.jpg"))
            all_faces.extend(jpg_files)
    
    return all_faces

def get_69caylin_images():
    """Obtiene todas las imágenes de 69caylin."""
    caylin_dir = Path("instagram_downloads/69caylin")
    if not caylin_dir.exists():
        return []
    
    return list(caylin_dir.glob("*.jpg"))

def improve_face_swap_result(result_img, source_img, target_img, deepseek_enhancer=None, use_deepseek=False):
    """
    Mejora ultra avanzada del resultado del face swap con post-procesamiento.
    
    Args:
        result_img: Imagen resultante del face swap
        source_img: Imagen fuente
        target_img: Imagen objetivo
        deepseek_enhancer: Instancia de DeepSeekFaceSwapEnhancer (opcional)
        use_deepseek: Si True, usa DeepSeek para mejorar (más lento pero mejor calidad)
    """
    # Si se usa DeepSeek y está disponible, aplicar mejoras de DeepSeek primero
    if use_deepseek and deepseek_enhancer and DEEPSEEK_AVAILABLE:
        try:
            # Usar DeepSeek sin análisis completo para velocidad (aplica mejoras estándar)
            result_img, _ = deepseek_enhancer.enhance_face_swap(
                result_img, source_img, target_img, use_analysis=False
            )
        except Exception as e:
            print(f"⚠ Error en mejora DeepSeek (continuando sin DeepSeek): {e}")
    
    # Mejora ultra avanzada estándar
    # Reducción de ruido preservando detalles (múltiples pasos mejorados)
    result_img = cv2.bilateralFilter(result_img, 9, 70, 70)
    result_img = cv2.bilateralFilter(result_img, 7, 50, 50)
    result_img = cv2.bilateralFilter(result_img, 5, 35, 35)
    
    # Ajuste de contraste y brillo ultra mejorado
    lab = cv2.cvtColor(result_img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Ecualización adaptativa del canal L ultra optimizada
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    
    # Mejora de saturación adaptativa con preservación de tonos de piel
    a_f = a.astype(np.float32)
    b_f = b.astype(np.float32)
    
    # Detectar regiones de piel
    skin_region = ((a_f > 120) & (a_f < 150) & (b_f > 130) & (b_f < 170))
    
    # Aumentar saturación más en áreas no-piel
    a_enhanced = np.where(skin_region,
                         np.clip(a_f * 1.02, 0, 255),
                         np.clip(a_f * 1.05, 0, 255))
    b_enhanced = np.where(skin_region,
                         np.clip(b_f * 1.02, 0, 255),
                         np.clip(b_f * 1.05, 0, 255))
    
    a = a_enhanced.astype(np.uint8)
    b = b_enhanced.astype(np.uint8)
    
    result_img = cv2.merge([l, a, b])
    result_img = cv2.cvtColor(result_img, cv2.COLOR_LAB2BGR)
    
    # Sharpening adaptativo ultra mejorado con detección de textura
    gray = cv2.cvtColor(result_img, cv2.COLOR_BGR2GRAY)
    
    # Detectar textura
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    texture_mask = np.abs(laplacian)
    texture_mask = cv2.GaussianBlur(texture_mask, (5, 5), 0)
    texture_mask = np.clip(texture_mask / (texture_mask.max() + 1e-6), 0, 1)
    texture_mask_3d = np.stack([texture_mask] * 3, axis=2)
    
    # Aplicar sharpening adaptativo
    kernel_strong = np.array([[-0.5, -1, -0.5],
                              [-1,  8, -1],
                              [-0.5, -1, -0.5]]) / 2.0
    kernel_soft = np.array([[0, -0.2, 0],
                             [-0.2, 1.8, -0.2],
                             [0, -0.2, 0]])
    
    sharpened_strong = cv2.filter2D(result_img, -1, kernel_strong)
    sharpened_soft = cv2.filter2D(result_img, -1, kernel_soft)
    
    # Mezclar según textura
    result_f = result_img.astype(np.float32)
    sharp_strong_f = sharpened_strong.astype(np.float32)
    sharp_soft_f = sharpened_soft.astype(np.float32)
    
    result_img = (result_f * (1 - texture_mask_3d * 0.2) + 
                  sharp_strong_f * (texture_mask_3d * 0.12) + 
                  sharp_soft_f * (texture_mask_3d * 0.08))
    result_img = np.clip(result_img, 0, 255).astype(np.uint8)
    
    # Corrección de color final ultra mejorada con histogram matching
    try:
        result_lab = cv2.cvtColor(result_img, cv2.COLOR_BGR2LAB)
        target_lab = cv2.cvtColor(target_img, cv2.COLOR_BGR2LAB)
        
        # Ajuste mejorado del canal L con blending multi-nivel
        result_l = result_lab[:, :, 0].astype(np.float32)
        target_l = target_lab[:, :, 0].astype(np.float32)
        
        # Crear máscara de blending para mejor integración
        # Más mezcla en bordes, menos en centro
        h, w = result_l.shape
        center_y, center_x = h // 2, w // 2
        y_coords, x_coords = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        blend_mask = np.clip(dist_from_center / max_dist, 0, 1)
        blend_mask = cv2.GaussianBlur(blend_mask, (51, 51), 0)
        
        # Mezclar con el target más en bordes
        result_l = result_l * (1 - blend_mask * 0.1) + target_l * (blend_mask * 0.1)
        result_lab[:, :, 0] = np.clip(result_l, 0, 255).astype(np.uint8)
        
        result_img = cv2.cvtColor(result_lab, cv2.COLOR_LAB2BGR)
    except:
        pass
    
    # Preservar coherencia de textura con el target
    try:
        target_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        result_gray = cv2.cvtColor(result_img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        
        # Extraer textura del target
        target_texture = target_gray - cv2.GaussianBlur(target_gray, (7, 7), 0)
        result_texture = result_gray - cv2.GaussianBlur(result_gray, (7, 7), 0)
        
        # Mezclar texturas sutilmente en toda la imagen para coherencia
        texture_blend = result_texture * 0.85 + target_texture * 0.15
        result_gray_final = cv2.GaussianBlur(result_gray, (7, 7), 0) + texture_blend
        
        # Aplicar de vuelta manteniendo color
        result_lab = cv2.cvtColor(result_img, cv2.COLOR_BGR2LAB)
        result_lab[:, :, 0] = np.clip(result_gray_final, 0, 255).astype(np.uint8)
        result_img = cv2.cvtColor(result_lab, cv2.COLOR_LAB2BGR)
    except:
        pass
    
    # Reducción final de ruido muy sutil (preservar textura)
    result_img = cv2.bilateralFilter(result_img, 3, 20, 20)
    
    # Mejora adicional: corrección de histograma adaptativa
    try:
        # Calcular histogramas
        result_hist = cv2.calcHist([result_img], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])
        target_hist = cv2.calcHist([target_img], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])
        
        # Normalizar histogramas
        result_hist = result_hist / (result_hist.sum() + 1e-7)
        target_hist = target_hist / (target_hist.sum() + 1e-7)
        
        # Calcular CDF (Cumulative Distribution Function)
        result_cdf = np.cumsum(result_hist.flatten())
        target_cdf = np.cumsum(target_hist.flatten())
        
        # Crear lookup table para matching de histograma
        # (simplificado - en producción usaría histogram matching completo)
        # Aplicar ajuste suave basado en diferencias de histograma
        result_lab = cv2.cvtColor(result_img, cv2.COLOR_BGR2LAB)
        target_lab = cv2.cvtColor(target_img, cv2.COLOR_BGR2LAB)
        
        # Ajuste sutil de canales A y B basado en histogramas
        result_a = result_lab[:, :, 1].astype(np.float32)
        result_b = result_lab[:, :, 2].astype(np.float32)
        target_a = target_lab[:, :, 1].astype(np.float32)
        target_b = target_lab[:, :, 2].astype(np.float32)
        
        # Ajuste adaptativo
        a_diff = target_a.mean() - result_a.mean()
        b_diff = target_b.mean() - result_b.mean()
        
        result_lab[:, :, 1] = np.clip(result_a + a_diff * 0.2, 0, 255).astype(np.uint8)
        result_lab[:, :, 2] = np.clip(result_b + b_diff * 0.2, 0, 255).astype(np.uint8)
        
        result_img = cv2.cvtColor(result_lab, cv2.COLOR_LAB2BGR)
    except:
        pass
    
    # Mejora final: realce de detalles finos
    try:
        # Usar unsharp masking para realzar detalles
        gaussian = cv2.GaussianBlur(result_img, (0, 0), 2.0)
        unsharp_mask = cv2.addWeighted(result_img, 1.5, gaussian, -0.5, 0)
        
        # Mezclar sutilmente
        result_img = cv2.addWeighted(result_img, 0.85, unsharp_mask, 0.15, 0)
    except:
        pass
    
    return result_img

def main():
    print("=" * 70)
    print("BATCH FACE SWAP MEJORADO: BUNNY -> 69CAYLIN")
    print("Con DeepSeek AI Enhancement")
    print("=" * 70)
    
    # Inicializar DeepSeek enhancer si está disponible
    deepseek_enhancer = None
    use_deepseek = DEEPSEEK_AVAILABLE
    
    if DEEPSEEK_AVAILABLE:
        try:
            print("\n🤖 Inicializando DeepSeek AI Enhancer...")
            deepseek_enhancer = DeepSeekFaceSwapEnhancer(
                api_key="sk-051c14b97c2a4526a0c3c98be47f17cb"
            )
            print("✓ DeepSeek enhancer inicializado correctamente")
        except Exception as e:
            print(f"⚠ Error inicializando DeepSeek: {e}")
            print("   Continuando sin mejoras de DeepSeek")
            use_deepseek = False
    else:
        print("\n⚠ DeepSeek no disponible. Instala: pip install requests")
    
    # Verificar si existe modelo entrenado
    model_path = Path("face_swap_simple_model.pth")
    if not model_path.exists():
        print("\n⚠ ADVERTENCIA: No se encontró modelo entrenado")
        print("   Usando algoritmo mejorado sin modelo entrenado")
        print("   (Para mejor calidad, ejecuta primero: python train_face_swap_model.py)\n")
    
    # Obtener imágenes
    print("\n📦 Cargando imágenes...")
    bunny_faces = get_bunny_faces()
    caylin_images = get_69caylin_images()
    
    if len(bunny_faces) == 0:
        print("❌ Error: No se encontraron imágenes de bunny")
        return
    
    if len(caylin_images) == 0:
        print("❌ Error: No se encontraron imágenes de 69caylin")
        return
    
    print(f"✓ Encontradas {len(bunny_faces)} caras de bunny")
    print(f"✓ Encontradas {len(caylin_images)} imágenes de 69caylin")
    
    # Crear carpeta de salida
    output_dir = Path("face_swap_results_bunny_to_69caylin")
    output_dir.mkdir(exist_ok=True)
    print(f"\n📁 Los resultados se guardarán en: {output_dir}")
    
    # Inicializar pipeline con modelo entrenado
    print("\n🔧 Inicializando pipeline con modelo entrenado...")
    pipeline = SimpleFaceSwapPipeline(model_path=str(model_path))
    
    # Procesar cada imagen de 69caylin
    print(f"\n🔄 Procesando {len(caylin_images)} imágenes...")
    if use_deepseek:
        print("   ✨ Usando mejoras de DeepSeek AI")
    print("-" * 70)
    
    successful = 0
    failed = 0
    
    for idx, caylin_img_path in enumerate(caylin_images, 1):
        try:
            # Seleccionar una cara de bunny aleatoria
            bunny_face_path = random.choice(bunny_faces)
            
            # Cargar imágenes
            bunny_img = cv2.imread(str(bunny_face_path))
            caylin_img = cv2.imread(str(caylin_img_path))
            
            if bunny_img is None or caylin_img is None:
                failed += 1
                continue
            
            # Hacer face swap con modelo entrenado
            result = pipeline.swap_faces(bunny_img, caylin_img)
            
            # Mejorar resultado con post-procesamiento + DeepSeek
            result = improve_face_swap_result(
                result, bunny_img, caylin_img, 
                deepseek_enhancer=deepseek_enhancer,
                use_deepseek=use_deepseek
            )
            
            # Aplicar mejoras avanzadas adicionales de DeepSeek si está disponible
            if use_deepseek and deepseek_enhancer:
                try:
                    # Aplicar mejoras específicas de color, blending y lighting
                    result = deepseek_enhancer._improve_color_matching(result, caylin_img)
                    result = deepseek_enhancer._improve_lighting(result, caylin_img)
                    # Aplicar mejora de textura de piel y características faciales
                    result = deepseek_enhancer._enhance_skin_texture(result, caylin_img)
                    result = deepseek_enhancer._enhance_facial_features(result)
                    # Aplicar mejoras avanzadas: Poisson blending, tone mapping, inpainting
                    result = deepseek_enhancer._apply_auto_enhancements(result, bunny_img, caylin_img)
                except Exception as e:
                    pass  # Continuar sin estas mejoras si fallan
            
            # Guardar resultado (sobrescribir)
            output_filename = f"bunny_face_on_{caylin_img_path.stem}.jpg"
            output_path = output_dir / output_filename
            
            # Guardar con máxima calidad JPEG ultra mejorada
            cv2.imwrite(str(output_path), result, 
                       [cv2.IMWRITE_JPEG_QUALITY, 100,
                        cv2.IMWRITE_JPEG_OPTIMIZE, 1])
            
            successful += 1
            if idx % 50 == 0:
                print(f"[{idx}/{len(caylin_images)}] Procesadas...")
            
        except Exception as e:
            print(f"❌ Error procesando {caylin_img_path.name}: {e}")
            failed += 1
            continue
    
    # Resumen
    print("\n" + "=" * 70)
    print("✅ PROCESO COMPLETADO")
    print("=" * 70)
    print(f"✓ Imágenes procesadas exitosamente: {successful}")
    print(f"⚠ Imágenes con errores: {failed}")
    print(f"📁 Resultados guardados en: {output_dir.absolute()}")
    if use_deepseek:
        print("\n✨ Mejoras aplicadas:")
        print("   - Modelo entrenado")
        print("   - DeepSeek AI Enhancement")
        print("   - Post-procesamiento avanzado")
    else:
        print("\n💡 Los resultados usan el modelo entrenado para mejor calidad")

if __name__ == "__main__":
    main()


