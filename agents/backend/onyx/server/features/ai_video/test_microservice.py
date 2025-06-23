import pytest
from fastapi.testclient import TestClient
from fastapi_microservice import app

client = TestClient(app)

TOKEN = "supersecrettoken"

@pytest.fixture
def auth_header():
    return {"Authorization": f"Bearer {TOKEN}"}

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_video_post(auth_header, monkeypatch):
    # Mock Celery task to avoid real async processing
    from fastapi_microservice import process_video_task
    monkeypatch.setattr(process_video_task, "delay", lambda *a, **kw: None)
    payload = {"input_text": "test video", "user_id": "user1"}
    resp = client.post("/v1/video", json=payload, headers=auth_header)
    assert resp.status_code == 202
    data = resp.json()
    assert data["status"] == "processing"
    assert data["request_id"].startswith("req_")

def test_video_post_unauthorized():
    payload = {"input_text": "test video", "user_id": "user1"}
    resp = client.post("/v1/video", json=payload)
    assert resp.status_code == 401

def test_metrics():
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "http_requests_total" in resp.text 