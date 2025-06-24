from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class RytrTone(str, Enum):
    assertive = "Assertive"
    awestruck = "Awestruck"
    candid = "Candid"
    casual = "Casual"
    cautionary = "Cautionary"
    compassionate = "Compassionate"
    convincing = "Convincing"
    critical = "Critical"
    earnest = "Earnest"
    enthusiastic = "Enthusiastic"
    formal = "Formal"
    funny = "Funny"
    humble = "Humble"
    humorous = "Humorous"
    informative = "Informative"
    inspirational = "Inspirational"
    joyful = "Joyful"
    passionate = "Passionate"
    playful = "Playful"
    positive = "Positive"
    professional = "Professional"
    sarcastic = "Sarcastic"
    thoughtful = "Thoughtful"
    urgent = "Urgent"
    witty = "Witty"

class CopywritingInput(BaseModel):
    product_description: str = Field(..., description="Descripción del producto o servicio")
    target_platform: str = Field(..., description="Plataforma donde se usará el copy")
    tone: RytrTone = Field(..., description="Tono deseado del copy (Rytr)")
    target_audience: Optional[str] = Field(None, description="Audiencia objetivo")
    key_points: Optional[List[str]] = Field(None, description="Puntos clave a destacar")

class CopywritingOutput(BaseModel):
    headline: str = Field(..., description="Encabezado principal")
    primary_text: str = Field(..., description="Texto principal del copy")
    hashtags: Optional[List[str]] = Field(None, description="Hashtags relevantes")
    platform_tips: Optional[str] = Field(None, description="Tips específicos para la plataforma") 