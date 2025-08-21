from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from onyx.server.features.ads.api import router as ads_router

from typing import Any, List, Dict, Optional
import logging
import asyncio
@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(ads_router)
    return TestClient(app)

@pytest.mark.asyncio
def test_generate_ads_success(client) -> Any:
    # Prepare a valid AdsGenerationRequest payload
    payload = {
        "url": "https://example.com",
        "prompt": "Write an ad for our new product.",
        "type": "ads",
        "user_id": "user-123",
        "brand_voice": {"tone": "friendly"},
        "audience_profile": {"age": "25-34"},
        "project_context": {"campaign": "launch"},
        "advanced": False,
        "use_langchain": False,
        "model_config": {
            "model_name": "onyx-ads-v1",
            "temperature": 0.7,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "max_tokens": 1000,
            "stop_sequences": [],
            "custom_parameters": {}
        }
    }

    response = client.post("/ads/core/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"
    assert "data" in data
    assert "timestamp" in data