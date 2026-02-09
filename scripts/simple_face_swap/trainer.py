"""
Simple Face Swap Trainer
=========================
Entrenador para el modelo de face swap.
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from .model import SimpleFaceSwapModel
from .dataset import SimpleFaceSwapDataset


class SimpleFaceSwapTrainer:
    """Entrenador para modelo de face swap."""
    
    def __init__(
        self,
        image_dir: str,
        device: str = 'cpu',
        batch_size: int = 4,
        lr: float = 0.0002
    ):
        """
        Inicializar entrenador.
        
        Args:
            image_dir: Directorio con imágenes
            device: Dispositivo ('cpu' o 'cuda')
            batch_size: Tamaño de batch
            lr: Learning rate
        """
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.batch_size = batch_size
        self.lr = lr
        
        # Crear dataset
        self.dataset = SimpleFaceSwapDataset(image_dir)
        self.dataloader = DataLoader(
            self.dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=0
        )
        
        # Crear modelo
        self.model = SimpleFaceSwapModel().to(self.device)
        
        # Optimizador
        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=lr,
            betas=(0.5, 0.999),
            weight_decay=1e-5
        )
        
        # Loss functions
        self.mse_loss = nn.MSELoss()
        self.l1_loss = nn.L1Loss()
        
        # Scheduler
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.5,
            patience=5,
            verbose=True
        )
    
    def train(self, epochs: int = 30, save_path: str = "face_swap_simple_model.pth"):
        """
        Entrenar el modelo.
        
        Args:
            epochs: Número de épocas
            save_path: Ruta donde guardar el modelo
        """
        print(f"🚀 Usando dispositivo: {self.device}")
        print(f"📦 Dataset cargado: {len(self.dataset)} pares de imágenes")
        print("Iniciando entrenamiento...")
        
        self.model.train()
        best_loss = float('inf')
        
        for epoch in range(epochs):
            total_loss = 0
            
            for batch_idx, (source, target, ground_truth) in enumerate(self.dataloader):
                source = source.to(self.device)
                target = target.to(self.device)
                ground_truth = ground_truth.to(self.device)
                
                # Forward
                output = self.model(source, target)
                
                # Loss combinado (MSE + L1 para mejor convergencia)
                loss_mse = self.mse_loss(output, ground_truth)
                loss_l1 = self.l1_loss(output, ground_truth)
                loss = loss_mse + 0.3 * loss_l1
                
                # Backward
                self.optimizer.zero_grad()
                loss.backward()
                
                # Gradient clipping para estabilidad
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                self.optimizer.step()
                
                total_loss += loss.item()
                
                if batch_idx % 20 == 0:
                    print(f"  Epoch {epoch+1}/{epochs}, Batch {batch_idx}, Loss: {loss.item():.4f}")
            
            avg_loss = total_loss / len(self.dataloader)
            print(f"Epoch {epoch+1}/{epochs} completado. Loss promedio: {avg_loss:.4f}")
            
            # Actualizar learning rate
            self.scheduler.step(avg_loss)
            
            # Guardar mejor modelo
            if avg_loss < best_loss:
                best_loss = avg_loss
                torch.save({
                    'epoch': epoch + 1,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'loss': avg_loss,
                }, save_path.replace('.pth', '_best.pth'))
            
            # Guardar checkpoint periódico
            if (epoch + 1) % 10 == 0:
                checkpoint_path = f"checkpoint_simple_epoch_{epoch+1}.pth"
                torch.save({
                    'epoch': epoch + 1,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'loss': avg_loss,
                }, checkpoint_path)
                print(f"  Checkpoint guardado: {checkpoint_path}")
        
        # Guardar modelo final
        torch.save({
            'epoch': epochs,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'loss': avg_loss,
        }, save_path)
        
        print(f"\nEntrenamiento completado!")
        print(f"Modelo guardado en: {save_path}")
        print(f"Mejor modelo guardado en: {save_path.replace('.pth', '_best.pth')}")


def train_simple_model(
    image_dir: str,
    epochs: int = 30,
    batch_size: int = 4,
    lr: float = 0.0002,
    save_path: str = "face_swap_simple_model.pth"
):
    """
    Función de conveniencia para entrenar el modelo.
    
    Args:
        image_dir: Directorio con imágenes
        epochs: Número de épocas
        batch_size: Tamaño de batch
        lr: Learning rate
        save_path: Ruta donde guardar el modelo
    """
    trainer = SimpleFaceSwapTrainer(
        image_dir=image_dir,
        batch_size=batch_size,
        lr=lr
    )
    trainer.train(epochs=epochs, save_path=save_path)






