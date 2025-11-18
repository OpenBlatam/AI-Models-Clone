"""
Batch processing for code explanations
"""

import logging
from typing import List, Dict, Any, Optional
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from .validator import InputValidator
from .prompt_builder import PromptBuilder
from .cache import ExplanationCache

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Processes batches of code explanations"""
    
    def __init__(
        self,
        model: AutoModelForSeq2SeqLM,
        tokenizer: AutoTokenizer,
        device: torch.device,
        max_length: int,
        max_target_length: int,
        cache: Optional[ExplanationCache] = None
    ):
        """Initialize batch processor
        
        Args:
            model: Model instance
            tokenizer: Tokenizer instance
            device: Device to run on
            max_length: Maximum input length
            max_target_length: Maximum target length
            cache: Cache instance (optional)
        """
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.max_length = max_length
        self.max_target_length = max_target_length
        self.cache = cache
        self.validator = InputValidator()
        self.prompt_builder = PromptBuilder()
    
    def process(
        self,
        codes: List[str],
        max_length: Optional[int] = None,
        temperature: float = 0.7,
        num_beams: int = 4,
        **kwargs: Any
    ) -> List[str]:
        """Process batch of codes
        
        Args:
            codes: List of codes to explain
            max_length: Maximum generation length
            temperature: Sampling temperature
            num_beams: Number of beams
            **kwargs: Additional generation parameters
            
        Returns:
            List of explanations
            
        Raises:
            ValueError: If no valid codes provided
            RuntimeError: If processing fails
        """
        # Validate and filter codes
        valid_codes = self.validator.validate_batch_codes(codes)
        if not valid_codes:
            raise ValueError("No valid codes provided")
        
        # Build prompts
        prompts = self.prompt_builder.build_batch(valid_codes)
        
        try:
            # Tokenize batch
            inputs = self.tokenizer(
                prompts,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_length,
                padding=True
            ).to(self.device)
            
            max_gen_length = max_length or self.max_target_length
            
            # Generate batch
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_gen_length,
                    temperature=temperature,
                    num_beams=num_beams,
                    early_stopping=True,
                    **kwargs
                )
            
            # Decode batch
            explanations = [
                self.tokenizer.decode(output, skip_special_tokens=True).strip()
                for output in outputs
            ]
            
            # Cache results
            if self.cache and self.cache.enabled:
                for code, explanation in zip(valid_codes, explanations):
                    if explanation:
                        self.cache.set(
                            code,
                            explanation,
                            max_length=max_length,
                            temperature=temperature,
                            num_beams=num_beams,
                            **kwargs
                        )
            
            return explanations
            
        except Exception as e:
            logger.error(f"Error processing batch: {e}", exc_info=True)
            raise RuntimeError(f"Failed to process batch: {e}") from e

