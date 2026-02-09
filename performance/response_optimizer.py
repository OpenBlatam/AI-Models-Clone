"""
Ultra-Fast Response Optimizer
Optimized FastAPI response handling for maximum speed
"""

import logging
from typing import Any, Dict, Optional
from fastapi.responses import Response, JSONResponse
from starlette.responses import Response as StarletteResponse

from .serialization_optimizer import get_serializer

logger = logging.getLogger(__name__)


class FastJSONResponse(JSONResponse):
    """Ultra-fast JSON response using optimized serialization"""
    
    def __init__(self, content: Any, **kwargs):
        serializer = get_serializer()
        # Use orjson for fast serialization
        if hasattr(serializer, 'dumps_str'):
            # Convert to string for JSONResponse
            if isinstance(content, (dict, list)):
                json_str = serializer.dumps_str(content)
                super().__init__(content=json_str, **kwargs)
            else:
                super().__init__(content=content, **kwargs)
        else:
            super().__init__(content=content, **kwargs)


class ResponseOptimizer:
    """
    Ultra-fast response optimizer
    
    Features:
    - Fast JSON serialization
    - Response compression hints
    - Cache headers optimization
    - Streaming responses
    """
    
    def __init__(self):
        self.serializer = get_serializer()
        logger.info("✅ Response optimizer initialized")
    
    def create_json_response(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        fast: bool = True
    ) -> Response:
        """
        Create optimized JSON response
        
        Args:
            content: Response content
            status_code: HTTP status code
            headers: Additional headers
            fast: Use fast serialization
            
        Returns:
            Optimized JSON response
        """
        if fast and isinstance(content, (dict, list)):
            # Use fast JSON response
            response = FastJSONResponse(content=content, status_code=status_code)
        else:
            response = JSONResponse(content=content, status_code=status_code)
        
        # Add performance headers
        if headers:
            for key, value in headers.items():
                response.headers[key] = value
        
        # Add cache hints
        response.headers["X-Response-Optimized"] = "true"
        
        return response
    
    def optimize_headers(self, response: Response, cache_ttl: int = 300) -> Response:
        """
        Optimize response headers for performance
        
        Args:
            response: Response to optimize
            cache_ttl: Cache TTL in seconds
            
        Returns:
            Response with optimized headers
        """
        # Add cache headers for GET requests
        if hasattr(response, 'status_code') and response.status_code == 200:
            response.headers["Cache-Control"] = f"public, max-age={cache_ttl}"
            response.headers["X-Content-Type-Options"] = "nosniff"
        
        return response


# Global optimizer instance
_optimizer: Optional[ResponseOptimizer] = None


def get_response_optimizer() -> ResponseOptimizer:
    """Get global response optimizer instance"""
    global _optimizer
    if _optimizer is None:
        _optimizer = ResponseOptimizer()
    return _optimizer















