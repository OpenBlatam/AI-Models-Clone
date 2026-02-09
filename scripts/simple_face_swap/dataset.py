"""
Simple Face Swap Dataset
========================
Dataset para entrenar el modelo de face swap.
"""

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset
from pathlib import Path

from .detector import SimpleFaceDetector


class SimpleFaceSwapDataset(Dataset):
    """Dataset simple para entrenar."""
    
    def __init__(self, image_dir: str, size: int = 256):
        """
        Inicializar dataset.
        
        Args:
            image_dir: Directorio con imágenes
            size: Tamaño de las caras
        """
        self.image_dir = Path(image_dir)
        self.size = size
        self.detector = SimpleFaceDetector()
        
        # Obtener imágenes
        self.images = (
            list(self.image_dir.glob("*.jpg")) +
            list(self.image_dir.glob("*.png")) +
            list(self.image_dir.glob("*.jpeg"))
        )
        
        if len(self.images) < 2:
            raise ValueError("Se necesitan al menos 2 imágenes")
    
    def __len__(self):
        """Tamaño del dataset (aumentado con data augmentation)."""
        return len(self.images) * 20
    
    def __getitem__(self, idx):
        """
        Obtener item del dataset.
        
        Args:
            idx: Índice del item
        
        Returns:
            (source, target, ground_truth) tensors
        """
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






