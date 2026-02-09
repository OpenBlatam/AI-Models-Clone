"""
Simple Face Swap Pipeline
==========================
Pipeline simple para face swap.
"""

import os
import cv2
import numpy as np
import torch
from typing import Optional

from .model import SimpleFaceSwapModel
from .detector import SimpleFaceDetector


class SimpleFaceSwapPipeline:
    """Pipeline simple para face swap."""
    
    def __init__(self, model_path: Optional[str] = None, device: str = 'cpu'):
        """
        Inicializar pipeline.
        
        Args:
            model_path: Ruta al modelo entrenado (opcional)
            device: Dispositivo ('cpu' o 'cuda')
        """
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.model = SimpleFaceSwapModel().to(self.device)
        self.detector = SimpleFaceDetector()
        
        if model_path and os.path.exists(model_path):
            try:
                checkpoint = torch.load(model_path, map_location=self.device)
                if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                    self.model.load_state_dict(checkpoint['model_state_dict'])
                else:
                    self.model.load_state_dict(checkpoint)
                self.model.eval()
                print(f"✓ Modelo cargado desde {model_path}")
            except Exception as e:
                print(f"⚠ No se pudo cargar el modelo: {e}")
                print("  Usando modelo sin entrenar (resultados básicos)")
        else:
            print("⚠ No se encontró modelo entrenado")
            print("  Usando detección básica sin modelo")
    
    def color_match(self, source: np.ndarray, target: np.ndarray) -> np.ndarray:
        """
        Ajusta el color de source para que coincida con target.
        
        Args:
            source: Imagen fuente
            target: Imagen objetivo
        
        Returns:
            Imagen con color corregido
        """
        # Convertir a LAB para mejor ajuste de color
        source_lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype(np.float32)
        target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        # Calcular medias y desviaciones estándar
        source_mean = np.mean(source_lab, axis=(0, 1))
        source_std = np.std(source_lab, axis=(0, 1)) + 1e-6
        
        target_mean = np.mean(target_lab, axis=(0, 1))
        target_std = np.std(target_lab, axis=(0, 1)) + 1e-6
        
        # Aplicar transformación de color
        corrected_lab = (source_lab - source_mean) * (target_std / source_std) + target_mean
        corrected_lab = np.clip(corrected_lab, 0, 255)
        
        # Convertir de vuelta a BGR
        corrected = cv2.cvtColor(corrected_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
        return corrected
    
    def swap_faces(
        self,
        source_image: np.ndarray,
        target_image: np.ndarray
    ) -> np.ndarray:
        """
        Intercambia la cara de source a target con alta calidad.
        
        Args:
            source_image: Imagen fuente
            target_image: Imagen objetivo
        
        Returns:
            Imagen resultante con cara intercambiada
        """
        # Extraer caras
        source_face = self.detector.extract_face(source_image, 256)
        target_face = self.detector.extract_face(target_image, 256)
        
        if source_face is None or target_face is None:
            return target_image
        
        # Ajustar color de la cara fuente para que coincida con el entorno
        source_face = self.color_match(source_face, target_face)
        
        # Si tenemos modelo entrenado, usarlo
        swapped_face = None
        try:
            # Preparar tensores
            source_tensor = torch.from_numpy(
                cv2.cvtColor(source_face, cv2.COLOR_BGR2RGB)
            ).float().permute(2, 0, 1).unsqueeze(0) / 255.0
            
            target_tensor = torch.from_numpy(
                cv2.cvtColor(target_face, cv2.COLOR_BGR2RGB)
            ).float().permute(2, 0, 1).unsqueeze(0) / 255.0
            
            source_tensor = source_tensor.to(self.device)
            target_tensor = target_tensor.to(self.device)
            
            # Generar cara intercambiada con modelo
            with torch.no_grad():
                self.model.eval()
                swapped_face_tensor = self.model(source_tensor, target_tensor)
            
            # Convertir a numpy
            swapped_face = swapped_face_tensor.squeeze(0).cpu().permute(1, 2, 0).numpy()
            swapped_face = (swapped_face * 255).astype(np.uint8)
            swapped_face = cv2.cvtColor(swapped_face, cv2.COLOR_RGB2BGR)
            
            # Mezclar con cara original para mejor resultado
            alpha = 0.75  # Peso del modelo aumentado
            swapped_face = cv2.addWeighted(swapped_face, alpha, source_face, 1-alpha, 0)
            
            # Mejora adicional de calidad
            swapped_face = cv2.bilateralFilter(swapped_face, 3, 30, 30)
        except Exception as e:
            swapped_face = source_face
        
        if swapped_face is None:
            # Sin modelo, usar cara fuente con mejor procesamiento
            swapped_face = source_face
        
        # Encontrar posición en imagen destino
        face_location = self.detector.detect_face(target_image)
        if face_location is None:
            return target_image
        
        x, y, w, h = face_location
        
        # Expandir región con más margen
        margin = 0.3
        x_expanded = max(0, int(x - w * margin))
        y_expanded = max(0, int(y - h * margin))
        w_expanded = min(target_image.shape[1] - x_expanded, int(w * (1 + 2 * margin)))
        h_expanded = min(target_image.shape[0] - y_expanded, int(h * (1 + 2 * margin)))
        
        # Redimensionar cara con interpolación de alta calidad
        swapped_resized = cv2.resize(
            swapped_face, (w_expanded, h_expanded),
            interpolation=cv2.INTER_LANCZOS4
        )
        
        # Crear máscara elíptica suave para mejor blending
        mask = np.zeros((h_expanded, w_expanded), dtype=np.float32)
        center_x, center_y = w_expanded // 2, h_expanded // 2
        radius_x, radius_y = int(w_expanded * 0.45), int(h_expanded * 0.5)
        
        y_coords, x_coords = np.ogrid[:h_expanded, :w_expanded]
        ellipse = ((x_coords - center_x) / radius_x) ** 2 + ((y_coords - center_y) / radius_y) ** 2
        mask[ellipse <= 1] = 1.0
        
        # Suavizar máscara múltiples veces
        mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=20, sigmaY=20)
        mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=15, sigmaY=15)
        mask = np.clip(mask, 0, 1)
        mask_3d = np.stack([mask] * 3, axis=2)
        
        # Aplicar blending mejorado
        result = target_image.copy()
        region = result[y_expanded:y_expanded+h_expanded,
                       x_expanded:x_expanded+w_expanded]
        
        # Blending con múltiples pasos
        blended = (swapped_resized * mask_3d + region * (1 - mask_3d)).astype(np.uint8)
        
        # Aplicar seamless cloning si está disponible
        try:
            mask_uint8 = (mask * 255).astype(np.uint8)
            center = (w_expanded // 2, h_expanded // 2)
            blended = cv2.seamlessClone(swapped_resized, region, mask_uint8, center, cv2.NORMAL_CLONE)
        except:
            pass
        
        result[y_expanded:y_expanded+h_expanded,
               x_expanded:x_expanded+w_expanded] = blended
        
        return result






