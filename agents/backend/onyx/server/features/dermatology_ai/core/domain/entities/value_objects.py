from dataclasses import dataclass
from typing import Dict


@dataclass
class SkinMetrics:
    overall_score: float
    texture_score: float
    hydration_score: float
    elasticity_score: float
    pigmentation_score: float
    pore_size_score: float
    wrinkles_score: float
    redness_score: float
    dark_spots_score: float
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "overall_score": self.overall_score,
            "texture_score": self.texture_score,
            "hydration_score": self.hydration_score,
            "elasticity_score": self.elasticity_score,
            "pigmentation_score": self.pigmentation_score,
            "pore_size_score": self.pore_size_score,
            "wrinkles_score": self.wrinkles_score,
            "redness_score": self.redness_score,
            "dark_spots_score": self.dark_spots_score,
        }


@dataclass
class Condition:
    name: str
    confidence: float
    severity: str
    description: str = None


@dataclass
class Recommendation:
    product_id: str
    product_name: str
    category: str
    priority: int
    reason: str
    confidence: float
    usage_frequency: str = None










