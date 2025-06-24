import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from agents.backend.onyx.server.features.copywriting.api import router as copywriting_router

@pytest.fixture(scope="module")
def client():
    app = FastAPI()
    app.include_router(copywriting_router)
    with TestClient(app) as c:
        yield c 