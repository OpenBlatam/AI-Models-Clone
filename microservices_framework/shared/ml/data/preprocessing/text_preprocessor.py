"""
Text Preprocessing
Specialized text preprocessing utilities.
"""

from typing import List, Callable, Optional
import re
from functools import partial


class TextPreprocessor:
    """Text preprocessing pipeline."""
    
    def __init__(self):
        self.steps: List[Callable] = []
    
    def add_step(self, func: Callable, *args, **kwargs):
        """Add a preprocessing step."""
        if args or kwargs:
            self.steps.append(partial(func, *args, **kwargs))
        else:
            self.steps.append(func)
        return self
    
    def process(self, text: str) -> str:
        """Process text through all steps."""
        result = text
        for step in self.steps:
            result = step(result)
        return result
    
    def process_batch(self, texts: List[str]) -> List[str]:
        """Process a batch of texts."""
        return [self.process(text) for text in texts]


def lowercase(text: str) -> str:
    """Convert to lowercase."""
    return text.lower()


def remove_extra_whitespace(text: str) -> str:
    """Remove extra whitespace."""
    return " ".join(text.split())


def remove_special_chars(text: str, keep_chars: Optional[str] = None) -> str:
    """Remove special characters."""
    if keep_chars:
        pattern = f"[^{keep_chars} ]"
    else:
        pattern = r"[^a-zA-Z0-9\s]"
    return re.sub(pattern, "", text)


def truncate(text: str, max_length: int) -> str:
    """Truncate text to max length."""
    return text[:max_length]


def normalize_unicode(text: str) -> str:
    """Normalize unicode characters."""
    import unicodedata
    return unicodedata.normalize("NFKD", text)


def create_text_preprocessor(
    lowercase: bool = True,
    remove_whitespace: bool = True,
    remove_special: bool = False,
    max_length: Optional[int] = None,
) -> TextPreprocessor:
    """Create a text preprocessor with common steps."""
    preprocessor = TextPreprocessor()
    
    if lowercase:
        preprocessor.add_step(lowercase)
    
    if remove_whitespace:
        preprocessor.add_step(remove_extra_whitespace)
    
    if remove_special:
        preprocessor.add_step(remove_special_chars)
    
    if max_length:
        preprocessor.add_step(truncate, max_length)
    
    return preprocessor



