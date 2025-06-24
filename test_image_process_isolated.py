from agents.backend.onyx.server.features.image_process.service import ImageProcessService
from agents.backend.onyx.server.features.image_process.models import (
    ImageExtractRequest, ImageSummaryRequest, ImageValidationRequest
)

def test_extract_text_url():
    service = ImageProcessService()
    req = ImageExtractRequest(image_url="https://test.com/img.jpg")
    resp = service.extract_text(req)
    assert resp.success
    assert "Texto extraído" in resp.extracted_text

def test_summarize_url():
    service = ImageProcessService()
    req = ImageSummaryRequest(image_url="https://test.com/img.jpg", summary_type="simple")
    resp = service.summarize(req)
    assert resp.success
    assert "Resumen" in resp.summary

def test_validate_url():
    service = ImageProcessService()
    req = ImageValidationRequest(image_url="https://test.com/img.jpg", validation_type="default")
    resp = service.validate(req)
    assert resp.success
    assert resp.is_valid is True
    assert resp.details["source"] == "https://test.com/img.jpg" 