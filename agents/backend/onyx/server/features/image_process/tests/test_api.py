from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
def test_analyze_image(client) -> Any:
    payload = {"image_url": "https://example.com/image.jpg"}
    response = client.post("/image-process/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["labels"] == ["example_label"]
    assert data["confidence_scores"]["example_label"] == 0.99
    assert data["ocr_text"] == "Texto de ejemplo extraído por OCR"
    assert data["faces_detected"] == 0
    assert data["objects"] == []
    assert "note" in data["metadata"]

def test_print_routes(client) -> Any:
    # Imprime todas las rutas disponibles en la app de test
    routes = [route.path for route in client.app.routes]
    print("RUTAS DISPONIBLES EN LA APP DE TEST:", routes)
    # Este test siempre pasa
    assert True 


def test_summary_multipart_empty_file(client) -> Any:
    files = {"file": ("empty.png", b"", "image/png")}
    data = {"mime_type": "image/png", "max_side_px": 128, "max_size_bytes": 1000000}
    r = client.post("/image-process/summary-multipart", files=files, data=data)
    assert r.status_code == 400
    assert r.json()["detail"] == "empty_file"


def test_summarize_batch_limit(client) -> Any:
    # Build a batch over the configured limit (default 32)
    payload = [{"image_base64": "dGVzdA==", "summary_type": "simple"} for _ in range(40)]
    r = client.post("/image-process/summarize-batch", json=payload)
    assert r.status_code == 400
    assert r.json()["detail"] == "batch_too_large"


def test_health_endpoint(client) -> Any:
    r = client.get("/image-process/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "max_workers" in data and isinstance(data["max_workers"], int)
    assert isinstance(data.get("allowed_mime", []), list)


def test_summary_multipart_content_type_mismatch(client) -> Any:
    files = {"file": ("x.png", b"123", "image/png")}
    data = {"mime_type": "image/jpeg", "max_side_px": 128, "max_size_bytes": 10_000_000}
    r = client.post("/image-process/summary-multipart", files=files, data=data)
    assert r.status_code == 400
    assert r.json()["detail"] == "content_type_mismatch"


def test_summary_multipart_declared_vs_actual_mime(client) -> Any:
    # A minimal valid PNG header (won't decode to full image but will trigger mismatch if declared jpeg)
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00IHDR" + b"0" * 80
    files = {"file": ("x.bin", png_bytes, "image/png")}
    data = {"mime_type": "image/jpeg", "max_side_px": 128, "max_size_bytes": 1000000}
    r = client.post("/image-process/summary-multipart", files=files, data=data)
    assert r.status_code in (400, 422)