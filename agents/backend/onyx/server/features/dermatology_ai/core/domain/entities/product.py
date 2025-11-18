from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from .enums import SkinType


@dataclass
class Product:
    id: str
    name: str
    category: str
    description: Optional[str] = None
    ingredients: List[str] = field(default_factory=list)
    price: Optional[float] = None
    rating: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_suitable_for_skin_type(self, skin_type: SkinType) -> bool:
        return True










