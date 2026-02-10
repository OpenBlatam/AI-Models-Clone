"""
Data Processors Module
=====================

Data processing and transformation components.

Author: BUL System
Date: 2024
"""

import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class TextProcessor(ABC):
    """
    Abstract base class for text processing.
    
    Allows custom text processing pipelines.
    """
    
    @abstractmethod
    def process(self, text: str) -> str:
        """
        Process text.
        
        Args:
            text: Input text
            
        Returns:
            Processed text
        """
        pass


class BasicTextProcessor(TextProcessor):
    """Basic text processor (no-op by default)."""
    
    def process(self, text: str) -> str:
        """Process text (returns as-is)."""
        return text.strip()


class DatasetProcessor:
    """
    Processor for dataset transformations.
    
    Handles preprocessing, cleaning, and transformation of datasets.
    
    Example:
        >>> processor = DatasetProcessor()
        >>> processed = processor.clean_dataset(raw_data)
        >>> processed = processor.normalize_dataset(processed)
    """
    
    def __init__(self, text_processor: Optional[TextProcessor] = None):
        """
        Initialize DatasetProcessor.
        
        Args:
            text_processor: Optional custom text processor
        """
        self.text_processor = text_processor or BasicTextProcessor()
    
    def clean_dataset(self, data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Clean dataset by removing invalid entries.
        
        Args:
            data: List of examples
            
        Returns:
            Cleaned dataset
        """
        cleaned = []
        for ex in data:
            prompt = self.text_processor.process(ex.get("prompt", ""))
            response = self.text_processor.process(ex.get("response", ""))
            
            if prompt and response:
                cleaned.append({"prompt": prompt, "response": response})
        
        logger.info(f"Cleaned dataset: {len(data)} -> {len(cleaned)} examples")
        return cleaned
    
    def normalize_dataset(self, data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Normalize dataset format.
        
        Args:
            data: List of examples
            
        Returns:
            Normalized dataset
        """
        normalized = []
        for ex in data:
            normalized.append({
                "prompt": ex.get("prompt", "").strip(),
                "response": ex.get("response", "").strip(),
            })
        return normalized
    
    def filter_by_length(
        self,
        data: List[Dict[str, str]],
        min_prompt_length: int = 0,
        max_prompt_length: Optional[int] = None,
        min_response_length: int = 0,
        max_response_length: Optional[int] = None,
    ) -> List[Dict[str, str]]:
        """
        Filter dataset by text lengths.
        
        Args:
            data: List of examples
            min_prompt_length: Minimum prompt length
            max_prompt_length: Maximum prompt length
            min_response_length: Minimum response length
            max_response_length: Maximum response length
            
        Returns:
            Filtered dataset
        """
        filtered = []
        for ex in data:
            prompt_len = len(ex.get("prompt", ""))
            response_len = len(ex.get("response", ""))
            
            if (prompt_len >= min_prompt_length and
                (max_prompt_length is None or prompt_len <= max_prompt_length) and
                response_len >= min_response_length and
                (max_response_length is None or response_len <= max_response_length)):
                filtered.append(ex)
        
        logger.info(f"Filtered dataset: {len(data)} -> {len(filtered)} examples")
        return filtered

