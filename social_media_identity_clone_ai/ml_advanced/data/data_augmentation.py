"""
Data augmentation para textos
"""

import logging
import random
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)


class TextAugmenter:
    """Augmentador de textos"""
    
    def __init__(self):
        pass
    
    def synonym_replacement(
        self,
        text: str,
        num_replacements: int = 2
    ) -> str:
        """
        Reemplazo de sinónimos (simplificado)
        
        Args:
            text: Texto original
            num_replacements: Número de reemplazos
            
        Returns:
            Texto aumentado
        """
        # En producción usaría WordNet o similar
        # Por ahora, retornar texto original
        return text
    
    def random_deletion(
        self,
        text: str,
        deletion_prob: float = 0.1
    ) -> str:
        """
        Eliminación aleatoria de palabras
        
        Args:
            text: Texto original
            deletion_prob: Probabilidad de eliminar palabra
            
        Returns:
            Texto aumentado
        """
        words = text.split()
        augmented_words = [
            word for word in words
            if random.random() > deletion_prob
        ]
        return " ".join(augmented_words)
    
    def random_swap(
        self,
        text: str,
        num_swaps: int = 2
    ) -> str:
        """
        Intercambio aleatorio de palabras
        
        Args:
            text: Texto original
            num_swaps: Número de intercambios
            
        Returns:
            Texto aumentado
        """
        words = text.split()
        if len(words) < 2:
            return text
        
        for _ in range(num_swaps):
            idx1, idx2 = random.sample(range(len(words)), 2)
            words[idx1], words[idx2] = words[idx2], words[idx1]
        
        return " ".join(words)
    
    def back_translation(
        self,
        text: str,
        target_language: str = "es"
    ) -> str:
        """
        Back translation (requiere modelo de traducción)
        
        Args:
            text: Texto original
            target_language: Idioma objetivo
            
        Returns:
            Texto aumentado
        """
        # En producción usaría modelo de traducción
        # Por ahora, retornar texto original
        return text
    
    def augment_batch(
        self,
        texts: List[str],
        methods: List[str] = ["random_deletion", "random_swap"],
        num_augmentations: int = 1
    ) -> List[str]:
        """
        Aumenta batch de textos
        
        Args:
            texts: Lista de textos
            methods: Métodos de augmentación
            num_augmentations: Número de aumentos por texto
            
        Returns:
            Textos aumentados
        """
        augmented_texts = []
        
        for text in texts:
            augmented_texts.append(text)  # Original
            
            for _ in range(num_augmentations):
                method = random.choice(methods)
                
                if method == "random_deletion":
                    augmented = self.random_deletion(text)
                elif method == "random_swap":
                    augmented = self.random_swap(text)
                elif method == "synonym_replacement":
                    augmented = self.synonym_replacement(text)
                else:
                    augmented = text
                
                augmented_texts.append(augmented)
        
        return augmented_texts




