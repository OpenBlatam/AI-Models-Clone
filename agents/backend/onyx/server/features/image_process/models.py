from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, root_validator
"""Pydantic models for Image Process feature."""

class ImageBaseRequest(BaseModel):
    """Request base para operaciones de imagen. Debe incluir image_url o image_base64."""
    image_url: Optional[str] = Field(
        None,
        description="URL de la imagen a procesar",
        example="https://example.com/imagen.jpg"
    )
    image_base64: Optional[str] = Field(
        None,
        description="Imagen codificada en base64",
        example="iVBORw0KGgoAAAANSUhEUgAA..."
    )

    @root_validator(skip_on_failure=True)
    def at_least_one_source(cls, values) -> Any:
        if not values.get("image_url") and not values.get("image_base64"):
            raise ValueError("Debes proporcionar image_url o image_base64")
        return values

class ImageExtractRequest(ImageBaseRequest):
    """Request para extracción de texto u objetos de una imagen."""
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Opciones adicionales para la extracción",
        example={"ocr": True, "language": "spa"}
    )

class ImageExtractResponse(BaseModel):
    """Respuesta para extracción de texto u objetos de una imagen."""
    success: bool = Field(..., example=True)
    extracted_text: Optional[str] = Field(None, example="Texto extraído de la imagen")
    error: Optional[str] = Field(None, example="Error al procesar la imagen")
    metadata: Optional[Dict[str, Any]] = Field(None, example={"ocr_confidence": 0.98})

class ImageSummaryRequest(ImageBaseRequest):
    """Request para resumen de imagen."""
    summary_type: Optional[str] = Field(
        "simple",
        description="Tipo de resumen: simple, avanzado, etc.",
        example="simple"
    )

class ImageSummaryResponse(BaseModel):
    """Respuesta para resumen de imagen."""
    success: bool = Field(..., example=True)
    summary: Optional[str] = Field(None, example="Resumen generado de la imagen")
    error: Optional[str] = Field(None, example="Error al generar el resumen")
    metadata: Optional[Dict[str, Any]] = Field(None, example={"summary_type": "simple"})

class ImageValidationRequest(ImageBaseRequest):
    """Request para validación de imagen."""
    validation_type: Optional[str] = Field(
        "default",
        description="Tipo de validación",
        example="default"
    )

class ImageValidationResponse(BaseModel):
    """Respuesta para validación de imagen."""
    success: bool = Field(..., example=True)
    is_valid: Optional[bool] = Field(None, example=True)
    error: Optional[str] = Field(None, example="Formato de imagen no soportado")
    details: Optional[Dict[str, Any]] = Field(None, example={"format": "jpg", "size": "1024x768"})

class ImageAnalysisResult(BaseModel):
    """Resultado de análisis de imagen (etiquetas, OCR, objetos, etc)."""
    labels: Optional[List[str]] = Field(None, description="Etiquetas detectadas en la imagen", example=["persona", "auto"])
    confidence_scores: Optional[Dict[str, float]] = Field(None, description="Confianza por etiqueta", example={"persona": 0.98, "auto": 0.85})
    ocr_text: Optional[str] = Field(None, description="Texto extraído por OCR", example="Texto detectado en la imagen")
    faces_detected: Optional[int] = Field(None, description="Número de rostros detectados", example=2)
    objects: Optional[List[Dict[str, Any]]] = Field(None, description="Objetos detectados", example=[{"type": "auto", "confidence": 0.85}])
    metadata: Optional[Dict[str, Any]] = Field(None, example={"procesado_por": "modelo-v1"}) 