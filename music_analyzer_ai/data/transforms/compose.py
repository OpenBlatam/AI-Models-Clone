"""
Compose Transformations
Chain multiple transformations together
"""

from typing import List, Callable, Any
import logging

logger = logging.getLogger(__name__)


class Compose:
    """
    Compose multiple transformations
    Similar to torchvision.transforms.Compose
    """
    
    def __init__(self, transforms: List[Callable]):
        self.transforms = transforms
    
    def __call__(self, data: Any) -> Any:
        """Apply all transformations in sequence"""
        for transform in self.transforms:
            try:
                data = transform(data)
            except Exception as e:
                logger.error(f"Error in transform {transform.__class__.__name__}: {str(e)}")
                raise
        return data
    
    def __repr__(self) -> str:
        format_string = self.__class__.__name__ + '('
        for t in self.transforms:
            format_string += '\n    ' + str(t)
        format_string += '\n)'
        return format_string


class ComposeTransforms:
    """
    Compose transformations with different input/output types
    """
    
    def __init__(self, transforms: List[Callable]):
        self.transforms = transforms
    
    def __call__(self, *args, **kwargs) -> Any:
        """Apply transformations"""
        result = args[0] if args else None
        
        for transform in self.transforms:
            if result is None:
                result = transform(*args, **kwargs)
            else:
                # Try to pass result and remaining args
                try:
                    result = transform(result, *args[1:], **kwargs)
                except TypeError:
                    # If transform doesn't accept result, try with original args
                    result = transform(*args, **kwargs)
        
        return result



