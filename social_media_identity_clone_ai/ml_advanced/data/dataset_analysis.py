"""
Análisis de datasets para deep learning
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
from pathlib import Path

logger = logging.getLogger(__name__)


class DatasetAnalyzer:
    """Analizador de datasets"""
    
    def __init__(self):
        pass
    
    def analyze_text_dataset(
        self,
        texts: List[str],
        tokenizer: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Analiza dataset de textos
        
        Args:
            texts: Lista de textos
            tokenizer: Tokenizer (opcional)
            
        Returns:
            Análisis completo
        """
        if not texts:
            return {}
        
        # Estadísticas básicas
        lengths = [len(text) for text in texts]
        word_counts = [len(text.split()) for text in texts]
        
        # Tokenización si hay tokenizer
        token_counts = []
        if tokenizer:
            for text in texts:
                tokens = tokenizer.encode(text, add_special_tokens=False)
                token_counts.append(len(tokens))
        
        # Análisis de vocabulario
        all_words = []
        for text in texts:
            all_words.extend(text.lower().split())
        
        word_freq = Counter(all_words)
        vocab_size = len(word_freq)
        
        # Caracteres especiales
        has_emojis = sum(1 for text in texts if any(ord(c) > 127 for c in text))
        has_hashtags = sum(1 for text in texts if '#' in text)
        has_mentions = sum(1 for text in texts if '@' in text)
        
        analysis = {
            "dataset_size": len(texts),
            "text_length": {
                "mean": float(np.mean(lengths)),
                "std": float(np.std(lengths)),
                "min": int(np.min(lengths)),
                "max": int(np.max(lengths)),
                "median": float(np.median(lengths))
            },
            "word_count": {
                "mean": float(np.mean(word_counts)),
                "std": float(np.std(word_counts)),
                "min": int(np.min(word_counts)),
                "max": int(np.max(word_counts)),
                "median": float(np.median(word_counts))
            },
            "vocabulary": {
                "vocab_size": vocab_size,
                "unique_words": vocab_size,
                "total_words": len(all_words),
                "avg_word_frequency": float(len(all_words) / vocab_size) if vocab_size > 0 else 0.0,
                "top_10_words": dict(word_freq.most_common(10))
            },
            "special_characters": {
                "has_emojis": has_emojis,
                "has_hashtags": has_hashtags,
                "has_mentions": has_mentions,
                "emoji_percentage": (has_emojis / len(texts)) * 100 if texts else 0.0
            }
        }
        
        if token_counts:
            analysis["token_count"] = {
                "mean": float(np.mean(token_counts)),
                "std": float(np.std(token_counts)),
                "min": int(np.min(token_counts)),
                "max": int(np.max(token_counts)),
                "median": float(np.median(token_counts))
            }
        
        return analysis
    
    def visualize_distribution(
        self,
        values: List[float],
        title: str = "Distribution",
        save_path: Optional[str] = None
    ):
        """Visualiza distribución"""
        try:
            plt.figure(figsize=(10, 6))
            plt.hist(values, bins=50, edgecolor='black')
            plt.title(title)
            plt.xlabel("Value")
            plt.ylabel("Frequency")
            plt.grid(True, alpha=0.3)
            
            if save_path:
                plt.savefig(save_path)
                logger.info(f"Gráfico guardado: {save_path}")
            else:
                plt.show()
        except Exception as e:
            logger.error(f"Error visualizando: {e}")




