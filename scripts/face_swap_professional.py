"""
Face Swap Professional - Usando Librerías Especializadas
=========================================================
Versión profesional usando MediaPipe, face-alignment y otras librerías avanzadas
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

# Intentar importar librerías especializadas
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("⚠ MediaPipe no disponible. Instala con: pip install mediapipe")

try:
    import face_alignment
    FACE_ALIGNMENT_AVAILABLE = True
except ImportError:
    FACE_ALIGNMENT_AVAILABLE = False
    print("⚠ face-alignment no disponible. Instala con: pip install face-alignment")

try:
    from skimage import transform as sktransform
    from skimage import filters
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False
    print("⚠ scikit-image no disponible. Instala con: pip install scikit-image")

try:
    from PIL import Image, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import insightface
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False
    print("⚠ InsightFace no disponible. Instala con: pip install insightface onnxruntime")

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

try:
    import albumentations as A
    ALBUMENTATIONS_AVAILABLE = True
except ImportError:
    ALBUMENTATIONS_AVAILABLE = False
    print("⚠ Albumentations no disponible. Instala con: pip install albumentations")

try:
    import kornia
    KORNIA_AVAILABLE = True
except ImportError:
    KORNIA_AVAILABLE = False
    print("⚠ Kornia no disponible. Instala con: pip install kornia")

try:
    from retinaface import RetinaFace
    RETINAFACE_AVAILABLE = True
except ImportError:
    RETINAFACE_AVAILABLE = False
    print("⚠ RetinaFace no disponible. Instala con: pip install retinaface")

try:
    import imageio
    IMAGEIO_AVAILABLE = True
except ImportError:
    IMAGEIO_AVAILABLE = False

try:
    from scipy import ndimage
    from scipy.spatial import distance
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("⚠ SciPy no disponible. Instala con: pip install scipy")

try:
    import numba
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    # Crear decorador dummy si numba no está disponible
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

try:
    from skimage import segmentation, restoration
    SKIMAGE_ADVANCED_AVAILABLE = True
except ImportError:
    SKIMAGE_ADVANCED_AVAILABLE = False


class ProfessionalFaceSwap:
    """Face swap profesional usando librerías especializadas."""
    
    def __init__(self):
        # Inicializar MediaPipe si está disponible
        if MEDIAPIPE_AVAILABLE:
            self.mp_face_mesh = mp.solutions.face_mesh
            self.mp_drawing = mp.solutions.drawing_utils
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5
            )
            print("✓ MediaPipe Face Mesh inicializado")
        else:
            self.face_mesh = None
            # Fallback a OpenCV
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            print("⚠ Usando OpenCV Cascade (instala MediaPipe para mejor calidad)")
        
        # Inicializar face-alignment si está disponible
        if FACE_ALIGNMENT_AVAILABLE:
            try:
                self.face_aligner = face_alignment.FaceAlignment(
                    face_alignment.LandmarksType.TWO_D,
                    flip_input=False,
                    device='cpu'
                )
                print("✓ Face Alignment inicializado")
            except:
                self.face_aligner = None
                FACE_ALIGNMENT_AVAILABLE = False
        else:
            self.face_aligner = None
        
        # Inicializar InsightFace si está disponible
        if INSIGHTFACE_AVAILABLE:
            try:
                self.insightface_app = insightface.app.FaceAnalysis(
                    providers=['CPUExecutionProvider']  # o 'CUDAExecutionProvider' si hay GPU
                )
                self.insightface_app.prepare(ctx_id=0, det_size=(640, 640))
                print("✓ InsightFace inicializado")
            except Exception as e:
                self.insightface_app = None
                INSIGHTFACE_AVAILABLE = False
                print(f"⚠ InsightFace no pudo inicializarse: {e}")
        else:
            self.insightface_app = None
        
        # Inicializar RetinaFace si está disponible
        if RETINAFACE_AVAILABLE:
            print("✓ RetinaFace disponible")
        else:
            pass
    
    def detect_face_mediapipe(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detecta cara usando MediaPipe (más preciso)."""
        if not MEDIAPIPE_AVAILABLE or self.face_mesh is None:
            return None
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            h, w = image.shape[:2]
            
            # Obtener bounding box de los landmarks
            x_coords = [landmark.x * w for landmark in face_landmarks.landmark]
            y_coords = [landmark.y * h for landmark in face_landmarks.landmark]
            
            x_min, x_max = int(min(x_coords)), int(max(x_coords))
            y_min, y_max = int(min(y_coords)), int(max(y_coords))
            
            # Expandir un poco
            margin = 0.1
            width = x_max - x_min
            height = y_max - y_min
            x_min = max(0, int(x_min - width * margin))
            y_min = max(0, int(y_min - height * margin))
            x_max = min(w, int(x_max + width * margin))
            y_max = min(h, int(y_max + height * margin))
            
            return (x_min, y_min, x_max - x_min, y_max - y_min)
        
        return None
    
    def get_face_landmarks_mediapipe(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Obtiene landmarks faciales usando MediaPipe."""
        if not MEDIAPIPE_AVAILABLE or self.face_mesh is None:
            return None
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            h, w = image.shape[:2]
            
            landmarks = np.array([
                [landmark.x * w, landmark.y * h]
                for landmark in face_landmarks.landmark
            ])
            
            return landmarks
        
        return None
    
    def get_face_landmarks_face_alignment(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Obtiene landmarks usando face-alignment (muy preciso)."""
        if not FACE_ALIGNMENT_AVAILABLE or self.face_aligner is None:
            return None
        
        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            landmarks = self.face_aligner.get_landmarks(rgb_image)
            
            if landmarks is not None and len(landmarks) > 0:
                return landmarks[0]  # Retornar primera cara
        
        except Exception as e:
            print(f"Error en face-alignment: {e}")
        
        return None
    
    def detect_face_insightface(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detecta cara usando InsightFace (muy preciso y rápido)."""
        if not INSIGHTFACE_AVAILABLE or self.insightface_app is None:
            return None
        
        try:
            faces = self.insightface_app.get(image)
            if faces and len(faces) > 0:
                face = faces[0]
                bbox = face.bbox.astype(np.int32)
                x, y, x2, y2 = bbox
                return (x, y, x2 - x, y2 - y)
        except Exception as e:
            print(f"Error en InsightFace: {e}")
        
        return None
    
    def get_face_landmarks_insightface(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Obtiene landmarks usando InsightFace (muy preciso)."""
        if not INSIGHTFACE_AVAILABLE or self.insightface_app is None:
            return None
        
        try:
            faces = self.insightface_app.get(image)
            if faces and len(faces) > 0:
                face = faces[0]
                landmarks = face.landmark_2d_106  # 106 landmarks
                return landmarks
        except Exception as e:
            print(f"Error en InsightFace landmarks: {e}")
        
        return None
    
    def detect_face_retinaface(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detecta cara usando RetinaFace (muy preciso)."""
        if not RETINAFACE_AVAILABLE:
            return None
        
        try:
            faces = RetinaFace.detect_faces(image)
            if faces:
                # Obtener la primera cara
                face_key = list(faces.keys())[0]
                face_data = faces[face_key]
                facial_area = face_data['facial_area']
                x, y, x2, y2 = facial_area
                return (x, y, x2 - x, y2 - y)
        except Exception as e:
            print(f"Error en RetinaFace: {e}")
        
        return None
    
    def detect_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detecta cara usando el mejor método disponible."""
        # Prioridad: InsightFace > RetinaFace > MediaPipe > OpenCV
        if INSIGHTFACE_AVAILABLE:
            result = self.detect_face_insightface(image)
            if result:
                return result
        
        if RETINAFACE_AVAILABLE:
            result = self.detect_face_retinaface(image)
            if result:
                return result
        
        if MEDIAPIPE_AVAILABLE:
            result = self.detect_face_mediapipe(image)
            if result:
                return result
        
        # Fallback a OpenCV
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8,8))
        gray_enhanced = clahe.apply(gray)
        
        faces = self.face_cascade.detectMultiScale(
            gray_enhanced,
            scaleFactor=1.05,
            minNeighbors=6,
            minSize=(100, 100)
        )
        
        if len(faces) > 0:
            faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
            return tuple(faces[0])
        
        return None
    
    def analyze_face_regions(self, image: np.ndarray, landmarks: np.ndarray) -> dict:
        """Analiza diferentes regiones faciales para mejor procesamiento."""
        if landmarks is None or len(landmarks) < 5:
            return {}
        
        h, w = image.shape[:2]
        regions = {}
        
        if len(landmarks) == 106:  # InsightFace
            # Ojos
            left_eye_points = landmarks[33:42] if len(landmarks) > 42 else landmarks[33:38]
            right_eye_points = landmarks[42:51] if len(landmarks) > 51 else landmarks[88:93]
            # Nariz
            nose_points = landmarks[51:60] if len(landmarks) > 60 else landmarks[86:91]
            # Boca
            mouth_points = landmarks[76:88] if len(landmarks) > 88 else landmarks[78:84]
            # Mejillas
            left_cheek = landmarks[1:5] if len(landmarks) > 5 else landmarks[0:2]
            right_cheek = landmarks[14:18] if len(landmarks) > 18 else landmarks[13:15]
        elif len(landmarks) == 68:  # face-alignment
            left_eye_points = landmarks[36:42]
            right_eye_points = landmarks[42:48]
            nose_points = landmarks[27:36]
            mouth_points = landmarks[48:68]
            left_cheek = landmarks[0:3]
            right_cheek = landmarks[13:16]
        else:
            return {}
        
        regions['left_eye'] = left_eye_points
        regions['right_eye'] = right_eye_points
        regions['nose'] = nose_points
        regions['mouth'] = mouth_points
        regions['left_cheek'] = left_cheek
        regions['right_cheek'] = right_cheek
        
        return regions
    
    def analyze_facial_features_deep(self, image: np.ndarray, landmarks: np.ndarray) -> dict:
        """Análisis profundo de características faciales para mejor preservación de identidad."""
        features = {}
        
        if landmarks is None or len(landmarks) < 5:
            return features
        
        try:
            # Convertir a LAB para análisis de color de piel
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l_channel = lab[:, :, 0].astype(np.float32)
            
            # Análisis de tono de piel
            if len(landmarks) == 106:
                cheek_left = landmarks[1:5] if len(landmarks) > 5 else landmarks[0:2]
                cheek_right = landmarks[14:18] if len(landmarks) > 18 else landmarks[13:15]
            elif len(landmarks) == 68:
                cheek_left = landmarks[0:3]
                cheek_right = landmarks[13:16]
            else:
                return features
            
            # Calcular tono de piel promedio en mejillas
            cheek_points = np.vstack([cheek_left, cheek_right])
            cheek_indices = np.clip(cheek_points.astype(int), 0, [image.shape[1]-1, image.shape[0]-1])
            skin_tones = []
            for idx in cheek_indices:
                if 0 <= idx[1] < l_channel.shape[0] and 0 <= idx[0] < l_channel.shape[1]:
                    skin_tones.append(l_channel[idx[1], idx[0]])
            
            if skin_tones:
                features['skin_tone'] = np.mean(skin_tones)
                features['skin_tone_std'] = np.std(skin_tones)
            
            # Análisis de estructura facial
            if len(landmarks) == 106:
                face_width = np.max(landmarks[:, 0]) - np.min(landmarks[:, 0])
                face_height = np.max(landmarks[:, 1]) - np.min(landmarks[:, 1])
            elif len(landmarks) == 68:
                face_width = np.max(landmarks[:, 0]) - np.min(landmarks[:, 0])
                face_height = np.max(landmarks[:, 1]) - np.min(landmarks[:, 1])
            else:
                return features
            
            features['face_aspect_ratio'] = face_width / (face_height + 1e-6)
            features['face_size'] = face_width * face_height
            
        except:
            pass
        
        return features
    
    def preserve_identity_features(self, source: np.ndarray, target: np.ndarray,
                                  source_landmarks: np.ndarray, target_landmarks: np.ndarray,
                                  mask: np.ndarray) -> np.ndarray:
        """Preserva características distintivas de identidad del source."""
        try:
            # Analizar características profundas
            source_features = self.analyze_facial_features_deep(source, source_landmarks)
            target_features = self.analyze_facial_features_deep(target, target_landmarks)
            
            if not source_features or not target_features:
                return source
            
            # Preservar tono de piel del source si es muy diferente
            if 'skin_tone' in source_features and 'skin_tone' in target_features:
                skin_diff = abs(source_features['skin_tone'] - target_features['skin_tone'])
                if skin_diff > 10:  # Diferencia significativa
                    # Ajustar tono de piel preservando el del source
                    source_lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype(np.float32)
                    target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)
                    
                    # Preservar luminosidad del source en área facial
                    skin_mask = cv2.GaussianBlur(mask, (31, 31), 0)
                    skin_mask_3d = np.stack([skin_mask] * 3, axis=2)
                    
                    # Mezclar luminosidad preservando más del source
                    source_lab[:, :, 0] = (source_lab[:, :, 0] * (1 - skin_mask * 0.3) + 
                                         target_lab[:, :, 0] * (skin_mask * 0.3))
                    
                    source = cv2.cvtColor(np.clip(source_lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
            
        except:
            pass
        
        return source
    
    def analyze_facial_expression(self, landmarks: np.ndarray) -> dict:
        """Analiza la expresión facial para preservarla mejor."""
        if landmarks is None or len(landmarks) < 5:
            return {}
        
        expression_info = {}
        
        try:
            if len(landmarks) == 106:  # InsightFace
                # Ojos
                left_eye = landmarks[33:42] if len(landmarks) > 42 else landmarks[33:38]
                right_eye = landmarks[42:51] if len(landmarks) > 51 else landmarks[88:93]
                # Boca
                mouth = landmarks[76:88] if len(landmarks) > 88 else landmarks[78:84]
                # Cejas
                left_eyebrow = landmarks[18:22] if len(landmarks) > 22 else landmarks[18:20]
                right_eyebrow = landmarks[23:27] if len(landmarks) > 27 else landmarks[23:25]
            elif len(landmarks) == 68:  # face-alignment
                left_eye = landmarks[36:42]
                right_eye = landmarks[42:48]
                mouth = landmarks[48:68]
                left_eyebrow = landmarks[17:22]
                right_eyebrow = landmarks[22:27]
            else:
                return {}
            
            # Calcular apertura de ojos
            left_eye_height = np.max(left_eye[:, 1]) - np.min(left_eye[:, 1])
            right_eye_height = np.max(right_eye[:, 1]) - np.min(right_eye[:, 1])
            expression_info['eye_openness'] = (left_eye_height + right_eye_height) / 2
            
            # Calcular apertura de boca
            mouth_height = np.max(mouth[:, 1]) - np.min(mouth[:, 1])
            mouth_width = np.max(mouth[:, 0]) - np.min(mouth[:, 0])
            expression_info['mouth_openness'] = mouth_height
            expression_info['mouth_width'] = mouth_width
            
            # Calcular posición de cejas
            left_eyebrow_y = np.mean(left_eyebrow[:, 1])
            right_eyebrow_y = np.mean(right_eyebrow[:, 1])
            expression_info['eyebrow_position'] = (left_eyebrow_y + right_eyebrow_y) / 2
            
        except:
            pass
        
        return expression_info
    
    def preserve_expression_features(self, source: np.ndarray, target: np.ndarray,
                                    source_landmarks: np.ndarray, target_landmarks: np.ndarray,
                                    mask: np.ndarray) -> np.ndarray:
        """Preserva características de expresión del target."""
        source_expr = self.analyze_facial_expression(source_landmarks)
        target_expr = self.analyze_facial_expression(target_landmarks)
        
        if not source_expr or not target_expr:
            return source
        
        # Calcular diferencias de expresión
        eye_diff = abs(target_expr.get('eye_openness', 0) - source_expr.get('eye_openness', 0))
        mouth_diff = abs(target_expr.get('mouth_openness', 0) - source_expr.get('mouth_openness', 0))
        
        # Si las expresiones son muy diferentes, preservar más del target
        if eye_diff > 5 or mouth_diff > 5:
            # Ajustar máscara para preservar expresión del target
            expr_mask = cv2.GaussianBlur(mask, (31, 31), 0)
            expr_mask_3d = np.stack([expr_mask] * 3, axis=2)
            
            # Mezclar preservando expresión del target
            result = source.astype(np.float32) * (1 - expr_mask_3d * 0.2) + \
                    target.astype(np.float32) * (expr_mask_3d * 0.2)
            return np.clip(result, 0, 255).astype(np.uint8)
        
        return source
    
    def analyze_geometric_structure(self, landmarks: np.ndarray) -> dict:
        """Análisis de estructura geométrica facial para mejor consistencia."""
        structure = {}
        
        if landmarks is None or len(landmarks) < 5:
            return structure
        
        try:
            # Calcular puntos clave
            if len(landmarks) == 106:
                left_eye = landmarks[38] if len(landmarks) > 38 else landmarks[0]
                right_eye = landmarks[88] if len(landmarks) > 88 else landmarks[0]
                nose = landmarks[86] if len(landmarks) > 86 else landmarks[0]
                mouth_center = landmarks[78] if len(landmarks) > 78 else landmarks[0]
            elif len(landmarks) == 68:
                left_eye = landmarks[36:42].mean(axis=0)
                right_eye = landmarks[42:48].mean(axis=0)
                nose = landmarks[30]
                mouth_center = landmarks[48:68].mean(axis=0)
            else:
                return structure
            
            # Calcular distancias clave
            eye_distance = np.linalg.norm(right_eye - left_eye)
            nose_to_eye_center = np.linalg.norm(nose - (left_eye + right_eye) / 2)
            mouth_to_nose = np.linalg.norm(mouth_center - nose)
            
            # Calcular ángulos
            eye_vector = right_eye - left_eye
            eye_angle = np.arctan2(eye_vector[1], eye_vector[0]) * 180 / np.pi
            
            structure['eye_distance'] = eye_distance
            structure['nose_to_eye_ratio'] = nose_to_eye_center / (eye_distance + 1e-6)
            structure['mouth_to_nose_ratio'] = mouth_to_nose / (eye_distance + 1e-6)
            structure['eye_angle'] = eye_angle
            structure['face_center'] = landmarks.mean(axis=0)
            
        except:
            pass
        
        return structure
    
    def preserve_geometric_consistency(self, source: np.ndarray, target: np.ndarray,
                                      source_landmarks: np.ndarray, target_landmarks: np.ndarray,
                                      mask: np.ndarray) -> np.ndarray:
        """Preserva consistencia geométrica entre source y target."""
        try:
            source_structure = self.analyze_geometric_structure(source_landmarks)
            target_structure = self.analyze_geometric_structure(target_landmarks)
            
            if not source_structure or not target_structure:
                return source
            
            # Detectar diferencias geométricas significativas
            eye_dist_diff = abs(source_structure.get('eye_distance', 0) - 
                               target_structure.get('eye_distance', 0))
            ratio_diff = abs(source_structure.get('nose_to_eye_ratio', 0) - 
                           target_structure.get('nose_to_eye_ratio', 0))
            
            # Si hay diferencias geométricas grandes, ajustar
            if eye_dist_diff > 10 or ratio_diff > 0.15:
                # Crear máscara geométrica para preservar estructura del target
                geom_mask = cv2.GaussianBlur(mask, (41, 41), 0)
                geom_mask_3d = np.stack([geom_mask] * 3, axis=2)
                
                # Mezclar preservando más estructura del target
                result = source.astype(np.float32) * (1 - geom_mask_3d * 0.15) + \
                        target.astype(np.float32) * (geom_mask_3d * 0.15)
                return np.clip(result, 0, 255).astype(np.uint8)
            
        except:
            pass
        
        return source
    
    def advanced_illumination_3d_analysis(self, image: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """Análisis 3D de iluminación usando landmarks."""
        if landmarks is None or len(landmarks) < 5:
            return image
        
        # Convertir a LAB para análisis de luminosidad
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)
        l_channel = lab[:, :, 0]
        
        # Calcular dirección de luz estimada
        # Usar nariz como punto de referencia
        if len(landmarks) == 106:
            nose = landmarks[86] if len(landmarks) > 86 else landmarks[0]
        elif len(landmarks) == 68:
            nose = landmarks[30]
        else:
            return image
        
        # Analizar iluminación alrededor de la nariz
        h, w = image.shape[:2]
        nose_x, nose_y = int(nose[0]), int(nose[1])
        
        # Crear mapa de iluminación estimado mejorado
        y_coords, x_coords = np.ogrid[:h, :w]
        dist_from_nose = np.sqrt((x_coords - nose_x)**2 + (y_coords - nose_y)**2)
        max_dist = np.sqrt(w**2 + h**2)
        normalized_dist = dist_from_nose / max_dist
        
        # Estimar dirección de luz (asumiendo luz desde arriba-izquierda)
        # Mejora: considerar múltiples direcciones
        angle_from_nose = np.arctan2(y_coords - nose_y, x_coords - nose_x)
        light_direction = np.cos(angle_from_nose - np.pi/4) * 0.5 + 0.5  # Luz desde arriba-izquierda
        
        light_map = 1.0 - normalized_dist * 0.25 - (1 - light_direction) * 0.1
        light_map = np.clip(light_map, 0.7, 1.0)
        
        return light_map
    
    def preserve_skin_texture_advanced(self, source: np.ndarray, target: np.ndarray, 
                                      mask: np.ndarray, source_landmarks: np.ndarray = None,
                                      target_landmarks: np.ndarray = None) -> np.ndarray:
        """Preserva la textura de la piel del target con análisis avanzado."""
        # Convertir a escala de grises para análisis de textura
        source_gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY).astype(np.float32)
        target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY).astype(np.float32)
        
        # Análisis de textura en múltiples escalas
        # Escala 1: Detalles finos (poros)
        source_detail_fine = source_gray - cv2.GaussianBlur(source_gray, (3, 3), 0)
        target_detail_fine = target_gray - cv2.GaussianBlur(target_gray, (3, 3), 0)
        
        # Escala 2: Detalles medianos (arrugas, líneas)
        source_detail_medium = source_gray - cv2.GaussianBlur(source_gray, (7, 7), 0)
        target_detail_medium = target_gray - cv2.GaussianBlur(target_gray, (7, 7), 0)
        
        # Escala 3: Detalles gruesos (sombras, iluminación)
        source_detail_coarse = source_gray - cv2.GaussianBlur(source_gray, (15, 15), 0)
        target_detail_coarse = target_gray - cv2.GaussianBlur(target_gray, (15, 15), 0)
        
        # Escala 4: Análisis de textura profundo (nuevo)
        source_detail_deep = source_gray - cv2.GaussianBlur(source_gray, (21, 21), 0)
        target_detail_deep = target_gray - cv2.GaussianBlur(target_gray, (21, 21), 0)
        
        # Crear máscaras adaptativas para cada escala
        mask_fine = cv2.GaussianBlur(mask, (5, 5), 0)
        mask_medium = cv2.GaussianBlur(mask, (15, 15), 0)
        mask_coarse = cv2.GaussianBlur(mask, (31, 31), 0)
        mask_deep = cv2.GaussianBlur(mask, (51, 51), 0)
        
        # Preservar textura del target en diferentes escalas
        # Detalles finos: más preservación del target (poros naturales)
        preserved_fine = source_detail_fine * (1 - mask_fine * 0.5) + target_detail_fine * (mask_fine * 0.5)
        
        # Detalles medianos: mezcla balanceada
        preserved_medium = source_detail_medium * (1 - mask_medium * 0.4) + target_detail_medium * (mask_medium * 0.4)
        
        # Detalles gruesos: más del source (estructura facial)
        preserved_coarse = source_detail_coarse * (1 - mask_coarse * 0.3) + target_detail_coarse * (mask_coarse * 0.3)
        
        # Detalles profundos: preservación de estructura general
        preserved_deep = source_detail_deep * (1 - mask_deep * 0.2) + target_detail_deep * (mask_deep * 0.2)
        
        # Reconstruir imagen desde múltiples escalas (4 escalas ahora)
        base = cv2.GaussianBlur(target_gray, (21, 21), 0)
        texture_blended = (base + preserved_fine * 0.35 + preserved_medium * 0.30 + 
                          preserved_coarse * 0.20 + preserved_deep * 0.15)
        
        return texture_blended
    
    def preserve_skin_texture(self, source: np.ndarray, target: np.ndarray, 
                              mask: np.ndarray) -> np.ndarray:
        """Preserva la textura de la piel del target para mayor realismo."""
        # Usar versión avanzada
        return self.preserve_skin_texture_advanced(source, target, mask, None, None)
    
    def align_face_using_landmarks(self, image: np.ndarray, landmarks: np.ndarray, 
                                  target_size: Tuple[int, int] = (256, 256)) -> Tuple[np.ndarray, np.ndarray]:
        """Alinea cara usando landmarks con transformación mejorada."""
        if landmarks is None or len(landmarks) < 5:
            return image, np.eye(3)
        
        # Puntos de referencia para alineamiento (ojos, nariz, boca)
        if len(landmarks) == 106:  # InsightFace
            # InsightFace: ojos en índices 38, 88, nariz en 86, boca en 78, 84
            left_eye = landmarks[38]
            right_eye = landmarks[88]
            nose = landmarks[86]
            mouth_left = landmarks[78]
            mouth_right = landmarks[84]
        elif len(landmarks) == 468:  # MediaPipe
            # Ojos: índices 33, 133, 159, 145, 362, 263
            left_eye = landmarks[33]
            right_eye = landmarks[263]
            nose = landmarks[4]
            mouth_left = landmarks[61]
            mouth_right = landmarks[291]
        elif len(landmarks) == 68:  # dlib/face-alignment
            left_eye = landmarks[36:42].mean(axis=0)
            right_eye = landmarks[42:48].mean(axis=0)
            nose = landmarks[30]
            mouth_left = landmarks[48]
            mouth_right = landmarks[54]
        else:
            # Usar primeros puntos como aproximación
            left_eye = landmarks[0]
            right_eye = landmarks[1] if len(landmarks) > 1 else landmarks[0]
            nose = landmarks[2] if len(landmarks) > 2 else landmarks[0]
            mouth_left = landmarks[3] if len(landmarks) > 3 else landmarks[0]
            mouth_right = landmarks[4] if len(landmarks) > 4 else landmarks[0]
        
        # Calcular ángulo de rotación
        eye_vector = right_eye - left_eye
        angle = np.degrees(np.arctan2(eye_vector[1], eye_vector[0]))
        
        # Puntos de destino para alineamiento mejorado (usar más puntos)
        target_left_eye = np.array([0.35, 0.35]) * target_size
        target_right_eye = np.array([0.65, 0.35]) * target_size
        target_nose = np.array([0.5, 0.5]) * target_size
        target_mouth_left = np.array([0.4, 0.65]) * target_size
        target_mouth_right = np.array([0.6, 0.65]) * target_size
        
        # Usar transformación de similaridad (más puntos = mejor alineamiento)
        source_points = np.array([left_eye, right_eye, nose, mouth_left, mouth_right], 
                                dtype=np.float32)
        target_points = np.array([target_left_eye, target_right_eye, target_nose,
                                 target_mouth_left, target_mouth_right], dtype=np.float32)
        
        # Calcular transformación de similaridad (preserva ángulos y proporciones)
        # Usar getAffineTransform con 3 puntos o estimateRigidTransform
        if len(source_points) >= 3:
            # Usar los 3 puntos más importantes
            src_3 = np.array([left_eye, right_eye, nose], dtype=np.float32)
            dst_3 = np.array([target_left_eye, target_right_eye, target_nose], dtype=np.float32)
            transform_matrix = cv2.getAffineTransform(src_3, dst_3)
        else:
            transform_matrix = np.eye(2, 3, dtype=np.float32)
        
        # Aplicar transformación con interpolación de alta calidad
        aligned = cv2.warpAffine(image, transform_matrix, target_size, 
                                flags=cv2.INTER_LANCZOS4,
                                borderMode=cv2.BORDER_REPLICATE)
        
        return aligned, transform_matrix
    
    def create_attention_mask(self, image: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """Crea máscara de atención para enfocar en regiones faciales importantes."""
        h, w = image.shape[:2]
        attention_mask = np.zeros((h, w), dtype=np.float32)
        
        if landmarks is None or len(landmarks) < 5:
            return np.ones((h, w), dtype=np.float32)
        
        try:
            # Identificar regiones importantes (ojos, nariz, boca)
            if len(landmarks) == 106:
                # Ojos
                left_eye = landmarks[33:42] if len(landmarks) > 42 else landmarks[33:38]
                right_eye = landmarks[42:51] if len(landmarks) > 51 else landmarks[88:93]
                # Nariz
                nose = landmarks[51:60] if len(landmarks) > 60 else landmarks[86:91]
                # Boca
                mouth = landmarks[76:88] if len(landmarks) > 88 else landmarks[78:84]
            elif len(landmarks) == 68:
                left_eye = landmarks[36:42]
                right_eye = landmarks[42:48]
                nose = landmarks[27:36]
                mouth = landmarks[48:68]
            else:
                return np.ones((h, w), dtype=np.float32)
            
            # Crear máscaras de atención para cada región
            regions = [left_eye, right_eye, nose, mouth]
            weights = [1.5, 1.5, 1.2, 1.3]  # Ojos y boca más importantes
            
            for region, weight in zip(regions, weights):
                if len(region) > 0:
                    # Crear máscara elíptica para la región
                    center = region.mean(axis=0).astype(int)
                    size = np.max(region, axis=0) - np.min(region, axis=0)
                    axes = (int(size[0] * 1.5), int(size[1] * 1.5))
                    
                    if axes[0] > 0 and axes[1] > 0:
                        cv2.ellipse(attention_mask, tuple(center), tuple(axes), 
                                  0, 0, 360, weight, -1)
            
            # Suavizar máscara de atención
            attention_mask = cv2.GaussianBlur(attention_mask, (21, 21), 0)
            attention_mask = np.clip(attention_mask / attention_mask.max(), 0.3, 1.0)
            
        except:
            return np.ones((h, w), dtype=np.float32)
        
        return attention_mask
    
    def adaptive_style_transfer(self, source: np.ndarray, target: np.ndarray,
                               mask: np.ndarray, attention_mask: np.ndarray = None) -> np.ndarray:
        """Transferencia de estilo adaptativa mejorada preservando identidad."""
        if attention_mask is None:
            attention_mask = np.ones(mask.shape, dtype=np.float32)
        
        try:
            # Convertir a LAB para mejor control de color
            source_lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype(np.float32)
            target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)
            
            # Calcular estadísticas de estilo del target
            mask_3d = np.stack([mask * attention_mask] * 3, axis=2)
            target_mean = np.sum(target_lab * mask_3d, axis=(0, 1)) / (np.sum(mask * attention_mask) + 1e-6)
            target_std = np.sqrt(np.sum(((target_lab - target_mean) ** 2) * mask_3d, axis=(0, 1)) / 
                               (np.sum(mask * attention_mask) + 1e-6)) + 1e-6
            
            # Calcular estadísticas del source
            source_mean = np.sum(source_lab * mask_3d, axis=(0, 1)) / (np.sum(mask * attention_mask) + 1e-6)
            source_std = np.sqrt(np.sum(((source_lab - source_mean) ** 2) * mask_3d, axis=(0, 1)) / 
                               (np.sum(mask * attention_mask) + 1e-6)) + 1e-6
            
            # Transferencia de estilo adaptativa
            # Preservar más identidad en regiones de alta atención
            style_weight = 1.0 - attention_mask * 0.3  # Menos transferencia en regiones importantes
            style_weight_3d = np.stack([style_weight] * 3, axis=2)
            
            # Aplicar transferencia de estilo
            result_lab = source_lab.copy()
            for c in range(3):
                # Normalizar
                normalized = (source_lab[:, :, c] - source_mean[c]) / (source_std[c] + 1e-6)
                # Aplicar estilo del target con peso adaptativo
                styled = normalized * target_std[c] * style_weight_3d[:, :, c] + \
                        normalized * source_std[c] * (1 - style_weight_3d[:, :, c])
                # Desnormalizar
                result_lab[:, :, c] = styled + source_mean[c] * (1 - mask * attention_mask * 0.2) + \
                                     target_mean[c] * (mask * attention_mask * 0.2)
            
            result = cv2.cvtColor(np.clip(result_lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
            return result
            
        except:
            return source
    
    def create_precise_mask_from_landmarks(self, shape: Tuple[int, int], 
                                          landmarks: np.ndarray) -> np.ndarray:
        """Crea máscara ultra precisa usando landmarks faciales con forma natural."""
        h, w = shape
        mask = np.zeros((h, w), dtype=np.float32)
        
        if landmarks is None or len(landmarks) < 5:
            # Fallback a máscara elíptica mejorada
            center = (w // 2, h // 2)
            axes = (int(w * 0.48), int(h * 0.58))
            cv2.ellipse(mask, center, axes, 0, 0, 360, 1.0, -1)
            # Suavizado múltiple
            for sigma in [40, 35, 30, 25, 20, 15, 12, 10]:
                mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=sigma, sigmaY=sigma)
            mask = np.clip(mask, 0, 1)
            return mask
        
        # Usar landmarks para crear máscara facial ultra precisa
        if len(landmarks) == 106:  # InsightFace
            # Contorno facial completo de InsightFace
            face_contour_indices = list(range(0, 33))  # Contorno facial
            # Agregar puntos de mejillas y mentón para forma más natural
            cheek_indices = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
            face_points = np.vstack([
                landmarks[face_contour_indices],
                landmarks[cheek_indices] if len(landmarks) > max(cheek_indices) else landmarks[face_contour_indices]
            ]).astype(np.int32)
        elif len(landmarks) == 468:  # MediaPipe
            # Contorno facial completo
            face_contour_indices = [10, 151, 9, 175, 152, 148, 176, 149, 150, 136, 
                                   172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109,
                                   10, 338, 337, 336, 296, 334, 293, 300, 276, 283, 282, 295]
            face_points = landmarks[face_contour_indices].astype(np.int32)
        elif len(landmarks) == 68:  # dlib/face-alignment
            # Contorno facial completo
            face_points = landmarks[0:17].astype(np.int32)
        else:
            # Usar todos los puntos disponibles
            face_points = landmarks.astype(np.int32)
        
        # Crear máscara usando el contorno con forma más natural
        cv2.fillPoly(mask, [face_points], 1.0)
        
        # Aplicar morfología para suavizar y expandir ligeramente
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Suavizado múltiple progresivo para transición ultra suave
        for sigma in [35, 30, 25, 20, 17, 15, 12, 10, 8]:
            mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=sigma, sigmaY=sigma)
        
        # Aplicar curva de suavizado adicional
        mask = np.power(mask, 0.75)  # Hacer transición más gradual
        
        mask = np.clip(mask, 0, 1)
        return mask
    
    def advanced_color_correction_with_skimage(self, source: np.ndarray, target: np.ndarray,
                                              mask: np.ndarray) -> np.ndarray:
        """Corrección de color ultra avanzada usando scikit-image y técnicas combinadas."""
        if not SKIMAGE_AVAILABLE:
            return source
        
        try:
            from skimage import exposure
            
            # Método 1: Histogram matching global
            result_hist = source.copy()
            mask_uint8 = (mask * 255).astype(np.uint8)
            
            for i in range(3):
                source_channel = source[:, :, i]
                target_channel = target[:, :, i]
                
                matched = exposure.match_histograms(
                    source_channel,
                    target_channel,
                    channel_axis=None
                )
                
                result_hist[:, :, i] = np.where(mask_uint8 > 128, matched, source_channel)
            
            # Método 2: Corrección LAB estadística
            source_lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype(np.float32)
            target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)
            mask_3d = np.stack([mask] * 3, axis=2)
            
            # Calcular estadísticas ponderadas
            mask_weighted = mask ** 1.5
            mask_weighted_3d = np.stack([mask_weighted] * 3, axis=2)
            
            source_mean = np.sum(source_lab * mask_weighted_3d, axis=(0, 1)) / (np.sum(mask_weighted) + 1e-6)
            source_std = np.sqrt(np.sum(((source_lab - source_mean) ** 2) * mask_weighted_3d, axis=(0, 1)) / (np.sum(mask_weighted) + 1e-6)) + 1e-6
            
            # Calcular estadísticas del entorno del target
            surrounding_mask = 1 - mask
            surrounding_mask = cv2.GaussianBlur(surrounding_mask, (151, 151), 0)
            surrounding_mask_3d = np.stack([surrounding_mask] * 3, axis=2)
            
            target_mean = np.sum(target_lab * surrounding_mask_3d, axis=(0, 1)) / (np.sum(surrounding_mask) + 1e-6)
            target_std = np.sqrt(np.sum(((target_lab - target_mean) ** 2) * surrounding_mask_3d, axis=(0, 1)) / (np.sum(surrounding_mask) + 1e-6)) + 1e-6
            
            # Aplicar transformación
            corrected_lab = source_lab.copy()
            corrected_lab = (corrected_lab - source_mean) * (target_std / source_std) + target_mean
            
            # Ajuste de luminosidad con blending adaptativo
            l_channel = corrected_lab[:, :, 0]
            target_l_channel = target_lab[:, :, 0]
            
            l_mask = cv2.GaussianBlur(mask, (71, 71), 0) * 0.7 + 0.3
            l_blended = l_channel * l_mask + target_l_channel * (1 - l_mask * 0.4)
            corrected_lab[:, :, 0] = l_blended
            
            result_lab = cv2.cvtColor(np.clip(corrected_lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
            
            # Combinar ambos métodos
            result = cv2.addWeighted(result_hist, 0.4, result_lab, 0.6, 0)
            
            return result.astype(np.uint8)
        except:
            return source
    
    def pre_blend_enhancement(self, image: np.ndarray) -> np.ndarray:
        """Mejora de calidad antes del blending para mejor resultado."""
        # Reducción de ruido preservando detalles
        image = cv2.bilateralFilter(image, 5, 40, 40)
        
        # Mejora de contraste sutil
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        image = cv2.merge([l, a, b])
        image = cv2.cvtColor(image, cv2.COLOR_LAB2BGR)
        
        return image
    
    def enhance_with_pil(self, image: np.ndarray) -> np.ndarray:
        """Mejora de calidad usando PIL con múltiples técnicas."""
        if not PIL_AVAILABLE:
            return image
        
        try:
            # Convertir a PIL
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Aplicar múltiples filtros de calidad
            # 1. Unsharp mask para sharpening natural
            pil_image = pil_image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            # 2. Mejora de contraste sutil
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(1.05)  # 5% más contraste
            
            # 3. Mejora de saturación sutil
            enhancer = ImageEnhance.Color(pil_image)
            pil_image = enhancer.enhance(1.03)  # 3% más saturación
            
            # Convertir de vuelta
            result = np.array(pil_image)
            result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
            
            return result
        except:
            return image
    
    def swap_faces_professional(self, source_image: np.ndarray, 
                               target_image: np.ndarray) -> np.ndarray:
        """Face swap profesional usando todas las librerías disponibles."""
        # Detectar caras
        source_face_rect = self.detect_face(source_image)
        target_face_rect = self.detect_face(target_image)
        
        if source_face_rect is None or target_face_rect is None:
            return target_image
        
        # Obtener landmarks (prioridad: InsightFace > face-alignment > MediaPipe)
        source_landmarks = None
        target_landmarks = None
        
        if INSIGHTFACE_AVAILABLE:
            source_landmarks = self.get_face_landmarks_insightface(source_image)
            target_landmarks = self.get_face_landmarks_insightface(target_image)
        
        if source_landmarks is None and FACE_ALIGNMENT_AVAILABLE:
            source_landmarks = self.get_face_landmarks_face_alignment(source_image)
        
        if target_landmarks is None and FACE_ALIGNMENT_AVAILABLE:
            target_landmarks = self.get_face_landmarks_face_alignment(target_image)
        
        if source_landmarks is None and MEDIAPIPE_AVAILABLE:
            source_landmarks = self.get_face_landmarks_mediapipe(source_image)
        
        if target_landmarks is None and MEDIAPIPE_AVAILABLE:
            target_landmarks = self.get_face_landmarks_mediapipe(target_image)
        
        # Extraer regiones de cara
        x, y, w, h = source_face_rect
        source_region = source_image[y:y+h, x:x+w].copy()
        
        x, y, w, h = target_face_rect
        target_region = target_image[y:y+h, x:x+w].copy()
        
        # Alinear caras si tenemos landmarks
        if source_landmarks is not None and target_landmarks is not None:
            # Ajustar landmarks a la región extraída
            source_landmarks_region = source_landmarks.copy()
            source_landmarks_region[:, 0] -= source_face_rect[0]
            source_landmarks_region[:, 1] -= source_face_rect[1]
            
            target_landmarks_region = target_landmarks.copy()
            target_landmarks_region[:, 0] -= target_face_rect[0]
            target_landmarks_region[:, 1] -= target_face_rect[1]
            
            # Alinear source a target con transformación mejorada
            source_aligned, transform_matrix = self.align_face_using_landmarks(
                source_region, source_landmarks_region, 
                target_size=(target_region.shape[1], target_region.shape[0])
            )
            
            # Redimensionar si es necesario con técnica avanzada
            if source_aligned.shape != target_region.shape:
                # Usar redimensionamiento progresivo para mejor calidad
                current = source_aligned
                target_w, target_h = target_region.shape[1], target_region.shape[0]
                
                # Si la diferencia es grande, hacer en pasos
                scale = max(target_w / current.shape[1], target_h / current.shape[0])
                if scale > 1.5 or scale < 0.7:
                    # Redimensionamiento progresivo
                    while abs(current.shape[1] - target_w) > 10 or abs(current.shape[0] - target_h) > 10:
                        next_w = int(current.shape[1] * (1 + np.sign(target_w - current.shape[1]) * 0.1))
                        next_h = int(current.shape[0] * (1 + np.sign(target_h - current.shape[0]) * 0.1))
                        current = cv2.resize(current, (next_w, next_h), interpolation=cv2.INTER_LANCZOS4)
                    
                    source_aligned = cv2.resize(current, (target_w, target_h), 
                                               interpolation=cv2.INTER_LANCZOS4)
                else:
                    source_aligned = cv2.resize(source_aligned, (target_w, target_h),
                                               interpolation=cv2.INTER_LANCZOS4)
            
            # Aplicar aumentación de calidad con Albumentations si está disponible
            if ALBUMENTATIONS_AVAILABLE:
                try:
                    transform = A.Compose([
                        A.CLAHE(clip_limit=2.5, tile_grid_size=(8, 8), p=0.6),
                        A.RandomBrightnessContrast(brightness_limit=0.08, contrast_limit=0.08, p=0.4),
                        A.GaussNoise(var_limit=(5.0, 10.0), p=0.2),  # Reducción de ruido
                    ])
                    source_aligned = transform(image=source_aligned)['image']
                except:
                    pass
        else:
            # Sin landmarks, usar redimensionamiento simple
            source_aligned = cv2.resize(source_region,
                                       (target_region.shape[1], target_region.shape[0]),
                                       interpolation=cv2.INTER_LANCZOS4)
        
        # Crear máscara precisa
        if target_landmarks is not None:
            target_landmarks_region = target_landmarks.copy()
            target_landmarks_region[:, 0] -= target_face_rect[0]
            target_landmarks_region[:, 1] -= target_face_rect[1]
            mask = self.create_precise_mask_from_landmarks(
                target_region.shape[:2], target_landmarks_region
            )
        else:
            # Máscara elíptica fallback
            h, w = target_region.shape[:2]
            mask = np.zeros((h, w), dtype=np.float32)
            cv2.ellipse(mask, (w//2, h//2), (int(w*0.45), int(h*0.55)), 0, 0, 360, 1.0, -1)
            for sigma in [30, 25, 20, 15, 10]:
                mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=sigma, sigmaY=sigma)
            mask = np.clip(mask, 0, 1)
        
        # Crear máscara de atención (NUEVO)
        attention_mask = None
        if target_landmarks is not None:
            target_landmarks_region = target_landmarks.copy()
            target_landmarks_region[:, 0] -= target_face_rect[0]
            target_landmarks_region[:, 1] -= target_face_rect[1]
            attention_mask = self.create_attention_mask(target_region, target_landmarks_region)
        
        # Corrección de color ultra avanzada
        if SKIMAGE_AVAILABLE:
            source_corrected = self.advanced_color_correction_with_skimage(
                source_aligned, target_region, mask
            )
        else:
            # Fallback básico
            source_corrected = source_aligned
        
        # Aplicar transferencia de estilo adaptativa (NUEVO)
        if attention_mask is not None:
            source_corrected = self.adaptive_style_transfer(
                source_corrected, target_region, mask, attention_mask
            )
        else:
            # Fallback a corrección básica
            source_lab = cv2.cvtColor(source_aligned, cv2.COLOR_BGR2LAB).astype(np.float32)
            target_lab = cv2.cvtColor(target_region, cv2.COLOR_BGR2LAB).astype(np.float32)
            mask_3d = np.stack([mask] * 3, axis=2)
            
            source_mean = np.sum(source_lab * mask_3d, axis=(0, 1)) / (np.sum(mask) + 1e-6)
            target_mean = np.sum(target_lab * mask_3d, axis=(0, 1)) / (np.sum(mask) + 1e-6)
            
            source_corrected_lab = source_lab - source_mean + target_mean
            source_corrected = cv2.cvtColor(
                np.clip(source_corrected_lab, 0, 255).astype(np.uint8),
                cv2.COLOR_LAB2BGR
            )
        
        # Aplicar corrección de iluminación avanzada
        source_corrected = self.apply_advanced_illumination_correction(
            source_corrected, target_region, mask
        )
        
        # Preservar características de expresión del target
        if source_landmarks is not None and target_landmarks is not None:
            source_landmarks_region = source_landmarks.copy()
            source_landmarks_region[:, 0] -= source_face_rect[0]
            source_landmarks_region[:, 1] -= source_face_rect[1]
            
            target_landmarks_region = target_landmarks.copy()
            target_landmarks_region[:, 0] -= target_face_rect[0]
            target_landmarks_region[:, 1] -= target_face_rect[1]
            
            source_corrected = self.preserve_expression_features(
                source_corrected, target_region,
                source_landmarks_region, target_landmarks_region, mask
            )
        
        # Análisis 3D de iluminación
        if target_landmarks is not None:
            target_landmarks_region = target_landmarks.copy()
            target_landmarks_region[:, 0] -= target_face_rect[0]
            target_landmarks_region[:, 1] -= target_face_rect[1]
            
            light_map = self.advanced_illumination_3d_analysis(
                source_corrected, target_landmarks_region
            )
            if light_map is not None:
                light_map_3d = np.stack([light_map] * 3, axis=2)
                source_corrected = source_corrected.astype(np.float32) * light_map_3d
                source_corrected = np.clip(source_corrected, 0, 255).astype(np.uint8)
        
        # Detectar oclusiones (NUEVO)
        occlusion_mask = None
        if target_landmarks is not None:
            target_landmarks_region = target_landmarks.copy()
            target_landmarks_region[:, 0] -= target_face_rect[0]
            target_landmarks_region[:, 1] -= target_face_rect[1]
            occlusion_mask = self.detect_occlusions(target_region, target_landmarks_region)
        
        # Blending ultra avanzado con múltiples técnicas
        # Intentar frecuencia primero (más avanzado)
        try:
            blended_freq = self.frequency_domain_enhancement(
                source_corrected, target_region, mask
            )
            # Mezclar con Poisson si está disponible
            if SCIPY_AVAILABLE:
                try:
                    blended_poisson = self.poisson_blending_advanced(
                        source_corrected, target_region, mask
                    )
                    # Combinar ambos métodos
                    blended = cv2.addWeighted(blended_freq, 0.4, blended_poisson, 0.6, 0)
                except:
                    blended = blended_freq
            else:
                blended = blended_freq
        except:
            # Fallback a Poisson o multi-scale
            if SCIPY_AVAILABLE:
                try:
                    blended = self.poisson_blending_advanced(
                        source_corrected, target_region, mask
                    )
                except:
                    blended = self.advanced_multi_scale_blending(
                        source_corrected, target_region, mask
                    )
            else:
                blended = self.advanced_multi_scale_blending(
                    source_corrected, target_region, mask
                )
        
        # Manejar oclusiones preservando más del target (NUEVO)
        if occlusion_mask is not None:
            occlusion_mask_3d = np.stack([occlusion_mask] * 3, axis=2)
            # En áreas con oclusiones, preservar más del target
            blended = blended.astype(np.float32) * (1 - occlusion_mask_3d * 0.2) + \
                     target_region.astype(np.float32) * (occlusion_mask_3d * 0.2)
            blended = np.clip(blended, 0, 255).astype(np.uint8)
        
        # Seamless cloning mejorado
        try:
            mask_uint8 = (mask * 255).astype(np.uint8)
            # Mejorar máscara para seamless cloning
            mask_uint8 = cv2.dilate(mask_uint8, np.ones((5, 5), np.uint8), iterations=1)
            mask_uint8 = cv2.GaussianBlur(mask_uint8, (15, 15), 0)
            
            # Calcular centro óptimo
            moments = cv2.moments(mask_uint8)
            if moments["m00"] != 0:
                center_x = int(moments["m10"] / moments["m00"])
                center_y = int(moments["m01"] / moments["m00"])
                center = (center_x, center_y)
            else:
                center = (target_region.shape[1] // 2, target_region.shape[0] // 2)
            
            # Intentar múltiples métodos de seamless cloning
            try:
                blended = cv2.seamlessClone(source_corrected, target_region, mask_uint8,
                                           center, cv2.NORMAL_CLONE)
            except:
                try:
                    blended = cv2.seamlessClone(source_corrected, target_region, mask_uint8,
                                               center, cv2.MIXED_CLONE)
                except:
                    pass
        except:
            pass
        
        # Mejora con PIL si está disponible
        if PIL_AVAILABLE:
            blended = self.enhance_with_pil(blended)
        
        # Mejora perceptual de calidad (NUEVO)
        blended = self.enhance_perceptual_quality(blended)
        
        # Post-procesamiento final ultra mejorado
        blended = self.advanced_post_processing(blended, target_region, mask)
        
        # Insertar de vuelta con blending ultra suave en bordes
        result = target_image.copy()
        x, y, w, h = target_face_rect
        
        # Crear máscara de inserción ultra suave con múltiples niveles
        insert_mask_base = np.ones((h, w), dtype=np.float32)
        insert_masks = [
            insert_mask_base,  # Nivel 1
            cv2.GaussianBlur(insert_mask_base, (15, 15), 0),  # Nivel 2
            cv2.GaussianBlur(insert_mask_base, (31, 31), 0),  # Nivel 3
            cv2.GaussianBlur(insert_mask_base, (51, 51), 0),  # Nivel 4
        ]
        
        # Mezclar suavemente en la región con múltiples niveles
        result_region = result[y:y+h, x:x+w].astype(np.float32)
        blended_f = blended.astype(np.float32)
        
        # Crear región final con blending multi-nivel
        final_region = result_region.copy()
        for i, im in enumerate(insert_masks):
            weight = [0.05, 0.10, 0.15, 0.20][i]  # Pesos progresivos
            im_3d = np.stack([im] * 3, axis=2)
            final_region = final_region * (1 - im_3d * weight) + blended_f * (im_3d * weight)
        
        # Asegurar que el centro esté completamente reemplazado
        center_mask = np.zeros((h, w), dtype=np.float32)
        cv2.circle(center_mask, (w//2, h//2), min(w, h)//3, 1.0, -1)
        center_mask = cv2.GaussianBlur(center_mask, (21, 21), 0)
        center_mask_3d = np.stack([center_mask] * 3, axis=2)
        
        final_region = final_region * (1 - center_mask_3d) + blended_f * center_mask_3d
        
        result[y:y+h, x:x+w] = np.clip(final_region, 0, 255).astype(np.uint8)
        
        # Mejora de detalles estructurales (NUEVO)
        if target_landmarks is not None:
            target_landmarks_full = target_landmarks.copy()
            result = self.enhance_structural_details(result, target_landmarks_full)
        
        # Mejora de características faciales específicas (NUEVO)
        if target_landmarks is not None:
            target_landmarks_full = target_landmarks.copy()
            result = self.enhance_facial_features(result, target_landmarks_full)
        
        # Reducción avanzada de artefactos (NUEVO)
        face_mask_full = np.zeros(result.shape[:2], dtype=np.float32)
        face_mask_full[y:y+h, x:x+w] = 1.0
        result = self.reduce_artifacts_advanced(result, face_mask_full)
        
        # Mejora de detalles finos (NUEVO)
        result = self.enhance_fine_details(result, face_mask_full)
        
        # Mejora de detalles de alta frecuencia (NUEVO)
        result = self.enhance_high_frequency_details(result, face_mask_full)
        
        # Análisis y mejora de coherencia espacial (NUEVO)
        result = self.analyze_spatial_coherence(result, face_mask_full)
        
        # Preservación de simetría facial (NUEVO)
        if target_landmarks is not None:
            target_landmarks_full = target_landmarks.copy()
            result = self.preserve_facial_symmetry(result, target_landmarks_full)
        
        # Post-procesamiento final de toda la imagen
        result = self.final_image_enhancement(result, target_image, x, y, w, h)
        
        return result
    
    def adaptive_quality_enhancement(self, image: np.ndarray) -> np.ndarray:
        """Mejora adaptativa de calidad basada en características de la imagen."""
        h, w = image.shape[:2]
        
        # Analizar calidad de la imagen
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calcular métricas de calidad
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = gray.mean()
        contrast = gray.std()
        
        # Ajustar mejoras según calidad detectada
        if laplacian_var < 100:  # Imagen borrosa
            # Aplicar sharpening más agresivo
            kernel = np.array([[-0.3, -0.7, -0.3],
                              [-0.7,  4.7, -0.7],
                              [-0.3, -0.7, -0.3]])
            sharpened = cv2.filter2D(image, -1, kernel)
            image = cv2.addWeighted(image, 0.7, sharpened, 0.3, 0)
        
        if brightness < 80:  # Imagen oscura
            # Mejorar brillo sutilmente
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
            l = clahe.apply(l)
            image = cv2.merge([l, a, b])
            image = cv2.cvtColor(image, cv2.COLOR_LAB2BGR)
        
        if contrast < 30:  # Bajo contraste
            # Mejorar contraste
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l = np.clip(l.astype(np.float32) * 1.1, 0, 255).astype(np.uint8)
            image = cv2.merge([l, a, b])
            image = cv2.cvtColor(image, cv2.COLOR_LAB2BGR)
        
        return image
    
    def final_image_enhancement(self, result: np.ndarray, target: np.ndarray,
                               face_x: int, face_y: int, face_w: int, face_h: int) -> np.ndarray:
        """Mejora final ultra avanzada de toda la imagen para máxima coherencia."""
        # Aplicar mejora adaptativa de calidad (NUEVO)
        result = self.adaptive_quality_enhancement(result)
        
        # Crear máscara de la región facial con múltiples niveles
        mask_full = np.zeros(result.shape[:2], dtype=np.float32)
        mask_full[face_y:face_y+face_h, face_x:face_x+face_w] = 1.0
        
        # Crear múltiples niveles de máscara
        mask_levels = [
            cv2.GaussianBlur(mask_full, (51, 51), 0),
            cv2.GaussianBlur(mask_full, (101, 101), 0),
            cv2.GaussianBlur(mask_full, (201, 201), 0),
        ]
        
        # Ajustar brillo y contraste global para coherencia
        result_lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB).astype(np.float32)
        target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        # Calcular estadísticas globales y locales
        result_l = result_lab[:, :, 0]
        target_l = target_lab[:, :, 0]
        
        result_l_mean = result_l.mean()
        target_l_mean = target_l.mean()
        
        # Ajustar brillo global con múltiples niveles
        diff = target_l_mean - result_l_mean
        
        # Aplicar ajuste progresivo según distancia de la cara
        for i, mask_level in enumerate(mask_levels):
            weight = [0.15, 0.10, 0.05][i]
            adjustment = diff * weight
            outside_mask = 1 - mask_level
            outside_mask_3d = np.stack([outside_mask] * 3, axis=2)
            
            result_lab[:, :, 0] = result_lab[:, :, 0] + adjustment * outside_mask_3d[:, :, 0]
        
        # Ajuste de contraste global sutil
        result_l_std = result_l.std()
        target_l_std = target_l.std()
        
        if result_l_std > 0:
            contrast_ratio = min(target_l_std / result_l_std, 1.1)  # Máximo 10% aumento
            result_lab[:, :, 0] = (result_lab[:, :, 0] - result_l_mean) * contrast_ratio + result_l_mean
        
        # Ajuste de saturación global para coherencia
        result_a = result_lab[:, :, 1]
        result_b = result_lab[:, :, 2]
        target_a = target_lab[:, :, 1]
        target_b = target_lab[:, :, 2]
        
        result_a_mean = result_a.mean()
        target_a_mean = target_a.mean()
        result_b_mean = result_b.mean()
        target_b_mean = target_b.mean()
        
        # Ajuste sutil de saturación fuera de la cara
        outside_mask_final = 1 - mask_levels[2]
        outside_mask_final_3d = np.stack([outside_mask_final] * 3, axis=2)
        
        a_adjustment = (target_a_mean - result_a_mean) * 0.05
        b_adjustment = (target_b_mean - result_b_mean) * 0.05
        
        result_lab[:, :, 1] = result_lab[:, :, 1] + a_adjustment * outside_mask_final_3d[:, :, 1]
        result_lab[:, :, 2] = result_lab[:, :, 2] + b_adjustment * outside_mask_final_3d[:, :, 2]
        
        result = cv2.cvtColor(np.clip(result_lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
        
        # Reducción final de ruido muy sutil en toda la imagen
        result = cv2.bilateralFilter(result, 3, 20, 20)
        
        return result
    
    def perceptual_quality_analysis(self, image: np.ndarray) -> dict:
        """Análisis perceptual de calidad de imagen."""
        metrics = {}
        
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 1. Análisis de nitidez (sharpness)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()
            metrics['sharpness'] = sharpness
            
            # 2. Análisis de contraste
            contrast = gray.std()
            metrics['contrast'] = contrast
            
            # 3. Análisis de brillo
            brightness = gray.mean()
            metrics['brightness'] = brightness
            
            # 4. Análisis de textura (entropía)
            # Calcular histograma
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = hist.flatten()
            hist = hist / (hist.sum() + 1e-6)  # Normalizar
            entropy = -np.sum(hist * np.log(hist + 1e-6))
            metrics['texture_entropy'] = entropy
            
            # 5. Análisis de uniformidad
            uniformity = np.sum(hist ** 2)
            metrics['uniformity'] = uniformity
            
        except:
            pass
        
        return metrics
    
    def enhance_perceptual_quality(self, image: np.ndarray) -> np.ndarray:
        """Mejora perceptual de calidad basada en análisis."""
        try:
            # Analizar calidad perceptual
            metrics = self.perceptual_quality_analysis(image)
            
            if not metrics:
                return image
            
            # Ajustar según métricas
            result = image.copy()
            
            # Mejorar nitidez si es baja
            if metrics.get('sharpness', 0) < 100:
                kernel = np.array([[-0.15, -0.4, -0.15],
                                  [-0.4,  2.3, -0.4],
                                  [-0.15, -0.4, -0.15]])
                sharpened = cv2.filter2D(result, -1, kernel)
                result = cv2.addWeighted(result, 0.85, sharpened, 0.15, 0)
            
            # Mejorar contraste si es bajo
            if metrics.get('contrast', 0) < 30:
                lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                l = np.clip(l.astype(np.float32) * 1.12, 0, 255).astype(np.uint8)
                result = cv2.merge([l, a, b])
                result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
            
            # Mejorar textura si es muy uniforme
            if metrics.get('uniformity', 0) > 0.15:
                # Aplicar filtro de textura sutil
                gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
                texture = cv2.Laplacian(gray, cv2.CV_64F)
                texture = np.abs(texture)
                texture = cv2.GaussianBlur(texture, (5, 5), 0)
                if texture.max() > 0:
                    texture = np.clip(texture / texture.max(), 0, 1)
                    texture_3d = np.stack([texture] * 3, axis=2)
                    # Aplicar sharpening selectivo
                    kernel = np.array([[-0.1, -0.2, -0.1],
                                      [-0.2,  1.2, -0.2],
                                      [-0.1, -0.2, -0.1]])
                    sharpened = cv2.filter2D(result, -1, kernel)
                    result = result.astype(np.float32) * (1 - texture_3d * 0.1) + \
                            sharpened.astype(np.float32) * (texture_3d * 0.1)
                    result = np.clip(result, 0, 255).astype(np.uint8)
            
        except:
            pass
        
        return result
    
    def analyze_facial_symmetry(self, image: np.ndarray, landmarks: np.ndarray) -> dict:
        """Análisis de simetría facial para mejor preservación."""
        symmetry = {}
        if landmarks is None or len(landmarks) < 5:
            return symmetry
        
        try:
            h, w = image.shape[:2]
            
            # Encontrar puntos clave de simetría
            if len(landmarks) == 106:
                # InsightFace: puntos de ojos y boca
                left_eye = landmarks[36] if len(landmarks) > 36 else landmarks[0]
                right_eye = landmarks[45] if len(landmarks) > 45 else landmarks[0]
                nose_tip = landmarks[86] if len(landmarks) > 86 else landmarks[0]
                mouth_left = landmarks[48] if len(landmarks) > 48 else landmarks[0]
                mouth_right = landmarks[54] if len(landmarks) > 54 else landmarks[0]
            elif len(landmarks) == 68:
                # face-alignment: puntos estándar
                left_eye = landmarks[36]
                right_eye = landmarks[45]
                nose_tip = landmarks[30]
                mouth_left = landmarks[48]
                mouth_right = landmarks[54]
            else:
                return symmetry
            
            # Calcular línea central de simetría
            center_x = (left_eye[0] + right_eye[0]) / 2
            symmetry['center_x'] = center_x
            
            # Calcular asimetría de ojos
            eye_distance_left = np.sqrt((left_eye[0] - center_x)**2 + (left_eye[1] - nose_tip[1])**2)
            eye_distance_right = np.sqrt((right_eye[0] - center_x)**2 + (right_eye[1] - nose_tip[1])**2)
            eye_asymmetry = abs(eye_distance_left - eye_distance_right) / max(eye_distance_left, eye_distance_right)
            symmetry['eye_asymmetry'] = eye_asymmetry
            
            # Calcular asimetría de boca
            mouth_distance_left = np.sqrt((mouth_left[0] - center_x)**2 + (mouth_left[1] - nose_tip[1])**2)
            mouth_distance_right = np.sqrt((mouth_right[0] - center_x)**2 + (mouth_right[1] - nose_tip[1])**2)
            mouth_asymmetry = abs(mouth_distance_left - mouth_distance_right) / max(mouth_distance_left, mouth_distance_right)
            symmetry['mouth_asymmetry'] = mouth_asymmetry
            
            # Calcular simetría general
            symmetry['overall_symmetry'] = 1.0 - (eye_asymmetry + mouth_asymmetry) / 2
            
        except:
            pass
        
        return symmetry
    
    def preserve_facial_symmetry(self, image: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """Preserva y mejora la simetría facial."""
        if landmarks is None or len(landmarks) < 5:
            return image
        
        try:
            symmetry = self.analyze_facial_symmetry(image, landmarks)
            if not symmetry or symmetry.get('overall_symmetry', 1.0) > 0.95:
                return image  # Ya es simétrico
            
            # Si hay asimetría significativa, aplicar corrección sutil
            center_x = symmetry.get('center_x', image.shape[1] / 2)
            h, w = image.shape[:2]
            
            # Crear máscara de corrección de simetría
            symmetry_mask = np.ones((h, w), dtype=np.float32)
            for y in range(h):
                for x in range(w):
                    dist_from_center = abs(x - center_x) / (w / 2)
                    # Reducir peso en bordes para corrección más suave
                    symmetry_mask[y, x] = 1.0 - dist_from_center * 0.1
            
            symmetry_mask = cv2.GaussianBlur(symmetry_mask, (15, 15), 0)
            symmetry_mask_3d = np.stack([symmetry_mask] * 3, axis=2)
            
            # Aplicar corrección de simetría muy sutil
            # Reflejar lado derecho al izquierdo y viceversa con peso bajo
            left_half = image[:, :int(center_x)].copy()
            right_half = image[:, int(center_x):].copy()
            
            # Reflejar y combinar
            left_flipped = cv2.flip(left_half, 1)
            right_flipped = cv2.flip(right_half, 1)
            
            # Ajustar tamaños si es necesario
            if left_flipped.shape[1] != right_half.shape[1]:
                min_w = min(left_flipped.shape[1], right_half.shape[1])
                left_flipped = left_flipped[:, :min_w]
                right_half = right_half[:, :min_w]
            
            if right_flipped.shape[1] != left_half.shape[1]:
                min_w = min(right_flipped.shape[1], left_half.shape[1])
                right_flipped = right_flipped[:, :min_w]
                left_half = left_half[:, :min_w]
            
            # Crear imagen simétrica promedio
            left_symmetric = (left_half.astype(np.float32) + right_flipped.astype(np.float32)) / 2
            right_symmetric = (right_half.astype(np.float32) + left_flipped.astype(np.float32)) / 2
            
            # Combinar con peso muy bajo para preservar características originales
            asymmetry_factor = 1.0 - symmetry.get('overall_symmetry', 1.0)
            blend_weight = min(asymmetry_factor * 0.15, 0.1)  # Máximo 10% de corrección
            
            result = image.copy()
            if left_symmetric.shape[1] == left_half.shape[1]:
                result[:, :int(center_x)] = (
                    result[:, :int(center_x)].astype(np.float32) * (1 - blend_weight) +
                    left_symmetric.astype(np.float32) * blend_weight
                ).astype(np.uint8)
            
            if right_symmetric.shape[1] == right_half.shape[1]:
                result[:, int(center_x):] = (
                    result[:, int(center_x):].astype(np.float32) * (1 - blend_weight) +
                    right_symmetric.astype(np.float32) * blend_weight
                ).astype(np.uint8)
            
            return result
            
        except:
            return image
    
    def enhance_high_frequency_details(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Mejora de detalles de alta frecuencia preservando textura natural."""
        try:
            # Convertir a escala de grises para análisis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Extraer detalles de alta frecuencia usando múltiples kernels
            # Kernel 1: Detalles muy finos (3x3)
            details_fine = gray.astype(np.float32) - cv2.GaussianBlur(gray, (3, 3), 0).astype(np.float32)
            
            # Kernel 2: Detalles medios (5x5)
            details_medium = gray.astype(np.float32) - cv2.GaussianBlur(gray, (5, 5), 0).astype(np.float32)
            
            # Kernel 3: Detalles gruesos (7x7)
            details_coarse = gray.astype(np.float32) - cv2.GaussianBlur(gray, (7, 7), 0).astype(np.float32)
            
            # Combinar detalles con pesos adaptativos
            combined_details = (
                details_fine * 0.5 +
                details_medium * 0.3 +
                details_coarse * 0.2
            )
            
            # Aplicar máscara para enfocar en región facial
            mask_blur = cv2.GaussianBlur(mask, (5, 5), 0)
            combined_details = combined_details * mask_blur
            
            # Aplicar detalles mejorados
            result = image.copy().astype(np.float32)
            for c in range(3):
                result[:, :, c] = np.clip(
                    result[:, :, c] + combined_details * 0.12,  # Peso conservador
                    0, 255
                )
            
            return result.astype(np.uint8)
            
        except:
            return image
    
    def analyze_spatial_coherence(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Análisis de coherencia espacial para mejor integración."""
        try:
            # Analizar gradientes locales
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calcular gradientes en X e Y
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Analizar coherencia local usando varianza de gradientes
            kernel_size = 5
            kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size * kernel_size)
            local_mean = cv2.filter2D(grad_magnitude, -1, kernel)
            local_var = cv2.filter2D((grad_magnitude - local_mean)**2, -1, kernel)
            
            # Crear máscara de coherencia (baja varianza = alta coherencia)
            coherence = 1.0 / (1.0 + local_var / (local_mean + 1e-6))
            coherence = np.clip(coherence, 0, 1)
            
            # Aplicar suavizado en regiones de baja coherencia
            low_coherence_mask = (coherence < 0.5).astype(np.float32)
            low_coherence_mask = cv2.GaussianBlur(low_coherence_mask, (7, 7), 0)
            
            # Aplicar bilateral filter selectivo en regiones de baja coherencia
            result = image.copy()
            if np.sum(low_coherence_mask) > 0:
                smoothed = cv2.bilateralFilter(image, 5, 20, 20)
                low_coherence_mask_3d = np.stack([low_coherence_mask] * 3, axis=2)
                result = (
                    result.astype(np.float32) * (1 - low_coherence_mask_3d * 0.3) +
                    smoothed.astype(np.float32) * (low_coherence_mask_3d * 0.3)
                ).astype(np.uint8)
            
            return result
            
        except:
            return image
    
    def preserve_visual_features(self, source: np.ndarray, target: np.ndarray,
                                mask: np.ndarray) -> np.ndarray:
        """Preserva características visuales importantes del source."""
        try:
            # Analizar características visuales
            source_metrics = self.perceptual_quality_analysis(source)
            target_metrics = self.perceptual_quality_analysis(target)
            
            if not source_metrics or not target_metrics:
                return source
            
            # Preservar nitidez del source si es mejor
            if source_metrics.get('sharpness', 0) > target_metrics.get('sharpness', 0) * 1.1:
                # Extraer detalles del source
                source_gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
                target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
                
                source_details = source_gray.astype(np.float32) - \
                                cv2.GaussianBlur(source_gray, (3, 3), 0).astype(np.float32)
                
                mask_blur = cv2.GaussianBlur(mask, (7, 7), 0)
                mask_3d = np.stack([mask_blur] * 3, axis=2)
                
                # Aplicar detalles del source
                result = source.astype(np.float32) + \
                        np.stack([source_details] * 3, axis=2) * mask_3d * 0.15
                result = np.clip(result, 0, 255).astype(np.uint8)
                return result
            
        except:
            pass
        
        return source
    
    def final_save_enhancement(self, image: np.ndarray) -> np.ndarray:
        """Mejora final antes de guardar para máxima calidad."""
        # Aplicar mejora perceptual (NUEVO)
        image = self.enhance_perceptual_quality(image)
        
        # Sharpening final muy sutil
        kernel = np.array([[0, -0.1, 0],
                          [-0.1, 1.4, -0.1],
                          [0, -0.1, 0]])
        sharpened = cv2.filter2D(image, -1, kernel)
        image = cv2.addWeighted(image, 0.95, sharpened, 0.05, 0)
        
        # Reducción final de ruido muy sutil
        image = cv2.bilateralFilter(image, 3, 20, 20)
        
        return image
    
    def apply_advanced_illumination_correction(self, source: np.ndarray, target: np.ndarray,
                                              mask: np.ndarray) -> np.ndarray:
        """Corrección de iluminación ultra avanzada con análisis de gradientes."""
        source_lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype(np.float32)
        target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        # Analizar iluminación del target con gradientes
        target_l = target_lab[:, :, 0]
        source_l = source_lab[:, :, 0]
        
        # Calcular gradientes de iluminación
        grad_x_target = cv2.Sobel(target_l, cv2.CV_32F, 1, 0, ksize=5)
        grad_y_target = cv2.Sobel(target_l, cv2.CV_32F, 0, 1, ksize=5)
        
        grad_x_source = cv2.Sobel(source_l, cv2.CV_32F, 1, 0, ksize=5)
        grad_y_source = cv2.Sobel(source_l, cv2.CV_32F, 0, 1, ksize=5)
        
        # Crear máscara de blending para iluminación (múltiples niveles)
        illum_mask_soft = cv2.GaussianBlur(mask, (151, 151), 0)
        illum_mask_hard = cv2.GaussianBlur(mask, (51, 51), 0)
        
        # Mezclar gradientes (preservar dirección de luz del target)
        grad_x = grad_x_source * (1 - illum_mask_soft * 0.6) + grad_x_target * (illum_mask_soft * 0.6)
        grad_y = grad_y_source * (1 - illum_mask_soft * 0.6) + grad_y_target * (illum_mask_soft * 0.6)
        
        # Transferir iluminación base gradualmente
        source_l_base = source_l * (1 - illum_mask_soft * 0.5) + target_l * (illum_mask_soft * 0.5)
        
        # Aplicar corrección de gradientes (aproximación)
        # Integrar gradientes para reconstruir iluminación
        source_l_corrected = source_l_base.copy()
        
        # Ajuste fino con gradientes en área de transición
        transition_area = illum_mask_hard * (1 - mask * 0.5)
        source_l_corrected = source_l_corrected + (grad_x + grad_y) * transition_area * 0.3
        
        source_lab[:, :, 0] = np.clip(source_l_corrected, 0, 255)
        
        result = cv2.cvtColor(source_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
        return result
    
    def frequency_domain_enhancement(self, source: np.ndarray, target: np.ndarray,
                                    mask: np.ndarray) -> np.ndarray:
        """Mejora usando análisis de frecuencia (FFT) para preservar detalles."""
        try:
            # Convertir a escala de grises
            source_gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY).astype(np.float32)
            target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY).astype(np.float32)
            
            # Aplicar FFT
            source_fft = np.fft.fft2(source_gray)
            target_fft = np.fft.fft2(target_gray)
            
            # Separar magnitud y fase
            source_magnitude = np.abs(source_fft)
            source_phase = np.angle(source_fft)
            target_magnitude = np.abs(target_fft)
            target_phase = np.angle(target_fft)
            
            # Crear máscara en dominio de frecuencia
            mask_fft = cv2.resize(mask, (source_gray.shape[1], source_gray.shape[0]))
            mask_fft = cv2.GaussianBlur(mask_fft, (21, 21), 0)
            
            # Mezclar magnitudes (preservar detalles de alta frecuencia del source)
            # Frecuencias altas (detalles) del source, bajas (estructura) del target
            h, w = source_gray.shape
            center_y, center_x = h // 2, w // 2
            y_coords, x_coords = np.ogrid[:h, :w]
            dist_from_center = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
            max_dist = np.sqrt(center_x**2 + center_y**2)
            freq_mask = np.clip(dist_from_center / max_dist, 0, 1)  # 0 = baja freq, 1 = alta freq
            
            # Mezclar: alta frecuencia del source, baja frecuencia del target
            blended_magnitude = (source_magnitude * freq_mask * mask_fft + 
                               target_magnitude * (1 - freq_mask * mask_fft))
            
            # Usar fase del target para mejor integración
            blended_phase = target_phase * (1 - mask_fft * 0.3) + source_phase * (mask_fft * 0.3)
            
            # Reconstruir
            blended_fft = blended_magnitude * np.exp(1j * blended_phase)
            result_gray = np.real(np.fft.ifft2(blended_fft))
            result_gray = np.clip(result_gray, 0, 255)
            
            # Convertir de vuelta a BGR y mezclar con colores
            result_gray_bgr = cv2.cvtColor(result_gray.astype(np.uint8), cv2.COLOR_GRAY2BGR)
            mask_3d = np.stack([mask] * 3, axis=2)
            result = result_gray_bgr.astype(np.float32) * mask_3d + source.astype(np.float32) * (1 - mask_3d * 0.2)
            
            return np.clip(result, 0, 255).astype(np.uint8)
        except:
            return source
    
    def poisson_blending_advanced(self, source: np.ndarray, target: np.ndarray,
                                 mask: np.ndarray) -> np.ndarray:
        """Poisson blending avanzado usando gradientes."""
        if not SCIPY_AVAILABLE:
            return self.advanced_multi_scale_blending(source, target, mask)
        
        try:
            # Convertir a escala de grises para cálculo
            source_gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY).astype(np.float32)
            target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY).astype(np.float32)
            
            # Calcular gradientes mejorados
            grad_x_source = cv2.Sobel(source_gray, cv2.CV_32F, 1, 0, ksize=5)
            grad_y_source = cv2.Sobel(source_gray, cv2.CV_32F, 0, 1, ksize=5)
            
            grad_x_target = cv2.Sobel(target_gray, cv2.CV_32F, 1, 0, ksize=5)
            grad_y_target = cv2.Sobel(target_gray, cv2.CV_32F, 0, 1, ksize=5)
            
            # Mezclar gradientes según máscara con múltiples niveles
            mask_blur_1 = cv2.GaussianBlur(mask, (5, 5), 0)
            mask_blur_2 = cv2.GaussianBlur(mask, (15, 15), 0)
            
            # Mezclar gradientes
            grad_x = (grad_x_source * mask_blur_1 + grad_x_target * (1 - mask_blur_1)) * 0.7
            grad_x += (grad_x_source * mask_blur_2 + grad_x_target * (1 - mask_blur_2)) * 0.3
            
            grad_y = (grad_y_source * mask_blur_1 + grad_y_target * (1 - mask_blur_1)) * 0.7
            grad_y += (grad_y_source * mask_blur_2 + grad_y_target * (1 - mask_blur_2)) * 0.3
            
            # Reconstruir desde gradientes (aproximación mejorada)
            result_gray = target_gray.copy()
            result_gray[mask > 0.5] = source_gray[mask > 0.5]
            
            # Aplicar corrección de gradientes mejorada
            correction = (grad_x + grad_y) * 0.15
            result_gray = result_gray + correction * mask_blur_1
            
            # Convertir de vuelta a BGR
            result = cv2.cvtColor(np.clip(result_gray, 0, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
            
            # Mezclar con colores originales preservando saturación
            mask_3d = np.stack([mask] * 3, axis=2)
            source_lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB)
            result_lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
            
            # Preservar canales de color del source
            result_lab[:, :, 1] = source_lab[:, :, 1] * mask_3d[:, :, 0] + result_lab[:, :, 1] * (1 - mask_3d[:, :, 0] * 0.3)
            result_lab[:, :, 2] = source_lab[:, :, 2] * mask_3d[:, :, 0] + result_lab[:, :, 2] * (1 - mask_3d[:, :, 0] * 0.3)
            
            result = cv2.cvtColor(np.clip(result_lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
            
            return result
        except:
            return self.advanced_multi_scale_blending(source, target, mask)
    
    def advanced_multi_scale_blending(self, source: np.ndarray, target: np.ndarray,
                                     mask: np.ndarray) -> np.ndarray:
        """Blending multi-escala ultra avanzado para transición perfecta."""
        source_f = source.astype(np.float32)
        target_f = target.astype(np.float32)
        
        # Crear múltiples niveles de máscara (más niveles)
        masks = [
            mask,  # Nivel 1: Original
            cv2.GaussianBlur(mask, (21, 21), 0),  # Nivel 2
            cv2.GaussianBlur(mask, (31, 31), 0),  # Nivel 3
            cv2.GaussianBlur(mask, (51, 51), 0),  # Nivel 4
            cv2.GaussianBlur(mask, (81, 81), 0),  # Nivel 5
            cv2.GaussianBlur(mask, (121, 121), 0),  # Nivel 6
        ]
        
        # Blending en cada nivel
        blended_levels = []
        for m in masks:
            m_3d = np.stack([m] * 3, axis=2)
            blended = source_f * m_3d + target_f * (1 - m_3d)
            blended_levels.append(blended)
        
        # Combinar niveles con pesos optimizados
        final = (blended_levels[0] * 0.25 + 
                blended_levels[1] * 0.20 + 
                blended_levels[2] * 0.18 + 
                blended_levels[3] * 0.15 +
                blended_levels[4] * 0.12 +
                blended_levels[5] * 0.10)
        
        # Preservar detalles finos con múltiples escalas
        source_details_1 = source_f - cv2.GaussianBlur(source_f, (3, 3), 0)
        source_details_2 = source_f - cv2.GaussianBlur(source_f, (5, 5), 0)
        
        detail_mask_1 = cv2.GaussianBlur(mask, (7, 7), 0)
        detail_mask_2 = cv2.GaussianBlur(mask, (15, 15), 0)
        
        detail_mask_1_3d = np.stack([detail_mask_1] * 3, axis=2)
        detail_mask_2_3d = np.stack([detail_mask_2] * 3, axis=2)
        
        final = final + source_details_1 * detail_mask_1_3d * 0.15
        final = final + source_details_2 * detail_mask_2_3d * 0.10
        
        # Preservar textura del target en área de transición
        target_texture = target_f - cv2.GaussianBlur(target_f, (7, 7), 0)
        transition_mask = cv2.GaussianBlur(1 - mask, (51, 51), 0) * 0.2
        transition_mask_3d = np.stack([transition_mask] * 3, axis=2)
        
        final = final + target_texture * transition_mask_3d
        
        return np.clip(final, 0, 255).astype(np.uint8)
    
    def super_resolution_enhancement(self, image: np.ndarray, scale: float = 1.2) -> np.ndarray:
        """Mejora de resolución usando técnicas avanzadas."""
        if scale <= 1.0:
            return image
        
        h, w = image.shape[:2]
        new_h, new_w = int(h * scale), int(w * scale)
        
        # Redimensionar con interpolación de alta calidad
        upscaled = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        # Aplicar sharpening adaptativo
        gray = cv2.cvtColor(upscaled, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_mask = np.abs(laplacian)
        texture_mask = cv2.GaussianBlur(texture_mask, (5, 5), 0)
        if texture_mask.max() > 0:
            texture_mask = np.clip(texture_mask / texture_mask.max(), 0, 1)
        else:
            texture_mask = np.zeros_like(texture_mask)
        texture_mask_3d = np.stack([texture_mask] * 3, axis=2)
        
        # Sharpening solo en áreas con textura
        kernel = np.array([[-0.2, -0.5, -0.2],
                          [-0.5,  3.4, -0.5],
                          [-0.2, -0.5, -0.2]])
        sharpened = cv2.filter2D(upscaled, -1, kernel)
        
        upscaled_f = upscaled.astype(np.float32)
        sharpened_f = sharpened.astype(np.float32)
        
        upscaled = (upscaled_f * (1 - texture_mask_3d * 0.15) + 
                   sharpened_f * (texture_mask_3d * 0.15))
        
        # Redimensionar de vuelta al tamaño original
        result = cv2.resize(np.clip(upscaled, 0, 255).astype(np.uint8), 
                           (w, h), interpolation=cv2.INTER_LANCZOS4)
        
        return result
    
    def enhance_facial_features(self, image: np.ndarray, landmarks: np.ndarray = None) -> np.ndarray:
        """Mejora de características faciales específicas (ojos, boca, etc.)."""
        if landmarks is None or len(landmarks) < 5:
            return image
        
        try:
            # Crear máscara de atención
            attention_mask = self.create_attention_mask(image, landmarks)
            
            # Aplicar sharpening selectivo en regiones de alta atención
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            detail_mask = np.abs(laplacian)
            detail_mask = cv2.GaussianBlur(detail_mask, (5, 5), 0)
            if detail_mask.max() > 0:
                detail_mask = np.clip(detail_mask / detail_mask.max(), 0, 1)
            else:
                detail_mask = np.zeros_like(detail_mask)
            
            # Combinar máscaras de atención y detalles
            combined_mask = attention_mask * detail_mask
            combined_mask_3d = np.stack([combined_mask] * 3, axis=2)
            
            # Sharpening adaptativo en regiones importantes
            kernel = np.array([[-0.2, -0.5, -0.2],
                              [-0.5,  3.4, -0.5],
                              [-0.2, -0.5, -0.2]])
            sharpened = cv2.filter2D(image, -1, kernel)
            
            image_f = image.astype(np.float32)
            sharpened_f = sharpened.astype(np.float32)
            
            result = image_f * (1 - combined_mask_3d * 0.25) + sharpened_f * (combined_mask_3d * 0.25)
            return np.clip(result, 0, 255).astype(np.uint8)
            
        except:
            return image
    
    def advanced_post_processing(self, image: np.ndarray, target: np.ndarray,
                                mask: np.ndarray) -> np.ndarray:
        """Post-procesamiento ultra avanzado para máxima calidad."""
        # Preservar detalles finos en múltiples escalas antes de procesar
        image_original = image.copy()
        
        details_fine = image.astype(np.float32) - cv2.GaussianBlur(image, (3, 3), 0).astype(np.float32)
        details_medium = image.astype(np.float32) - cv2.GaussianBlur(image, (5, 5), 0).astype(np.float32)
        details_coarse = image.astype(np.float32) - cv2.GaussianBlur(image, (7, 7), 0).astype(np.float32)
        
        # Reducción de ruido preservando detalles (múltiples pasos)
        image = cv2.bilateralFilter(image, 9, 70, 70)
        image = cv2.bilateralFilter(image, 7, 50, 50)
        image = cv2.bilateralFilter(image, 5, 35, 35)
        
        # Restaurar detalles en múltiples escalas
        image = image.astype(np.float32) + details_fine * 0.6 + details_medium * 0.3 + details_coarse * 0.1
        image = np.clip(image, 0, 255).astype(np.uint8)
        
        # Aplicar super-resolución sutil si la imagen es pequeña
        h, w = image.shape[:2]
        if h < 300 or w < 300:
            image = self.super_resolution_enhancement(image, scale=1.1)
        
        # Mejora de contraste adaptativa mejorada
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # CLAHE optimizado
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Mejora de saturación adaptativa con preservación de tonos de piel
        a_f = a.astype(np.float32)
        b_f = b.astype(np.float32)
        
        # Detectar tonos de piel
        skin_tones = ((a_f > 120) & (a_f < 150) & (b_f > 130) & (b_f < 170))
        
        # Aumentar saturación más en áreas no-piel
        a = np.where(skin_tones,
                    np.clip(a_f * 1.01, 0, 255),  # Muy sutil en piel
                    np.clip(a_f * 1.04, 0, 255)).astype(np.uint8)
        b = np.where(skin_tones,
                    np.clip(b_f * 1.01, 0, 255),  # Muy sutil en piel
                    np.clip(b_f * 1.04, 0, 255)).astype(np.uint8)
        
        image = cv2.merge([l, a, b])
        image = cv2.cvtColor(image, cv2.COLOR_LAB2BGR)
        
        # Sharpening adaptativo mejorado
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detectar textura con múltiples métodos
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        texture_mask = np.abs(laplacian) + np.abs(sobel_x) + np.abs(sobel_y)
        texture_mask = cv2.GaussianBlur(texture_mask, (5, 5), 0)
        if texture_mask.max() > 0:
            texture_mask = np.clip(texture_mask / texture_mask.max(), 0, 1)
        else:
            texture_mask = np.zeros_like(texture_mask)
        texture_mask_3d = np.stack([texture_mask] * 3, axis=2)
        
        # Aplicar sharpening con múltiples kernels
        kernel_strong = np.array([[-0.3, -0.8, -0.3],
                                  [-0.8,  7.5, -0.8],
                                  [-0.3, -0.8, -0.3]]) / 2.0
        kernel_soft = np.array([[0, -0.2, 0],
                                 [-0.2, 1.8, -0.2],
                                 [0, -0.2, 0]])
        
        sharpened_strong = cv2.filter2D(image, -1, kernel_strong)
        sharpened_soft = cv2.filter2D(image, -1, kernel_soft)
        
        image_f = image.astype(np.float32)
        sharp_strong_f = sharpened_strong.astype(np.float32)
        sharp_soft_f = sharpened_soft.astype(np.float32)
        
        # Mezclar según textura
        image = (image_f * (1 - texture_mask_3d * 0.12) + 
                sharp_strong_f * (texture_mask_3d * 0.08) + 
                sharp_soft_f * (texture_mask_3d * 0.04))
        image = np.clip(image, 0, 255).astype(np.uint8)
        
        # Preservar coherencia de textura con target
        if SCIPY_AVAILABLE:
            try:
                target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY).astype(np.float32)
                image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32)
                
                # Extraer textura del target
                target_texture = target_gray - ndimage.gaussian_filter(target_gray, sigma=3)
                image_texture = image_gray - ndimage.gaussian_filter(image_gray, sigma=3)
                
                # Mezclar texturas en área de transición
                transition_mask = cv2.GaussianBlur(1 - mask, (71, 71), 0) * 0.25
                
                final_texture = image_texture * (1 - transition_mask) + target_texture * transition_mask
                image_gray_final = ndimage.gaussian_filter(image_gray, sigma=3) + final_texture
                
                # Aplicar de vuelta
                image_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
                image_lab[:, :, 0] = np.clip(image_gray_final, 0, 255).astype(np.uint8)
                image = cv2.cvtColor(image_lab, cv2.COLOR_LAB2BGR)
            except:
                pass
        
        # Reducción final de ruido muy sutil
        image = cv2.bilateralFilter(image, 3, 20, 20)
        
        return image


def batch_professional_swap():
    """Procesa imágenes usando versión profesional."""
    from pathlib import Path
    import random
    
    print("=" * 70)
    print("FACE SWAP PROFESIONAL: BUNNY -> 69CAYLIN")
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
        print("Error: No se encontraron imagenes suficientes")
        return
    
    print(f"Encontradas {len(all_bunny_faces)} caras de bunny")
    print(f"Encontradas {len(caylin_images)} imagenes de 69caylin")
    
    # Crear carpeta de salida
    output_dir = Path("face_swap_results_bunny_to_69caylin")
    output_dir.mkdir(exist_ok=True)
    
    # Inicializar face swap profesional
    print("\nInicializando face swap profesional...")
    face_swapper = ProfessionalFaceSwap()
    
    print(f"\nProcesando {len(caylin_images)} imagenes...")
    print("-" * 70)
    
    successful = 0
    failed = 0
    
    for idx, caylin_img_path in enumerate(caylin_images, 1):
        try:
            bunny_face_path = random.choice(all_bunny_faces)
            
            bunny_img = cv2.imread(str(bunny_face_path))
            caylin_img = cv2.imread(str(caylin_img_path))
            
            if bunny_img is None or caylin_img is None:
                failed += 1
                continue
            
            # Face swap profesional
            result = face_swapper.swap_faces_professional(bunny_img, caylin_img)
            
            # Guardar con máxima calidad ultra mejorada
            output_filename = f"bunny_face_on_{caylin_img_path.stem}.jpg"
            output_path = output_dir / output_filename
            
            # Aplicar mejora final antes de guardar
            result = self.final_save_enhancement(result)
            
            cv2.imwrite(str(output_path), result,
                       [cv2.IMWRITE_JPEG_QUALITY, 100,
                        cv2.IMWRITE_JPEG_OPTIMIZE, 1])
            
            successful += 1
            if idx % 50 == 0:
                print(f"[{idx}/{len(caylin_images)}] Procesadas...")
            
        except Exception as e:
            print(f"Error en {caylin_img_path.name}: {e}")
            failed += 1
            continue
    
    print("\n" + "=" * 70)
    print("PROCESO COMPLETADO")
    print("=" * 70)
    print(f"Imagenes procesadas: {successful}")
    print(f"Errores: {failed}")
    print(f"Resultados en: {output_dir.absolute()}")


if __name__ == "__main__":
    batch_professional_swap()








