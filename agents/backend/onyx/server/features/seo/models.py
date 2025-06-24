from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class SEOScrapeRequest(BaseModel):
    url: str = Field(..., description="URL a analizar o scrapear", example="https://ejemplo.com")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Opciones adicionales para el scraping")

class SEOScrapeResponse(BaseModel):
    success: bool = Field(..., example=True)
    data: Optional[Dict[str, Any]] = Field(None, description="Datos extraídos o analizados")
    error: Optional[str] = Field(None, description="Mensaje de error si falla el scraping") 