from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from agents.backend.onyx.server.features.copywriting.api import router as copywriting_router

from typing import Any, List, Dict, Optional
import logging
import asyncio
@pytest.fixture(scope="module")
def client():
    
    """client function."""
app = FastAPI()
    app.include_router(copywriting_router)
    with TestClient(app) as c:
        yield c 