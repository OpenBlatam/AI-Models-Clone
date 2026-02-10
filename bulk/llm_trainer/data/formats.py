"""
Dataset Format Support Module
==============================

Support for multiple dataset formats (JSON, CSV, Parquet, etc.)

Author: BUL System
Date: 2024
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
import csv

logger = logging.getLogger(__name__)


class DatasetFormatLoader:
    """
    Loader for different dataset formats.
    
    Supports:
    - JSON (default)
    - CSV
    - Parquet (if pandas available)
    
    Example:
        >>> loader = DatasetFormatLoader()
        >>> data = loader.load("data.json")  # Auto-detect format
        >>> data = loader.load_csv("data.csv")
    """
    
    @staticmethod
    def load(file_path: Union[str, Path]) -> List[Dict[str, str]]:
        """
        Load dataset from file, auto-detecting format.
        
        Args:
            file_path: Path to dataset file
            
        Returns:
            List of dictionaries with "prompt" and "response"
            
        Raises:
            ValueError: If format is not supported or file is invalid
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix == '.json':
            return DatasetFormatLoader.load_json(path)
        elif suffix == '.csv':
            return DatasetFormatLoader.load_csv(path)
        elif suffix == '.parquet':
            return DatasetFormatLoader.load_parquet(path)
        else:
            # Try JSON by default
            logger.warning(f"Unknown file extension {suffix}, trying JSON format")
            return DatasetFormatLoader.load_json(path)
    
    @staticmethod
    def load_json(file_path: Path) -> List[Dict[str, str]]:
        """
        Load dataset from JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            List of dictionaries
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Normalize format
        if isinstance(data, dict):
            for key in ["data", "examples", "dataset", "samples"]:
                if key in data:
                    data = data[key]
                    break
        
        if not isinstance(data, list):
            raise ValueError(f"JSON file must contain a list, got {type(data)}")
        
        return data
    
    @staticmethod
    def load_csv(file_path: Path) -> List[Dict[str, str]]:
        """
        Load dataset from CSV file.
        
        CSV should have columns: prompt, response
        Or: input, output / question, answer (auto-mapped)
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of dictionaries with "prompt" and "response"
        """
        data = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Map common column names
            column_mapping = {
                'input': 'prompt',
                'question': 'prompt',
                'text': 'prompt',
                'output': 'response',
                'answer': 'response',
                'target': 'response',
            }
            
            for row in reader:
                # Map columns
                mapped_row = {}
                for key, value in row.items():
                    mapped_key = column_mapping.get(key.lower(), key.lower())
                    if mapped_key in ['prompt', 'response']:
                        mapped_row[mapped_key] = value.strip() if value else ""
                
                # Ensure we have both fields
                if 'prompt' in mapped_row and 'response' in mapped_row:
                    data.append({
                        'prompt': mapped_row['prompt'],
                        'response': mapped_row['response']
                    })
                elif 'prompt' in row and 'response' in row:
                    data.append({
                        'prompt': row['prompt'].strip(),
                        'response': row['response'].strip()
                    })
        
        if not data:
            raise ValueError("No valid prompt/response pairs found in CSV")
        
        logger.info(f"Loaded {len(data)} examples from CSV")
        return data
    
    @staticmethod
    def load_parquet(file_path: Path) -> List[Dict[str, str]]:
        """
        Load dataset from Parquet file.
        
        Args:
            file_path: Path to Parquet file
            
        Returns:
            List of dictionaries with "prompt" and "response"
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for Parquet support. Install with: pip install pandas")
        
        df = pd.read_parquet(file_path)
        
        # Map common column names
        column_mapping = {
            'input': 'prompt',
            'question': 'prompt',
            'text': 'prompt',
            'output': 'response',
            'answer': 'response',
            'target': 'response',
        }
        
        # Rename columns
        df.columns = [column_mapping.get(col.lower(), col.lower()) for col in df.columns]
        
        # Ensure we have required columns
        if 'prompt' not in df.columns or 'response' not in df.columns:
            raise ValueError("Parquet file must contain 'prompt' and 'response' columns (or mapped equivalents)")
        
        data = [
            {'prompt': str(row['prompt']), 'response': str(row['response'])}
            for _, row in df.iterrows()
        ]
        
        logger.info(f"Loaded {len(data)} examples from Parquet")
        return data

