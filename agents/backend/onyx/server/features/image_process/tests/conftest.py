import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from agents.backend.onyx.server.features.image_process.api import router as image_process_router

@pytest.fixture(scope="module")
def client():
    app = FastAPI()
    app.include_router(image_process_router, prefix="/api/image_process")
    with TestClient(app) as c:
        yield c 