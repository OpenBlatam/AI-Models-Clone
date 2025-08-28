from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class MaxBodySizeMiddleware(BaseHTTPMiddleware):
    """Abort requests whose Content-Length exceeds max_bytes with 413."""

    def __init__(self, app, max_bytes: int):
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next):
        size_hdr = request.headers.get("content-length")
        if size_hdr:
            try:
                size = int(size_hdr)
                if size > self.max_bytes:
                    return Response("payload_too_large", status_code=413)
            except Exception:
                pass
        return await call_next(request)


