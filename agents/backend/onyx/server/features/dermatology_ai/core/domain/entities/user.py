from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

from .enums import SkinType


@dataclass
class User:
    id: str
    email: str
    name: Optional[str] = None
    skin_type: Optional[SkinType] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def update_preferences(self, preferences: Dict[str, Any]):
        self.preferences.update(preferences)
        self.updated_at = datetime.utcnow()










