"""
Face Swap de Alta Calidad
==========================
Versión mejorada con técnicas avanzadas para resultados profesionales
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import os
import sys
import io

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class HighQualityFaceSwap:
    """Face swap de alta calidad con mejor blending y ajuste de color."""
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
    
    def detect_face_landmarks(self, image: np.ndarray, face_rect) -> Optional[np.ndarray]:
        """Estima landmarks faciales usando detección de ojos."""
        x, y, w, h = face_rect
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_roi = gray[y:y+h, x:x+w]
        
        # Detectar ojos
        eyes = self.eye_cascade.detectMultiScale(face_roi, 1.1, 3)
        
        if len(eyes) >= 2:
            # Ordenar ojos por posición x
            eyes = sorted(eyes, key=lambda e: e[0])
            left_eye = eyes[0]
            right_eye = eyes[1]
            
            # Calcular puntos de referencia
            left_eye_center = (x + left_eye[0] + left_eye[2]//2, 
                              y + left_eye[1] + left_eye[3]//2)
            right_eye_center = (x + right_eye[0] + right_eye[2]//2,
                               y + right_eye[1] + right_eye[3]//2)
            
            # Estimar otros puntos
            nose = ((left_eye_center[0] + right_eye_center[0]) // 2,
                   (left_eye_center[1] + right_eye_center[1]) // 2 + h // 4)
            mouth_left = (x + w * 0.25, y + int(h * 0.7))
            mouth_right = (x + int(w * 0.75), y + int(h * 0.7))
            
            points = np.array([
                left_eye_center,
                right_eye_center,
                nose,
                mouth_left,
                mouth_right
            ])
            return points
        
        # Fallback: estimación básica
        points = np.array([
            [x + w * 0.35, y + h * 0.35],  # Ojo izquierdo estimado
            [x + w * 0.65, y + h * 0.35],  # Ojo derecho estimado
            [x + w * 0.5, y + h * 0.6],    # Nariz
            [x + w * 0.3, y + h * 0.75],   # Boca izquierda
            [x + w * 0.7, y + h * 0.75],   # Boca derecha
        ])
        return points
    
    def get_face_mask(self, image_shape: Tuple[int, int], face_rect, landmarks: Optional[np.ndarray] = None) -> np.ndarray:
        """Crea una máscara suave para la cara."""
        h, w = image_shape[:2]
        mask = np.zeros((h, w), dtype=np.float32)
        
        x, y, face_w, face_h = face_rect
        
        # Crear máscara elíptica suave
        center_x = x + face_w // 2
        center_y = y + face_h // 2
        
        # Expandir región para incluir más contexto
        radius_x = int(face_w * 0.6)
        radius_y = int(face_h * 0.7)
        
        y_coords, x_coords = np.ogrid[:h, :w]
        
        # Máscara elíptica
        ellipse_mask = ((x_coords - center_x) / radius_x) ** 2 + ((y_coords - center_y) / radius_y) ** 2 <= 1
        
        mask[ellipse_mask] = 1.0
        
        # Suavizar bordes con múltiples pasos de blur
        mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=15, sigmaY=15)
        mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=10, sigmaY=10)
        
        # Asegurar que los valores estén en [0, 1]
        mask = np.clip(mask, 0, 1)
        
        return mask
    
    def color_correction(self, source: np.ndarray, target: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Ajusta el color de la cara fuente para que coincida con el entorno."""
        # Convertir a LAB para mejor ajuste de color
        source_lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype(np.float32)
        target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        # Calcular estadísticas de color en la región de la cara
        mask_3d = np.stack([mask] * 3, axis=2)
        
        # Media y desviación estándar de la cara fuente
        source_mean = np.sum(source_lab * mask_3d, axis=(0, 1)) / (np.sum(mask) + 1e-6)
        source_std = np.sqrt(np.sum(((source_lab - source_mean) ** 2) * mask_3d, axis=(0, 1)) / (np.sum(mask) + 1e-6)) + 1e-6
        
        # Media y desviación estándar del área alrededor de la cara en target
        # Usar área alrededor de la cara (inverso de la máscara suavizada)
        surrounding_mask = 1 - mask
        surrounding_mask = cv2.GaussianBlur(surrounding_mask, (51, 51), 0)
        surrounding_mask_3d = np.stack([surrounding_mask] * 3, axis=2)
        
        target_mean = np.sum(target_lab * surrounding_mask_3d, axis=(0, 1)) / (np.sum(surrounding_mask) + 1e-6)
        target_std = np.sqrt(np.sum(((target_lab - target_mean) ** 2) * surrounding_mask_3d, axis=(0, 1)) / (np.sum(surrounding_mask) + 1e-6)) + 1e-6
        
        # Aplicar transformación de color
        corrected_lab = source_lab.copy()
        corrected_lab = (corrected_lab - source_mean) * (target_std / source_std) + target_mean
        
        # Convertir de vuelta a BGR
        corrected = cv2.cvtColor(corrected_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
        
        return corrected
    
    def seamless_clone(self, source: np.ndarray, target: np.ndarray, mask: np.ndarray, center: Tuple[int, int]) -> np.ndarray:
        """Usa seamless cloning de OpenCV para mejor integración."""
        # Convertir máscara a uint8
        mask_uint8 = (mask * 255).astype(np.uint8)
        
        # Aplicar seamless cloning
        result = cv2.seamlessClone(
            source, target, mask_uint8, center, 
            cv2.NORMAL_CLONE
        )
        
        return result
    
    def detect_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detecta la cara más grande en la imagen."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        if len(faces) > 0:
            # Retornar la cara más grande
            faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
            return tuple(faces[0])
        
        return None
    
    def extract_face_region(self, image: np.ndarray, face_rect: Tuple[int, int, int, int], 
                           expand_factor: float = 0.4) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
        """Extrae la región de la cara con margen expandido."""
        x, y, w, h = face_rect
        
        # Expandir región
        expand_w = int(w * expand_factor)
        expand_h = int(h * expand_factor)
        
        x_expanded = max(0, x - expand_w)
        y_expanded = max(0, y - expand_h)
        w_expanded = min(image.shape[1] - x_expanded, w + 2 * expand_w)
        h_expanded = min(image.shape[0] - y_expanded, h + 2 * expand_h)
        
        face_region = image[y_expanded:y_expanded+h_expanded, 
                          x_expanded:x_expanded+w_expanded]
        
        # Ajustar coordenadas relativas
        adjusted_rect = (x - x_expanded, y - y_expanded, w, h)
        
        return face_region, adjusted_rect
    
    def swap_faces(self, source_image: np.ndarray, target_image: np.ndarray) -> np.ndarray:
        """Intercambia caras con alta calidad."""
        # Detectar caras
        source_face_rect = self.detect_face(source_image)
        target_face_rect = self.detect_face(target_image)
        
        if source_face_rect is None or target_face_rect is None:
            print("⚠ No se detectó cara en una o ambas imágenes")
            return target_image
        
        # Extraer regiones de caras
        source_face_region, source_adjusted_rect = self.extract_face_region(
            source_image, source_face_rect, expand_factor=0.4
        )
        target_face_region, target_adjusted_rect = self.extract_face_region(
            target_image, target_face_rect, expand_factor=0.4
        )
        
        # Redimensionar cara fuente para que coincida con el tamaño de la cara destino
        target_w = target_face_rect[2]
        target_h = target_face_rect[3]
        source_w = source_face_rect[2]
        source_h = source_face_rect[3]
        
        # Calcular factor de escala
        scale_w = target_w / source_w
        scale_h = target_h / source_h
        scale = max(scale_w, scale_h) * 1.1  # Ligeramente más grande para mejor cobertura
        
        new_source_w = int(source_face_region.shape[1] * scale)
        new_source_h = int(source_face_region.shape[0] * scale)
        
        source_resized = cv2.resize(source_face_region, (new_source_w, new_source_h), 
                                   interpolation=cv2.INTER_LANCZOS4)
        
        # Ajustar tamaño si es necesario para que quepa en la región target
        if new_source_w > target_face_region.shape[1] or new_source_h > target_face_region.shape[0]:
            scale_factor = min(
                target_face_region.shape[1] / new_source_w,
                target_face_region.shape[0] / new_source_h
            )
            new_source_w = int(new_source_w * scale_factor)
            new_source_h = int(new_source_h * scale_factor)
            source_resized = cv2.resize(source_resized, (new_source_w, new_source_h),
                                      interpolation=cv2.INTER_LANCZOS4)
        
        # Crear imagen del tamaño de target_face_region
        source_aligned = np.zeros_like(target_face_region)
        
        # Centrar la cara fuente
        offset_x = (target_face_region.shape[1] - new_source_w) // 2
        offset_y = (target_face_region.shape[0] - new_source_h) // 2
        
        source_aligned[offset_y:offset_y+new_source_h, 
                      offset_x:offset_x+new_source_w] = source_resized
        
        # Crear máscara para la cara
        mask_rect = (
            offset_x + int(new_source_w * 0.1),
            offset_y + int(new_source_h * 0.1),
            int(new_source_w * 0.8),
            int(new_source_h * 0.8)
        )
        
        mask = self.get_face_mask(target_face_region.shape[:2], mask_rect)
        
        # Ajustar color
        source_corrected = self.color_correction(source_aligned, target_face_region, mask)
        
        # Aplicar blending mejorado
        mask_3d = np.stack([mask] * 3, axis=2)
        
        # Blending con múltiples capas
        blended = (source_corrected * mask_3d + 
                  target_face_region * (1 - mask_3d)).astype(np.uint8)
        
        # Aplicar seamless cloning en el centro
        center = (target_face_region.shape[1] // 2, target_face_region.shape[0] // 2)
        try:
            blended = self.seamless_clone(source_corrected, target_face_region, mask, center)
        except:
            pass  # Si falla, usar el blending normal
        
        # Insertar de vuelta en la imagen original
        result = target_image.copy()
        x_expanded = max(0, target_face_rect[0] - int(target_face_rect[2] * 0.4))
        y_expanded = max(0, target_face_rect[1] - int(target_face_rect[3] * 0.4))
        
        h_blended, w_blended = blended.shape[:2]
        result[y_expanded:y_expanded+h_blended, 
               x_expanded:x_expanded+w_blended] = blended
        
        return result


def batch_high_quality_swap():
    """Procesa todas las imágenes con face swap de alta calidad."""
    from pathlib import Path
    import random
    
    print("=" * 70)
    print("FACE SWAP DE ALTA CALIDAD: BUNNY -> 69CAYLIN")
    print("=" * 70)
    
    # Obtener imágenes
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
        print("❌ Error: No se encontraron imágenes suficientes")
        return
    
    print(f"Encontradas {len(all_bunny_faces)} caras de bunny")
    print(f"Encontradas {len(caylin_images)} imagenes de 69caylin")
    
    # Crear carpeta de salida
    output_dir = Path("face_swap_results_bunny_to_69caylin")
    output_dir.mkdir(exist_ok=True)
    
    # Inicializar face swap de alta calidad
    print("\n🔧 Inicializando face swap de alta calidad...")
    face_swapper = HighQualityFaceSwap()
    
    print(f"\n🔄 Procesando {len(caylin_images)} imágenes...")
    print("-" * 70)
    
    successful = 0
    failed = 0
    
    for idx, caylin_img_path in enumerate(caylin_images, 1):
        try:
            # Seleccionar cara de bunny aleatoria
            bunny_face_path = random.choice(all_bunny_faces)
            
            # Cargar imágenes
            bunny_img = cv2.imread(str(bunny_face_path))
            caylin_img = cv2.imread(str(caylin_img_path))
            
            if bunny_img is None or caylin_img is None:
                failed += 1
                continue
            
            # Hacer face swap de alta calidad
            result = face_swapper.swap_faces(bunny_img, caylin_img)
            
            # Guardar resultado (sobrescribir)
            output_filename = f"bunny_face_on_{caylin_img_path.stem}.jpg"
            output_path = output_dir / output_filename
            
            # Guardar con alta calidad JPEG
            cv2.imwrite(str(output_path), result, 
                       [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            successful += 1
            if idx % 50 == 0:
                print(f"[{idx}/{len(caylin_images)}] Procesadas...")
            
        except Exception as e:
            print(f"❌ Error en {caylin_img_path.name}: {e}")
            failed += 1
            continue
    
    print("\n" + "=" * 70)
    print("PROCESO COMPLETADO")
    print("=" * 70)
    print(f"Imagenes procesadas: {successful}")
    print(f"Errores: {failed}")
    print(f"Resultados en: {output_dir.absolute()}")


if __name__ == "__main__":
    batch_high_quality_swap()








