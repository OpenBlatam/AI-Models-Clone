"""
Data Augmentation Module

Text augmentation techniques for training data.
"""

import sys
from pathlib import Path

# Import from parent directory
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from preprocessing_utils import DataAugmentation

__all__ = [
    "DataAugmentation",
]

