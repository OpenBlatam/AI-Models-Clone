"""
Chat validation utilities

Extracted validation logic for chat operations.
"""

from typing import Optional, List
from ....exceptions import InvalidChatError


class ChatValidator:
    """Validation utilities for chat operations."""
    
    @staticmethod
    def validate_chat_id(chat_id: str) -> str:
        """Validate and normalize chat ID."""
        if not chat_id or not chat_id.strip():
            raise InvalidChatError("Chat ID cannot be empty")
        return chat_id.strip()
    
    @staticmethod
    def validate_user_id(user_id: str) -> str:
        """Validate and normalize user ID."""
        if not user_id or not user_id.strip():
            raise InvalidChatError("User ID cannot be empty")
        return user_id.strip()
    
    @staticmethod
    def validate_title(title: str) -> str:
        """Validate and normalize title."""
        if not title or not title.strip():
            raise InvalidChatError("Title cannot be empty")
        return title.strip()
    
    @staticmethod
    def validate_chat_content(chat_content: str) -> str:
        """Validate and normalize chat content."""
        if not chat_content or not chat_content.strip():
            raise InvalidChatError("Chat content cannot be empty")
        return chat_content.strip()
    
    @staticmethod
    def process_tags(tags: Optional[List[str]]) -> Optional[str]:
        """Process and format tags list to string."""
        if not tags:
            return None
        
        valid_tags = {tag.strip().lower() for tag in tags if tag and tag.strip()}
        return ",".join(list(valid_tags)[:10]) if valid_tags else None
    
    @staticmethod
    def ensure_ownership(chat, user_id: str) -> None:
        """Ensure user owns the chat."""
        if chat.user_id != user_id:
            raise InvalidChatError("User is not the owner of this chat")






