from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from fastapi import APIRouter
from fastapi import Response

from model_server.constants import GPUStatus
from model_server.utils import get_gpu_type

from typing import Any, List, Dict, Optional
import logging
import asyncio
router = APIRouter(prefix="/api")


@router.get("/health")
async def healthcheck() -> Response:
    return Response(status_code=200)


@router.get("/gpu-status")
async def route_gpu_status() -> dict[str, bool | str]:
    gpu_type = get_gpu_type()
    gpu_available = gpu_type != GPUStatus.NONE
    return {"gpu_available": gpu_available, "type": gpu_type}
