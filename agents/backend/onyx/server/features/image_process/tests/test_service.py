from typing import Any
import pytest
from pydantic import ValidationError

from agents.backend.onyx.server.features.image_process.models import (
    ImageExtractRequest,
    ImageSummaryRequest,
    ImageValidationRequest,
)
from agents.backend.onyx.server.features.image_process.service import ImageProcessService

"""
Unit tests for ImageProcessService.
"""


class TestImageProcessService:
    def setup_method(self) -> Any:
        self.service = ImageProcessService()

    def test_extract_text_url(self) -> Any:
        req = ImageExtractRequest(image_url="https://test.com/img.jpg")
        resp = self.service.extract_text(req)
        assert resp.success
        assert "Texto extraído" in resp.extracted_text

    def test_extract_text_base64(self) -> Any:
        req = ImageExtractRequest(image_base64="dGVzdA==")
        resp = self.service.extract_text(req)
        assert resp.success
        assert "base64" in resp.extracted_text

    def test_extract_text_no_image(self) -> Any:
        with pytest.raises(ValidationError):
            ImageExtractRequest()

    def test_summarize_url(self) -> Any:
        req = ImageSummaryRequest(image_url="https://test.com/img.jpg", summary_type="simple")
        resp = self.service.summarize(req)
        assert resp.success
        assert "Resumen" in (resp.summary or "")

    def test_summarize_base64(self) -> Any:
        req = ImageSummaryRequest(image_base64="dGVzdA==", summary_type="simple")
        resp = self.service.summarize(req)
        assert resp.success
        assert "base64" in (resp.summary or "")

    def test_summarize_no_image(self) -> Any:
        with pytest.raises(ValidationError):
            ImageSummaryRequest()

    def test_validate_url(self) -> bool:
        req = ImageValidationRequest(image_url="https://test.com/img.jpg", validation_type="default")
        resp = self.service.validate(req)
        assert resp.success
        assert resp.is_valid is True
        assert resp.details["source"] == "https://test.com/img.jpg"

    def test_validate_base64(self) -> bool:
        req = ImageValidationRequest(image_base64="dGVzdA==", validation_type="default")
        resp = self.service.validate(req)
        assert resp.success
        assert resp.is_valid is True
        assert resp.details["source"] == "base64"

    def test_validate_no_image(self) -> bool:
        with pytest.raises(ValidationError):
            ImageValidationRequest()