from fastapi import FastAPI
from .api import router
from .middleware_limit import MaxBodySizeMiddleware
from PIL import Image


def register_image_process(app: FastAPI, max_request_bytes: int = 20_000_000, warmup: bool = False) -> None:
    """Register image_process feature in a FastAPI app.

    - Adds size limit middleware (413 on overflow)
    - Includes the feature router under /image-process
    """
    app.add_middleware(MaxBodySizeMiddleware, max_bytes=max_request_bytes)
    app.include_router(router)
    if warmup:
        try:
            # Priming Pillow decode/encode paths with a tiny image
            _ = Image.new("RGB", (32, 32), (127, 63, 31)).convert("RGBA")
        except Exception:
            pass


