"""
Service for Image Process feature (Onyx) with guard clauses.
"""
import base64
from typing import Optional, Dict, Any
from .models import (
    ImageExtractRequest, ImageExtractResponse,
    ImageSummaryRequest, ImageSummaryResponse,
    ImageValidationRequest, ImageValidationResponse,
    ImageAnalysisResult
)
from . import extract, image_utils, image_sumary, validation

class ImageProcessService:
    """Central service for image extraction, summary, validation, and analysis with guard clauses."""

    @staticmethod
    def extract_text(request: ImageExtractRequest) -> ImageExtractResponse:
        """Extract text from image with guard clauses."""
        # Guard clause: Validate request
        if not request:
            return ImageExtractResponse(success=False, error="Request cannot be null")
        
        # Guard clause: Check if image is provided
        if not request.image_url and not request.image_base64:
            return ImageExtractResponse(success=False, error="No image provided")
        
        # Guard clause: Validate image URL format
        if request.image_url and not request.image_url.strip():
            return ImageExtractResponse(success=False, error="Image URL cannot be empty")
        
        # Guard clause: Validate base64 format
        if request.image_base64 and not request.image_base64.strip():
            return ImageExtractResponse(success=False, error="Base64 image cannot be empty")
        
        try:
            # Lógica de extract.py
            if request.image_url:
                text = extract.extract_text_from_url(request.image_url, **request.options)
            else:
                text = extract.extract_text_from_base64(request.image_base64, **request.options)
            
            return ImageExtractResponse(success=True, extracted_text=text)
        except Exception as e:
            return ImageExtractResponse(success=False, error=str(e))

    @staticmethod
    def summarize(request: ImageSummaryRequest) -> ImageSummaryResponse:
        """Summarize image with guard clauses."""
        # Guard clause: Validate request
        if not request:
            return ImageSummaryResponse(success=False, error="Request cannot be null")
        
        # Guard clause: Check if image is provided
        if not request.image_url and not request.image_base64:
            return ImageSummaryResponse(success=False, error="No image provided")
        
        # Guard clause: Validate image URL format
        if request.image_url and not request.image_url.strip():
            return ImageSummaryResponse(success=False, error="Image URL cannot be empty")
        
        # Guard clause: Validate base64 format
        if request.image_base64 and not request.image_base64.strip():
            return ImageSummaryResponse(success=False, error="Base64 image cannot be empty")
        
        # Guard clause: Validate summary type
        valid_summary_types = ["brief", "detailed", "technical", "creative"]
        if request.summary_type and request.summary_type not in valid_summary_types:
            return ImageSummaryResponse(success=False, error=f"Invalid summary type. Must be one of: {', '.join(valid_summary_types)}")
        
        try:
            # Lógica de image-sumary.py
            if request.image_url:
                summary = image_sumary.summarize_image_url(request.image_url, summary_type=request.summary_type)
            else:
                summary = image_sumary.summarize_image_base64(request.image_base64, summary_type=request.summary_type)
            
            return ImageSummaryResponse(success=True, summary=summary)
        except Exception as e:
            return ImageSummaryResponse(success=False, error=str(e))

    @staticmethod
    def validate(request: ImageValidationRequest) -> ImageValidationResponse:
        """Validate image with guard clauses."""
        # Guard clause: Validate request
        if not request:
            return ImageValidationResponse(success=False, error="Request cannot be null")
        
        # Guard clause: Check if image is provided
        if not request.image_url and not request.image_base64:
            return ImageValidationResponse(success=False, error="No image provided")
        
        # Guard clause: Validate image URL format
        if request.image_url and not request.image_url.strip():
            return ImageValidationResponse(success=False, error="Image URL cannot be empty")
        
        # Guard clause: Validate base64 format
        if request.image_base64 and not request.image_base64.strip():
            return ImageValidationResponse(success=False, error="Base64 image cannot be empty")
        
        # Guard clause: Validate validation type
        valid_validation_types = ["format", "content", "size", "quality", "security"]
        if request.validation_type and request.validation_type not in valid_validation_types:
            return ImageValidationResponse(success=False, error=f"Invalid validation type. Must be one of: {', '.join(valid_validation_types)}")
        
        try:
            # Lógica de validation.py
            if request.image_url:
                is_valid, details = validation.validate_image_url(request.image_url, validation_type=request.validation_type)
            else:
                is_valid, details = validation.validate_image_base64(request.image_base64, validation_type=request.validation_type)
            
            return ImageValidationResponse(success=True, is_valid=is_valid, details=details)
        except Exception as e:
            return ImageValidationResponse(success=False, error=str(e))

    @staticmethod
    def analyze(request: ImageExtractRequest) -> ImageAnalysisResult:
        """Analyze image with guard clauses."""
        # Guard clause: Validate request
        if not request:
            return ImageAnalysisResult(
                labels=[],
                confidence_scores={},
                ocr_text="",
                faces_detected=0,
                objects=[],
                metadata={"error": "Request cannot be null"}
            )
        
        # Guard clause: Check if image is provided
        if not request.image_url and not request.image_base64:
            return ImageAnalysisResult(
                labels=[],
                confidence_scores={},
                ocr_text="",
                faces_detected=0,
                objects=[],
                metadata={"error": "No image provided"}
            )
        
        # Placeholder para análisis avanzado (IA, OCR, detección de objetos, etc.)
        # Aquí podrías integrar modelos de IA, servicios de OCR, etc.
        return ImageAnalysisResult(
            labels=["example_label"],
            confidence_scores={"example_label": 0.99},
            ocr_text="Texto de ejemplo extraído por OCR",
            faces_detected=0,
            objects=[],
            metadata={"note": "Este es un resultado de ejemplo"}
        ) 