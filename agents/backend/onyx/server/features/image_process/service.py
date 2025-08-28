from __future__ import annotations

from typing import Any

from . import extract, image_summary, validation
from .models import (
    ImageExtractRequest,
    ImageExtractResponse,
    ImageSummaryRequest,
    ImageSummaryResponse,
    ImageValidationRequest,
    ImageValidationResponse,
    ImageAnalysisResult,
)


class ImageProcessService:
    """Central service for image extraction, summary, validation, and analysis.

    This version keeps simple guard clauses and delegates to small modules
    to make unit testing straightforward and predictable.
    """

    @staticmethod
    def extract_text(request: ImageExtractRequest) -> ImageExtractResponse:
        if request is None:
            return ImageExtractResponse(success=False, error="Request cannot be null")

        if not request.image_url and not request.image_base64:
            return ImageExtractResponse(success=False, error="No image provided")

        if request.image_url is not None and not request.image_url.strip():
            return ImageExtractResponse(success=False, error="Image URL cannot be empty")

        if request.image_base64 is not None and not request.image_base64.strip():
            return ImageExtractResponse(success=False, error="Base64 image cannot be empty")

        try:
            if request.image_url:
                text = extract.extract_text_from_url(request.image_url, **(request.options or {}))
            else:
                text = extract.extract_text_from_base64(request.image_base64 or "", **(request.options or {}))
            return ImageExtractResponse(success=True, extracted_text=text)
        except Exception as exc:  # pragma: no cover - defensive
            return ImageExtractResponse(success=False, error=str(exc))

    @staticmethod
    def summarize(request: ImageSummaryRequest) -> ImageSummaryResponse:
        if request is None:
            return ImageSummaryResponse(success=False, error="Request cannot be null")

        if not request.image_url and not request.image_base64:
            return ImageSummaryResponse(success=False, error="No image provided")

        if request.image_url is not None and not request.image_url.strip():
            return ImageSummaryResponse(success=False, error="Image URL cannot be empty")

        if request.image_base64 is not None and not request.image_base64.strip():
            return ImageSummaryResponse(success=False, error="Base64 image cannot be empty")

        try:
            if request.image_url:
                summary = image_summary.summarize_image_url(request.image_url, summary_type=request.summary_type or "simple")
            else:
                summary = image_summary.summarize_image_base64(request.image_base64 or "", summary_type=request.summary_type or "simple")
            return ImageSummaryResponse(success=True, summary=summary)
        except Exception as exc:  # pragma: no cover - defensive
            return ImageSummaryResponse(success=False, error=str(exc))

    @staticmethod
    def validate(request: ImageValidationRequest) -> ImageValidationResponse:
        if request is None:
            return ImageValidationResponse(success=False, error="Request cannot be null")

        if not request.image_url and not request.image_base64:
            return ImageValidationResponse(success=False, error="No image provided")

        if request.image_url is not None and not request.image_url.strip():
            return ImageValidationResponse(success=False, error="Image URL cannot be empty")

        if request.image_base64 is not None and not request.image_base64.strip():
            return ImageValidationResponse(success=False, error="Base64 image cannot be empty")

        try:
            if request.image_url:
                is_valid, details = validation.validate_image_url(
                    request.image_url, validation_type=request.validation_type or "default"
                )
            else:
                is_valid, details = validation.validate_image_base64(
                    request.image_base64 or "", validation_type=request.validation_type or "default"
                )
            return ImageValidationResponse(success=True, is_valid=is_valid, details=details)
        except Exception as exc:  # pragma: no cover - defensive
            return ImageValidationResponse(success=False, error=str(exc))

    @staticmethod
    def analyze(request: ImageExtractRequest) -> ImageAnalysisResult:
        if request is None:
            return ImageAnalysisResult(
                labels=[], confidence_scores={}, ocr_text="", faces_detected=0, objects=[],
                metadata={"error": "Request cannot be null"},
            )

        if not request.image_url and not request.image_base64:
            return ImageAnalysisResult(
                labels=[], confidence_scores={}, ocr_text="", faces_detected=0, objects=[],
                metadata={"error": "No image provided"},
            )

        return ImageAnalysisResult(
            labels=["example_label"],
            confidence_scores={"example_label": 0.99},
            ocr_text="Texto de ejemplo extraído por OCR",
            faces_detected=0,
            objects=[],
            metadata={"note": "Este es un resultado de ejemplo"},
        )