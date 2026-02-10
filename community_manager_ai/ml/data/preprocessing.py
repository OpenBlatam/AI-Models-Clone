"""
Data Preprocessing - Preprocesamiento de Datos
==============================================

Pipeline de preprocesamiento optimizado.
"""

import torch
from torch.utils.data import Dataset
from typing import List, Dict, Any, Optional, Callable, Tuple
from transformers import AutoTokenizer
import numpy as np
from functools import lru_cache


class TextPreprocessor:
    """Preprocesador de texto optimizado"""
    
    def __init__(
        self,
        tokenizer: Any,
        max_length: int = 512,
        padding: str = "max_length",
        truncation: bool = True
    ):
        """
        Inicializar preprocesador
        
        Args:
            tokenizer: Tokenizer a usar
            max_length: Longitud máxima
            padding: Estrategia de padding
            truncation: Truncar si es necesario
        """
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.padding = padding
        self.truncation = truncation
    
    @lru_cache(maxsize=1000)
    def preprocess(self, text: str) -> Dict[str, torch.Tensor]:
        """
        Preprocesar texto (con cache)
        
        Args:
            text: Texto a preprocesar
            
        Returns:
            Dict con tokens
        """
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding=self.padding,
            truncation=self.truncation,
            return_tensors="pt"
        )
        
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0)
        }
    
    def preprocess_batch(self, texts: List[str]) -> Dict[str, torch.Tensor]:
        """
        Preprocesar batch de textos
        
        Args:
            texts: Lista de textos
            
        Returns:
            Dict con batch de tokens
        """
        encodings = self.tokenizer(
            texts,
            max_length=self.max_length,
            padding=self.padding,
            truncation=self.truncation,
            return_tensors="pt"
        )
        
        return encodings


class ImagePreprocessor:
    """Preprocesador de imágenes"""
    
    def __init__(
        self,
        size: Tuple[int, int] = (512, 512),
        mean: Optional[List[float]] = None,
        std: Optional[List[float]] = None
    ):
        """
        Inicializar preprocesador de imágenes
        
        Args:
            size: Tamaño objetivo
            mean: Media para normalización
            std: Desviación estándar
        """
        from torchvision import transforms
        
        self.size = size
        self.mean = mean or [0.485, 0.456, 0.406]
        self.std = std or [0.229, 0.224, 0.225]
        
        self.transform = transforms.Compose([
            transforms.Resize(size),
            transforms.ToTensor(),
            transforms.Normalize(mean=self.mean, std=self.std)
        ])
    
    def preprocess(self, image) -> torch.Tensor:
        """
        Preprocesar imagen
        
        Args:
            image: Imagen (PIL Image)
            
        Returns:
            Tensor preprocesado
        """
        return self.transform(image)
    
    def preprocess_batch(self, images: List) -> torch.Tensor:
        """
        Preprocesar batch de imágenes
        
        Args:
            images: Lista de imágenes
            
        Returns:
            Batch tensor
        """
        tensors = [self.preprocess(img) for img in images]
        return torch.stack(tensors)


class DataAugmentation:
    """Data augmentation para entrenamiento"""
    
    def __init__(self, augmentation_type: str = "text"):
        """
        Inicializar data augmentation
        
        Args:
            augmentation_type: Tipo (text, image)
        """
        self.augmentation_type = augmentation_type
    
    def augment_text(self, text: str) -> str:
        """
        Augmentar texto
        
        Args:
            text: Texto original
            
        Returns:
            Texto augmentado
        """
        # Técnicas simples de augmentation
        # TODO: Integrar con bibliotecas como nlpaug
        return text
    
    def augment_image(self, image) -> Any:
        """
        Augmentar imagen
        
        Args:
            image: Imagen original
            
        Returns:
            Imagen augmentada
        """
        from torchvision import transforms
        
        augment_transform = transforms.Compose([
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=10),
            transforms.ColorJitter(brightness=0.2, contrast=0.2)
        ])
        
        return augment_transform(image)

