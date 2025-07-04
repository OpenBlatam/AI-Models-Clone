"""
Presentation Schemas - LinkedIn Posts
====================================

This module contains all API schemas for the LinkedIn Posts system.
Schemas define the structure of API requests and responses.
"""

from .linkedin_post_schemas import (
    LinkedInPostCreateRequest,
    LinkedInPostUpdateRequest,
    LinkedInPostResponse,
    LinkedInPostListResponse,
    LinkedInPostGenerateRequest,
    LinkedInPostGenerateResponse,
    LinkedInPostOptimizeRequest,
    LinkedInPostOptimizeResponse,
    LinkedInPostAnalyzeRequest,
    LinkedInPostAnalyzeResponse,
    LinkedInPostABTestRequest,
    LinkedInPostABTestResponse,
)

__all__ = [
    "LinkedInPostCreateRequest",
    "LinkedInPostUpdateRequest", 
    "LinkedInPostResponse",
    "LinkedInPostListResponse",
    "LinkedInPostGenerateRequest",
    "LinkedInPostGenerateResponse",
    "LinkedInPostOptimizeRequest",
    "LinkedInPostOptimizeResponse",
    "LinkedInPostAnalyzeRequest",
    "LinkedInPostAnalyzeResponse",
    "LinkedInPostABTestRequest",
    "LinkedInPostABTestResponse",
] 