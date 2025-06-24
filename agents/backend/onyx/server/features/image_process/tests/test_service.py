"""
Unit tests for ImageProcessService.
"""
import pytest
from agents.backend.onyx.server.features.image_process.models import (
    ImageExtractRequest, ImageSummaryRequest, ImageValidationRequest
)
from agents.backend.onyx.server.features.image_process.service import ImageProcessService
from pydantic import ValidationError

class TestImageProcessService:
    def setup_method(self):
        self.service = ImageProcessService()

    def test_extract_text_url(self):
        req = ImageExtractRequest(image_url="https://test.com/img.jpg")
        resp = self.service.extract_text(req)
        assert resp.success
        assert "Texto extraído" in resp.extracted_text

    def test_extract_text_base64(self):
        req = ImageExtractRequest(image_base64="dGVzdA==")
        resp = self.service.extract_text(req)
        assert resp.success
        assert "base64" in resp.extracted_text

    def test_extract_text_no_image(self):
        with pytest.raises(ValidationError):
            req = ImageExtractRequest()

    def test_summarize_url(self):
        req = ImageSummaryRequest(image_url="https://test.com/img.jpg", summary_type="simple")
        resp = self.service.summarize(req)
        assert resp.success
        assert "Resumen" in resp.summary

    def test_summarize_base64(self):
        req = ImageSummaryRequest(image_base64="dGVzdA==", summary_type="simple")
        resp = self.service.summarize(req)
        assert resp.success
        assert "base64" in resp.summary

    def test_summarize_no_image(self):
        with pytest.raises(ValidationError):
            req = ImageSummaryRequest()

    def test_validate_url(self):
        req = ImageValidationRequest(image_url="https://test.com/img.jpg", validation_type="default")
        resp = self.service.validate(req)
        assert resp.success
        assert resp.is_valid is True
        assert resp.details["source"] == "https://test.com/img.jpg"

    def test_validate_base64(self):
        req = ImageValidationRequest(image_base64="dGVzdA==", validation_type="default")
        resp = self.service.validate(req)
        assert resp.success
        assert resp.is_valid is True
        assert resp.details["source"] == "base64"

    def test_validate_no_image(self):
        with pytest.raises(ValidationError):
            req = ImageValidationRequest() 