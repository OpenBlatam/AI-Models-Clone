"""
Data Validators Module
======================

Validation components for datasets and formats.

Author: BUL System
Date: 2024
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class FormatValidator(ABC):
    """
    Abstract base class for format validators.
    
    Allows creating custom format validators.
    """
    
    @abstractmethod
    def validate(self, data: Any) -> tuple[bool, Optional[str]]:
        """
        Validate data format.
        
        Args:
            data: Data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass


class JSONFormatValidator(FormatValidator):
    """Validator for JSON format."""
    
    def validate(self, data: Any) -> Tuple[bool, Optional[str]]:
        """Validate JSON format."""
        try:
            if isinstance(data, str):
                json.loads(data)
            elif isinstance(data, (dict, list)):
                json.dumps(data)  # Test serialization
            else:
                return False, f"Invalid JSON type: {type(data)}"
            return True, None
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"


class DatasetValidator:
    """
    Validator for dataset format and quality.
    
    Validates structure, content, and quality of training datasets.
    
    Example:
        >>> validator = DatasetValidator()
        >>> is_valid, errors = validator.validate_structure(data)
        >>> quality = validator.validate_quality(data)
    """
    
    def __init__(self):
        """Initialize DatasetValidator."""
        self.format_validator = JSONFormatValidator()
    
    def validate_structure(self, data: List[Dict[str, str]]) -> Tuple[bool, List[str]]:
        """
        Validate dataset structure.
        
        Args:
            data: List of example dictionaries
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        if not isinstance(data, list):
            errors.append("Dataset must be a list")
            return False, errors
        
        if len(data) == 0:
            errors.append("Dataset is empty")
            return False, errors
        
        required_fields = ["prompt", "response"]
        
        for i, example in enumerate(data):
            if not isinstance(example, dict):
                errors.append(f"Example {i} must be a dictionary")
                continue
            
            for field in required_fields:
                if field not in example:
                    errors.append(f"Example {i} missing field '{field}'")
                elif not isinstance(example[field], str):
                    errors.append(f"Example {i} field '{field}' must be a string")
                elif not example[field].strip():
                    errors.append(f"Example {i} field '{field}' is empty")
        
        return len(errors) == 0, errors
    
    def validate_quality(self, data: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Validate dataset quality metrics.
        
        Args:
            data: List of example dictionaries
            
        Returns:
            Dictionary with quality metrics
        """
        if not data:
            return {"quality_score": 0, "warnings": ["Dataset is empty"], "is_valid": False}
        
        warnings = []
        score = 100.0
        
        # Check duplicates
        unique_prompts = set(ex["prompt"].lower().strip() for ex in data)
        duplicate_ratio = 1 - (len(unique_prompts) / len(data))
        if duplicate_ratio > 0.1:
            warnings.append(f"High duplicate ratio: {duplicate_ratio:.2%}")
            score -= duplicate_ratio * 20
        
        # Check response lengths
        response_lengths = [len(ex["response"]) for ex in data]
        avg_length = sum(response_lengths) / len(response_lengths)
        short_responses = sum(1 for l in response_lengths if l < 10)
        
        if short_responses > len(data) * 0.1:
            warnings.append(f"Many short responses: {short_responses}/{len(data)}")
            score -= (short_responses / len(data)) * 15
        
        # Check dataset size
        if len(data) < 10:
            warnings.append("Dataset is very small (< 10 examples)")
            score -= 10
        elif len(data) < 100:
            warnings.append("Dataset is small (< 100 examples)")
            score -= 5
        
        return {
            "quality_score": max(0, score),
            "warnings": warnings,
            "is_valid": score >= 70,
            "duplicate_ratio": duplicate_ratio,
            "avg_response_length": avg_length,
        }
    
    def validate_file(self, file_path: Path) -> Tuple[bool, List[str], Optional[List[Dict[str, str]]]]:
        """
        Validate dataset file.
        
        Args:
            file_path: Path to dataset file
            
        Returns:
            Tuple of (is_valid, errors, data)
        """
        errors = []
        
        # Check file exists
        if not file_path.exists():
            errors.append(f"File not found: {file_path}")
            return False, errors, None
        
        # Check file is readable
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {e}")
            return False, errors, None
        except Exception as e:
            errors.append(f"Error reading file: {e}")
            return False, errors, None
        
        # Normalize format
        if isinstance(data, dict):
            if "data" in data:
                data = data["data"]
            elif "examples" in data:
                data = data["examples"]
            else:
                errors.append("Dataset dict must contain 'data' or 'examples'")
                return False, errors, None
        
        # Validate structure
        is_valid, structure_errors = self.validate_structure(data)
        errors.extend(structure_errors)
        
        return is_valid, errors, data if is_valid else None

