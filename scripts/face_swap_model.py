"""
Modelo de Face Swap - Intercambio de Caras
===========================================
Modelo simple y entrenable para hacer face swap en cualquier imagen.

Requisitos:
    pip install opencv-python face-recognition dlib torch torchvision pillow numpy
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import face_recognition
from pathlib import Path
from typing import Tuple, Optional, List
import os


class FaceSwapModel(nn.Module):
    """
    Modelo CNN simple para face swap.
    Toma dos caras alineadas y genera una cara fusionada.
    """
    
    def __init__(self, input_size=256, latent_dim=512):
        super(FaceSwapModel, self).__init__()
        
        # Encoder para cara fuente
        self.encoder_source = nn.Sequential(
            nn.Conv2d(3, 64, 4, 2, 1),  # 256 -> 128
            nn.LeakyReLU(0.2),
            nn.Conv2d(64, 128, 4, 2, 1),  # 128 -> 64
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2),
            nn.Conv2d(128, 256, 4, 2, 1),  # 64 -> 32
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2),
            nn.Conv2d(256, 512, 4, 2, 1),  # 32 -> 16
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2),
            nn.Conv2d(512, latent_dim, 4, 2, 1),  # 16 -> 8
        )
        
        # Encoder para cara destino
        self.encoder_target = nn.Sequential(
            nn.Conv2d(3, 64, 4, 2, 1),
            nn.LeakyReLU(0.2),
            nn.Conv2d(64, 128, 4, 2, 1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2),
            nn.Conv2d(128, 256, 4, 2, 1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2),
            nn.Conv2d(256, 512, 4, 2, 1),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2),
            nn.Conv2d(512, latent_dim, 4, 2, 1),
        )
        
        # Fusion layer
        self.fusion = nn.Sequential(
            nn.Linear(latent_dim * 2, latent_dim),
            nn.ReLU(),
            nn.Linear(latent_dim, latent_dim),
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(latent_dim, 512, 4, 2, 1),  # 8 -> 16
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.ConvTranspose2d(512, 256, 4, 2, 1),  # 16 -> 32
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.ConvTranspose2d(256, 128, 4, 2, 1),  # 32 -> 64
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.ConvTranspose2d(128, 64, 4, 2, 1),  # 64 -> 128
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 3, 4, 2, 1),  # 128 -> 256
            nn.Tanh()
        )
        
    def forward(self, source_face, target_face):
        # Encoder
        source_latent = self.encoder_source(source_face)
        target_latent = self.encoder_target(target_face)
        
        # Flatten para fusion
        batch_size = source_latent.size(0)
        source_flat = source_latent.view(batch_size, -1)
        target_flat = target_latent.view(batch_size, -1)
        
        # Fusion
        combined = torch.cat([source_flat, target_flat], dim=1)
        fused = self.fusion(combined)
        
        # Reshape para decoder
        fused = fused.view(batch_size, -1, 8, 8)
        
        # Decoder
        output = self.decoder(fused)
        
        # Normalize to [0, 1]
        output = (output + 1) / 2
        
        return output


class FaceDetector:
    """Utilidad para detectar y alinear caras en imágenes."""
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def detect_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detecta una cara en la imagen.
        Returns: (x, y, w, h) o None
        """
        # Usar face_recognition para mejor precisión
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image, model='hog')
        
        if len(face_locations) > 0:
            top, right, bottom, left = face_locations[0]
            return (left, top, right - left, bottom - top)
        
        # Fallback a OpenCV
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        if len(faces) > 0:
            return tuple(faces[0])
        
        return None
    
    def extract_face(self, image: np.ndarray, size: int = 256) -> Optional[np.ndarray]:
        """
        Extrae y alinea una cara de la imagen.
        """
        face_location = self.detect_face(image)
        if face_location is None:
            return None
        
        x, y, w, h = face_location
        
        # Expandir región para incluir más contexto
        margin = 0.3
        x_expanded = max(0, int(x - w * margin))
        y_expanded = max(0, int(y - h * margin))
        w_expanded = min(image.shape[1] - x_expanded, int(w * (1 + 2 * margin)))
        h_expanded = min(image.shape[0] - y_expanded, int(h * (1 + 2 * margin)))
        
        # Extraer región de la cara
        face_region = image[y_expanded:y_expanded+h_expanded, 
                           x_expanded:x_expanded+w_expanded]
        
        # Redimensionar a tamaño estándar
        face_resized = cv2.resize(face_region, (size, size))
        
        return face_resized
    
    def align_face(self, image: np.ndarray, size: int = 256) -> Optional[np.ndarray]:
        """
        Alinea la cara usando landmarks faciales.
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_landmarks = face_recognition.face_landmarks(rgb_image)
        
        if len(face_landmarks) == 0:
            return self.extract_face(image, size)
        
        # Obtener puntos clave
        landmarks = face_landmarks[0]
        
        # Puntos de referencia para alineación
        left_eye = np.mean(landmarks['left_eye'], axis=0)
        right_eye = np.mean(landmarks['right_eye'], axis=0)
        nose = np.mean(landmarks['nose_tip'], axis=0)
        
        # Calcular ángulo de rotación
        eye_vector = right_eye - left_eye
        angle = np.arctan2(eye_vector[1], eye_vector[0]) * 180 / np.pi
        
        # Rotar imagen
        center = (image.shape[1] // 2, image.shape[0] // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, 
                                 (image.shape[1], image.shape[0]))
        
        # Extraer cara alineada
        return self.extract_face(rotated, size)


class FaceSwapDataset(Dataset):
    """Dataset para entrenar el modelo de face swap."""
    
    def __init__(self, image_dir: str, size: int = 256):
        self.image_dir = Path(image_dir)
        self.size = size
        self.detector = FaceDetector()
        
        # Obtener todas las imágenes
        self.images = list(self.image_dir.glob("*.jpg")) + \
                     list(self.image_dir.glob("*.png")) + \
                     list(self.image_dir.glob("*.jpeg"))
        
        if len(self.images) < 2:
            raise ValueError("Se necesitan al menos 2 imágenes para entrenar")
    
    def __len__(self):
        return len(self.images) * 10  # Aumentar dataset con pares aleatorios
    
    def __getitem__(self, idx):
        # Seleccionar dos imágenes aleatorias
        idx1 = np.random.randint(0, len(self.images))
        idx2 = np.random.randint(0, len(self.images))
        
        while idx1 == idx2:
            idx2 = np.random.randint(0, len(self.images))
        
        # Cargar imágenes
        img1 = cv2.imread(str(self.images[idx1]))
        img2 = cv2.imread(str(self.images[idx2]))
        
        # Extraer caras
        face1 = self.detector.align_face(img1, self.size)
        face2 = self.detector.align_face(img2, self.size)
        
        # Si no se detecta cara, usar imagen completa redimensionada
        if face1 is None:
            face1 = cv2.resize(img1, (self.size, self.size))
        if face2 is None:
            face2 = cv2.resize(img2, (self.size, self.size))
        
        # Convertir a tensor y normalizar
        face1 = cv2.cvtColor(face1, cv2.COLOR_BGR2RGB)
        face2 = cv2.cvtColor(face2, cv2.COLOR_BGR2RGB)
        
        face1 = torch.from_numpy(face1).float().permute(2, 0, 1) / 255.0
        face2 = torch.from_numpy(face2).float().permute(2, 0, 1) / 255.0
        
        # Target: cara fuente (para entrenamiento)
        target = face1.clone()
        
        return face1, face2, target


class FaceSwapPipeline:
    """Pipeline completo para hacer face swap."""
    
    def __init__(self, model_path: Optional[str] = None, device: str = 'cpu'):
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.model = FaceSwapModel().to(self.device)
        self.detector = FaceDetector()
        
        if model_path and os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.eval()
            print(f"Modelo cargado desde {model_path}")
    
    def swap_faces(self, 
                   source_image: np.ndarray, 
                   target_image: np.ndarray,
                   use_blending: bool = True) -> np.ndarray:
        """
        Intercambia la cara de source_image a target_image.
        
        Args:
            source_image: Imagen con la cara fuente
            target_image: Imagen donde se colocará la cara
            use_blending: Si True, usa blending suave en los bordes
        
        Returns:
            Imagen con la cara intercambiada
        """
        # Extraer caras
        source_face = self.detector.align_face(source_image, 256)
        target_face = self.detector.align_face(target_image, 256)
        
        if source_face is None or target_face is None:
            print("No se detectó cara en una o ambas imágenes")
            return target_image
        
        # Preparar para el modelo
        source_tensor = torch.from_numpy(
            cv2.cvtColor(source_face, cv2.COLOR_BGR2RGB)
        ).float().permute(2, 0, 1).unsqueeze(0) / 255.0
        
        target_tensor = torch.from_numpy(
            cv2.cvtColor(target_face, cv2.COLOR_BGR2RGB)
        ).float().permute(2, 0, 1).unsqueeze(0) / 255.0
        
        source_tensor = source_tensor.to(self.device)
        target_tensor = target_tensor.to(self.device)
        
        # Generar cara intercambiada
        with torch.no_grad():
            swapped_face = self.model(source_tensor, target_tensor)
        
        # Convertir a numpy
        swapped_face = swapped_face.squeeze(0).cpu().permute(1, 2, 0).numpy()
        swapped_face = (swapped_face * 255).astype(np.uint8)
        swapped_face = cv2.cvtColor(swapped_face, cv2.COLOR_RGB2BGR)
        
        # Encontrar posición de la cara en la imagen destino
        face_location = self.detector.detect_face(target_image)
        if face_location is None:
            return target_image
        
        x, y, w, h = face_location
        
        # Expandir región
        margin = 0.3
        x_expanded = max(0, int(x - w * margin))
        y_expanded = max(0, int(y - h * margin))
        w_expanded = min(target_image.shape[1] - x_expanded, int(w * (1 + 2 * margin)))
        h_expanded = min(target_image.shape[0] - y_expanded, int(h * (1 + 2 * margin)))
        
        # Redimensionar cara intercambiada al tamaño de la región
        swapped_resized = cv2.resize(swapped_face, (w_expanded, h_expanded))
        
        # Crear máscara para blending suave
        if use_blending:
            mask = np.ones((h_expanded, w_expanded), dtype=np.float32)
            mask = cv2.GaussianBlur(mask, (21, 21), 0)
            mask = np.stack([mask] * 3, axis=2)
        else:
            mask = np.ones((h_expanded, w_expanded, 3), dtype=np.float32)
        
        # Aplicar blending
        result = target_image.copy()
        region = result[y_expanded:y_expanded+h_expanded, 
                       x_expanded:x_expanded+w_expanded]
        
        blended = (swapped_resized * mask + region * (1 - mask)).astype(np.uint8)
        result[y_expanded:y_expanded+h_expanded, 
               x_expanded:x_expanded+w_expanded] = blended
        
        return result
    
    def save_model(self, path: str):
        """Guarda el modelo entrenado."""
        torch.save(self.model.state_dict(), path)
        print(f"Modelo guardado en {path}")


def train_model(image_dir: str, 
                epochs: int = 50,
                batch_size: int = 4,
                lr: float = 0.0002,
                save_path: str = "face_swap_model.pth"):
    """
    Entrena el modelo de face swap.
    
    Args:
        image_dir: Directorio con imágenes para entrenar
        epochs: Número de épocas
        batch_size: Tamaño del batch
        lr: Learning rate
        save_path: Ruta donde guardar el modelo
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Usando dispositivo: {device}")
    
    # Crear dataset y dataloader
    dataset = FaceSwapDataset(image_dir)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    
    # Crear modelo
    model = FaceSwapModel().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, betas=(0.5, 0.999))
    criterion = nn.MSELoss()
    
    # Entrenar
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for batch_idx, (source, target, ground_truth) in enumerate(dataloader):
            source = source.to(device)
            target = target.to(device)
            ground_truth = ground_truth.to(device)
            
            # Forward pass
            output = model(source, target)
            
            # Loss
            loss = criterion(output, ground_truth)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
            if batch_idx % 10 == 0:
                print(f"Epoch {epoch+1}/{epochs}, Batch {batch_idx}, Loss: {loss.item():.4f}")
        
        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1}/{epochs} completado. Loss promedio: {avg_loss:.4f}")
        
        # Guardar checkpoint
        if (epoch + 1) % 10 == 0:
            torch.save(model.state_dict(), f"checkpoint_epoch_{epoch+1}.pth")
    
    # Guardar modelo final
    torch.save(model.state_dict(), save_path)
    print(f"Entrenamiento completado. Modelo guardado en {save_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Face Swap Model")
    parser.add_argument("--mode", choices=["train", "swap"], required=True,
                       help="Modo: train o swap")
    parser.add_argument("--image-dir", type=str,
                       help="Directorio con imágenes (para entrenar)")
    parser.add_argument("--source", type=str,
                       help="Imagen fuente (para swap)")
    parser.add_argument("--target", type=str,
                       help="Imagen destino (para swap)")
    parser.add_argument("--output", type=str, default="output.jpg",
                       help="Imagen de salida (para swap)")
    parser.add_argument("--model", type=str, default="face_swap_model.pth",
                       help="Ruta del modelo")
    parser.add_argument("--epochs", type=int, default=50,
                       help="Número de épocas (para entrenar)")
    parser.add_argument("--batch-size", type=int, default=4,
                       help="Tamaño del batch (para entrenar)")
    
    args = parser.parse_args()
    
    if args.mode == "train":
        if not args.image_dir:
            print("Error: --image-dir es requerido para entrenar")
            exit(1)
        train_model(args.image_dir, args.epochs, args.batch_size, save_path=args.model)
    
    elif args.mode == "swap":
        if not args.source or not args.target:
            print("Error: --source y --target son requeridos para swap")
            exit(1)
        
        pipeline = FaceSwapPipeline(model_path=args.model)
        source_img = cv2.imread(args.source)
        target_img = cv2.imread(args.target)
        
        result = pipeline.swap_faces(source_img, target_img)
        cv2.imwrite(args.output, result)
        print(f"Resultado guardado en {args.output}")








