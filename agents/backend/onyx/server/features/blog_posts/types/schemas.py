from pydantic import BaseModel, Field, validator
import logging

logger = logging.getLogger("blog_posts.schemas")

class InvalidTargetError(Exception):
    """Raised when a target address is invalid."""
    def __init__(self, target: str):
        self.target = target
        self.message = f"Invalid target address: {target}"
        super().__init__(self.message)

class TimeoutError(Exception):
    """Raised when an operation times out."""
    pass

class BlogPostIn(BaseModel):
    title: str = Field(..., max_length=256)
    content: str
    target: str = Field(..., description="Target address for demonstration.")

    @validator("title")
    def validate_title(cls, v):
        if not v or not v.strip():
            logger.warning({
                "module": "schemas",
                "function": "validate_title",
                "parameter": v,
                "error": "Title is empty or whitespace."
            })
            raise ValueError("Title is required and cannot be empty.")
        return v

    @validator("content")
    def validate_content(cls, v):
        if not v or not v.strip():
            logger.warning({
                "module": "schemas",
                "function": "validate_content",
                "parameter": v,
                "error": "Content is empty or whitespace."
            })
            raise ValueError("Content is required and cannot be empty.")
        return v

    @validator("target")
    def validate_target(cls, v):
        if not v or not v.startswith("http"):
            logger.error({
                "module": "schemas",
                "function": "validate_target",
                "parameter": v,
                "error": "Malformed target address."
            })
            raise InvalidTargetError(v)
        return v 