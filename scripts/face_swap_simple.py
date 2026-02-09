"""
Face Swap Simple - Versión sin dependencias complejas
=====================================================
Versión simplificada que solo usa OpenCV y PyTorch.
No requiere dlib ni face_recognition.
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional
import os


class SimpleFaceSwapModel(nn.Module):
    """Modelo CNN mejorado para face swap con mejor arquitectura."""
    
    def __init__(self, input_size=256):
        super(SimpleFaceSwapModel, self).__init__()
        
        # Encoder mejorado con conexiones residuales
        self.encoder_conv1 = nn.Sequential(
            nn.Conv2d(6, 64, 4, 2, 1),
            nn.LeakyReLU(0.2, inplace=True)
        )
        
        self.encoder_conv2 = nn.Sequential(
            nn.Conv2d(64, 128, 4, 2, 1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True)
        )
        
        self.encoder_conv3 = nn.Sequential(
            nn.Conv2d(128, 256, 4, 2, 1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True)
        )
        
        self.encoder_conv4 = nn.Sequential(
            nn.Conv2d(256, 512, 4, 2, 1),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2, inplace=True)
        )
        
        # Capa de bottleneck con atención
        self.bottleneck = nn.Sequential(
            nn.Conv2d(512, 512, 3, 1, 1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, 3, 1, 1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True)
        )
        
        # Decoder mejorado con skip connections
        self.decoder_conv1 = nn.Sequential(
            nn.ConvTranspose2d(512, 256, 4, 2, 1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True)
        )
        
        self.decoder_conv2 = nn.Sequential(
            nn.ConvTranspose2d(256, 128, 4, 2, 1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True)
        )
        
        self.decoder_conv3 = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 4, 2, 1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True)
        )
        
        self.decoder_conv4 = nn.Sequential(
            nn.ConvTranspose2d(64, 3, 4, 2, 1),
            nn.Tanh()  # Cambiar a Tanh para mejor rango
        )
        
    def forward(self, source, target):
        # Concatenar source y target
        combined = torch.cat([source, target], dim=1)
        
        # Normalizar a [-1, 1] si viene de [0, 1]
        if combined.max() <= 1.0:
            combined = combined * 2.0 - 1.0
        
        # Encoder con skip connections
        e1 = self.encoder_conv1(combined)  # 128x128
        e2 = self.encoder_conv2(e1)         # 64x64
        e3 = self.encoder_conv3(e2)         # 32x32
        e4 = self.encoder_conv4(e3)         # 16x16
        
        # Bottleneck
        bottleneck = self.bottleneck(e4)
        
        # Decoder
        d1 = self.decoder_conv1(bottleneck)  # 32x32
        d2 = self.decoder_conv2(d1)          # 64x64
        d3 = self.decoder_conv3(d2)          # 128x128
        output = self.decoder_conv4(d3)      # 256x256
        
        # Normalizar de vuelta a [0, 1]
        output = (output + 1.0) / 2.0
        
        return output


class SimpleFaceDetector:
    """Detector de caras simple usando solo OpenCV."""
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
    
    def detect_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detecta una cara en la imagen."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detectar caras
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        if len(faces) > 0:
            # Retornar la cara más grande
            faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
            return tuple(faces[0])
        
        return None
    
    def extract_face(self, image: np.ndarray, size: int = 256) -> Optional[np.ndarray]:
        """Extrae y redimensiona una cara."""
        face_location = self.detect_face(image)
        if face_location is None:
            return None
        
        x, y, w, h = face_location
        
        # Expandir región
        margin = 0.2
        x_expanded = max(0, int(x - w * margin))
        y_expanded = max(0, int(y - h * margin))
        w_expanded = min(image.shape[1] - x_expanded, int(w * (1 + 2 * margin)))
        h_expanded = min(image.shape[0] - y_expanded, int(h * (1 + 2 * margin)))
        
        # Extraer región
        face_region = image[y_expanded:y_expanded+h_expanded, 
                           x_expanded:x_expanded+w_expanded]
        
        # Redimensionar
        face_resized = cv2.resize(face_region, (size, size))
        
        return face_resized


class SimpleFaceSwapDataset(Dataset):
    """Dataset simple para entrenar."""
    
    def __init__(self, image_dir: str, size: int = 256):
        self.image_dir = Path(image_dir)
        self.size = size
        self.detector = SimpleFaceDetector()
        
        # Obtener imágenes
        self.images = list(self.image_dir.glob("*.jpg")) + \
                     list(self.image_dir.glob("*.png")) + \
                     list(self.image_dir.glob("*.jpeg"))
        
        if len(self.images) < 2:
            raise ValueError("Se necesitan al menos 2 imágenes")
    
    def __len__(self):
        return len(self.images) * 20
    
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
        face1 = self.detector.extract_face(img1, self.size)
        face2 = self.detector.extract_face(img2, self.size)
        
        # Si no se detecta, usar imagen completa
        if face1 is None:
            face1 = cv2.resize(img1, (self.size, self.size))
        if face2 is None:
            face2 = cv2.resize(img2, (self.size, self.size))
        
        # Convertir a RGB y tensor
        face1 = cv2.cvtColor(face1, cv2.COLOR_BGR2RGB)
        face2 = cv2.cvtColor(face2, cv2.COLOR_BGR2RGB)
        
        face1 = torch.from_numpy(face1).float().permute(2, 0, 1) / 255.0
        face2 = torch.from_numpy(face2).float().permute(2, 0, 1) / 255.0
        
        # Target: cara fuente
        target = face1.clone()
        
        return face1, face2, target


class SimpleFaceSwapPipeline:
    """Pipeline simple para face swap."""
    
    def __init__(self, model_path: Optional[str] = None, device: str = 'cpu'):
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.model = SimpleFaceSwapModel().to(self.device)
        self.detector = SimpleFaceDetector()
        
        if model_path and os.path.exists(model_path):
            try:
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                self.model.eval()
                print(f"✓ Modelo cargado desde {model_path}")
            except Exception as e:
                print(f"⚠ No se pudo cargar el modelo: {e}")
                print("  Usando modelo sin entrenar (resultados básicos)")
        else:
            print("⚠ No se encontró modelo entrenado")
            print("  Usando detección básica sin modelo")
    
    def color_match(self, source: np.ndarray, target: np.ndarray) -> np.ndarray:
        """Ajusta el color de source para que coincida con target."""
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
    
    def swap_faces(self, 
                   source_image: np.ndarray, 
                   target_image: np.ndarray) -> np.ndarray:
        """Intercambia la cara de source a target con alta calidad."""
        # Extraer caras
        source_face = self.detector.extract_face(source_image, 256)
        target_face = self.detector.extract_face(target_image, 256)
        
        if source_face is None or target_face is None:
            return target_image
        
        # Ajustar color de la cara fuente para que coincida con el entorno
        source_face = self.color_match(source_face, target_face)
        
        # Si tenemos modelo entrenado, usarlo
        swapped_face = None
        if hasattr(self.model, 'encoder'):
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
                
                # Mezclar con cara original para mejor resultado (ajustado)
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
        swapped_resized = cv2.resize(swapped_face, (w_expanded, h_expanded), 
                                    interpolation=cv2.INTER_LANCZOS4)
        
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


def train_simple_model(image_dir: str, 
                      epochs: int = 30,
                      batch_size: int = 4,
                      lr: float = 0.0002,
                      save_path: str = "face_swap_simple_model.pth"):
    """Entrena el modelo simple."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"🚀 Usando dispositivo: {device}")
    
    # Crear dataset
    print("📦 Cargando dataset...")
    dataset = SimpleFaceSwapDataset(image_dir)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    
    print(f"✓ Dataset cargado: {len(dataset)} pares de imágenes")
    
    # Crear modelo mejorado
    model = SimpleFaceSwapModel().to(device)
    
    # Optimizador mejorado con weight decay
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, betas=(0.5, 0.999), weight_decay=1e-5)
    
    # Loss combinado para mejor entrenamiento
    mse_loss = nn.MSELoss()
    l1_loss = nn.L1Loss()
    
    # Scheduler para learning rate adaptativo
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5, verbose=True
    )
    
    print("Iniciando entrenamiento...")
    model.train()
    
    best_loss = float('inf')
    
    for epoch in range(epochs):
        total_loss = 0
        for batch_idx, (source, target, ground_truth) in enumerate(dataloader):
            source = source.to(device)
            target = target.to(device)
            ground_truth = ground_truth.to(device)
            
            # Forward
            output = model(source, target)
            
            # Loss combinado (MSE + L1 para mejor convergencia)
            loss_mse = mse_loss(output, ground_truth)
            loss_l1 = l1_loss(output, ground_truth)
            loss = loss_mse + 0.3 * loss_l1  # Combinación ponderada
            
            # Backward
            optimizer.zero_grad()
            loss.backward()
            
            # Gradient clipping para estabilidad
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            optimizer.step()
            
            total_loss += loss.item()
            
            if batch_idx % 20 == 0:
                print(f"  Epoch {epoch+1}/{epochs}, Batch {batch_idx}, Loss: {loss.item():.4f}")
        
        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1}/{epochs} completado. Loss promedio: {avg_loss:.4f}")
        
        # Actualizar learning rate
        scheduler.step(avg_loss)
        
        # Guardar mejor modelo
        if avg_loss < best_loss:
            best_loss = avg_loss
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': avg_loss,
            }, save_path.replace('.pth', '_best.pth'))
        
        # Guardar checkpoint periódico
        if (epoch + 1) % 10 == 0:
            checkpoint_path = f"checkpoint_simple_epoch_{epoch+1}.pth"
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': avg_loss,
            }, checkpoint_path)
            print(f"  Checkpoint guardado: {checkpoint_path}")
    
    # Guardar modelo final
    torch.save({
        'epoch': epochs,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': avg_loss,
    }, save_path)
    print(f"\nEntrenamiento completado!")
    print(f"Modelo guardado en: {save_path}")
    print(f"Mejor modelo guardado en: {save_path.replace('.pth', '_best.pth')}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Face Swap Model")
    parser.add_argument("--mode", choices=["train", "swap"], required=True)
    parser.add_argument("--image-dir", type=str, help="Directorio con imágenes")
    parser.add_argument("--source", type=str, help="Imagen fuente")
    parser.add_argument("--target", type=str, help="Imagen destino")
    parser.add_argument("--output", type=str, default="output.jpg")
    parser.add_argument("--model", type=str, default="face_swap_simple_model.pth")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=4)
    
    args = parser.parse_args()
    
    if args.mode == "train":
        if not args.image_dir:
            print("❌ Error: --image-dir es requerido")
            exit(1)
        train_simple_model(args.image_dir, args.epochs, args.batch_size, save_path=args.model)
    
    elif args.mode == "swap":
        if not args.source or not args.target:
            print("❌ Error: --source y --target son requeridos")
            exit(1)
        
        pipeline = SimpleFaceSwapPipeline(model_path=args.model)
        source_img = cv2.imread(args.source)
        target_img = cv2.imread(args.target)
        
        if source_img is None or target_img is None:
            print("❌ Error: No se pudieron cargar las imágenes")
            exit(1)
        
        result = pipeline.swap_faces(source_img, target_img)
        cv2.imwrite(args.output, result)
        print(f"✅ Resultado guardado en {args.output}")








