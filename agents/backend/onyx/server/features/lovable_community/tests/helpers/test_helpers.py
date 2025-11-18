"""
Helpers generales para tests de Lovable Community
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional


def generate_chat_id() -> str:
    """Genera un ID de chat único"""
    return str(uuid.uuid4())


def generate_user_id() -> str:
    """Genera un ID de usuario único"""
    return f"user-{uuid.uuid4().hex[:8]}"


def create_chat_dict(
    chat_id: Optional[str] = None,
    user_id: Optional[str] = None,
    title: str = "Test Chat",
    description: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Crea un diccionario de chat para testing"""
    return {
        "id": chat_id or generate_chat_id(),
        "user_id": user_id or generate_user_id(),
        "title": title,
        "description": description or "Test description",
        "chat_content": kwargs.get("chat_content", '{"messages": []}'),
        "tags": kwargs.get("tags", ["test"]),
        "vote_count": kwargs.get("vote_count", 0),
        "remix_count": kwargs.get("remix_count", 0),
        "view_count": kwargs.get("view_count", 0),
        "score": kwargs.get("score", 0.0),
        "is_public": kwargs.get("is_public", True),
        "is_featured": kwargs.get("is_featured", False),
        "created_at": kwargs.get("created_at", datetime.utcnow()),
        "updated_at": kwargs.get("updated_at", datetime.utcnow()),
        **kwargs
    }


def create_publish_request(
    title: str = "Test Chat",
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Crea un request de publicación para testing"""
    return {
        "title": title,
        "description": description or "Test description",
        "chat_content": kwargs.get("chat_content", '{"messages": []}'),
        "tags": tags or ["test"],
        "is_public": kwargs.get("is_public", True),
        **kwargs
    }


def create_remix_request(
    original_chat_id: str,
    title: str = "Remix: Test Chat",
    **kwargs
) -> Dict[str, Any]:
    """Crea un request de remix para testing"""
    return {
        "original_chat_id": original_chat_id,
        "title": title,
        "description": kwargs.get("description", "Remix description"),
        "chat_content": kwargs.get("chat_content", '{"messages": []}'),
        "tags": kwargs.get("tags", ["remix", "test"]),
        **kwargs
    }


def create_vote_request(
    chat_id: str,
    vote_type: str = "upvote"
) -> Dict[str, Any]:
    """Crea un request de voto para testing"""
    return {
        "chat_id": chat_id,
        "vote_type": vote_type
    }


def create_search_request(
    query: Optional[str] = None,
    tags: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Crea un request de búsqueda para testing"""
    return {
        "query": query,
        "tags": tags,
        "user_id": kwargs.get("user_id"),
        "sort_by": kwargs.get("sort_by", "score"),
        "order": kwargs.get("order", "desc"),
        "page": kwargs.get("page", 1),
        "page_size": kwargs.get("page_size", 20),
        **kwargs
    }

