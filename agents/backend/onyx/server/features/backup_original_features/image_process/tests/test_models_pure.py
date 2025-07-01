import pytest
from pydantic import ValidationError
from agents.backend.onyx.server.features.image_process.models import (
    ImageBaseRequest,
    ImageExtractRequest,
    ImageExtractResponse,
    ImageSummaryRequest,
    ImageSummaryResponse,
    ImageValidationRequest,
    ImageValidationResponse,
    ImageAnalysisResult
)

def test_image_base_request_valid_url():
    req = ImageBaseRequest(image_url="https://example.com/img.jpg")
    assert req.image_url == "https://example.com/img.jpg"
    assert req.image_base64 is None

def test_image_base_request_valid_base64():
    req = ImageBaseRequest(image_base64="iVBORw0KGgoAAAANSUhEUgAA...")
    assert req.image_base64.startswith("iVBORw0KGgo")
    assert req.image_url is None

def test_image_base_request_invalid():
    with pytest.raises(ValidationError):
        ImageBaseRequest()

def test_image_extract_request_options():
    req = ImageExtractRequest(image_url="url", options={"ocr": True})
    assert req.options["ocr"] is True

def test_image_extract_response_success():
    resp = ImageExtractResponse(success=True, extracted_text="Texto", metadata={"ocr_confidence": 0.99})
    assert resp.success is True
    assert resp.extracted_text == "Texto"
    assert resp.metadata["ocr_confidence"] == 0.99

def test_image_summary_request_type():
    req = ImageSummaryRequest(image_url="url", summary_type="avanzado")
    assert req.summary_type == "avanzado"

def test_image_summary_response_error():
    resp = ImageSummaryResponse(success=False, error="Error")
    assert resp.success is False
    assert resp.error == "Error"

def test_image_validation_request_type():
    req = ImageValidationRequest(image_url="url", validation_type="custom")
    assert req.validation_type == "custom"

def test_image_validation_response_details():
    resp = ImageValidationResponse(success=True, is_valid=True, details={"format": "jpg"})
    assert resp.is_valid is True
    assert resp.details["format"] == "jpg"

def test_image_analysis_result_full():
    result = ImageAnalysisResult(
        labels=["persona", "auto"],
        confidence_scores={"persona": 0.98, "auto": 0.85},
        ocr_text="Texto OCR",
        faces_detected=2,
        objects=[{"type": "auto", "confidence": 0.85}],
        metadata={"procesado_por": "modelo-v1"}
    )
    assert result.labels == ["persona", "auto"]
    assert result.confidence_scores["persona"] == 0.98
    assert result.ocr_text == "Texto OCR"
    assert result.faces_detected == 2
    assert result.objects[0]["type"] == "auto"
    assert result.metadata["procesado_por"] == "modelo-v1"
