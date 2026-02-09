from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
MODULAR ADS - Types Module
========================

Tipos, enums y definiciones de datos para el sistema de ads modular.
Módulo independiente y reutilizable.
"""


class AdType(Enum):
    """Tipos de ads soportados en el sistema modular"""
    FACEBOOK = "facebook"
    GOOGLE = "google"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    PINTEREST = "pinterest"

class AdPriority(Enum):
    """Niveles de prioridad para ads"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    MINIMAL = 1

class CacheLevel(Enum):
    """Niveles de cache disponibles"""
    L1_MEMORY = "l1_memory"
    L2_COMPRESSED = "l2_compressed"
    L3_CAMPAIGN = "l3_campaign"
    L4_DISTRIBUTED = "l4_distributed"

class PerformanceTier(Enum):
    """Tiers de performance del sistema"""
    ULTRA_MAXIMUM = ("ULTRA MAXIMUM", 95.0)
    MAXIMUM = ("MAXIMUM", 85.0)
    ULTRA = ("ULTRA", 70.0)
    OPTIMIZED = ("OPTIMIZED", 50.0)
    ENHANCED = ("ENHANCED", 30.0)
    STANDARD = ("STANDARD", 0.0)
    
    def __init__(self, display_name: str, threshold: float):
        
    """__init__ function."""
self.display_name = display_name
        self.threshold = threshold

class AdStatus(Enum):
    """Estados de los ads"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class OptimizationLevel(Enum):
    """Niveles de optimización"""
    BASIC = "basic"
    ADVANCED = "advanced"
    ULTRA = "ultra"
    MAXIMUM = "maximum"

# Type aliases para mayor claridad
AdID = str
CampaignID = str
UserID = str
Timestamp = float
Score = float
Milliseconds = float

# Constantes del sistema
DEFAULT_CACHE_TTL = 3600  # 1 hora
MAX_AD_CONTENT_LENGTH = 500
MAX_KEYWORDS_COUNT = 10
MAX_BATCH_SIZE = 100
DEFAULT_TIMEOUT = 30.0

__all__ = [
    # Enums
    'AdType',
    'AdPriority',
    'CacheLevel', 
    'PerformanceTier',
    'AdStatus',
    'OptimizationLevel',
    
    # Type aliases
    'AdID',
    'CampaignID',
    'UserID',
    'Timestamp',
    'Score',
    'Milliseconds',
    
    # Constants
    'DEFAULT_CACHE_TTL',
    'MAX_AD_CONTENT_LENGTH',
    'MAX_KEYWORDS_COUNT',
    'MAX_BATCH_SIZE',
    'DEFAULT_TIMEOUT',
] 