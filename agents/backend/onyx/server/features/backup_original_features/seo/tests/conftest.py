import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from agents.backend.onyx.server.features.seo.api import router as seo_router

@pytest.fixture(scope="module")
def client():
    app = FastAPI()
    app.include_router(seo_router)
    with TestClient(app) as c:
        yield c 