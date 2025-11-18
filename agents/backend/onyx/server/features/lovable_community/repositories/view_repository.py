"""
View Repository

Repository for ChatView model with specialized queries.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import timedelta

from ..models import ChatView
from ..helpers import get_current_timestamp
from .base import BaseRepository


class ViewRepository(BaseRepository[ChatView]):
    """
    Repository for ChatView with specialized query methods.
    """
    
    def __init__(self, db: Session):
        super().__init__(db, ChatView)
    
    def get_by_chat_id(self, chat_id: str) -> List[ChatView]:
        """
        Get all views for a chat.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            List of views
        """
        return self.db.query(ChatView).filter(
            ChatView.chat_id == chat_id
        ).order_by(desc(ChatView.created_at)).all()
    
    def count_by_chat_id(self, chat_id: str) -> int:
        """
        Count views for a chat.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Count of views
        """
        return self.db.query(ChatView).filter(
            ChatView.chat_id == chat_id
        ).count()
    
    def get_recent_views(
        self,
        chat_id: str,
        hours: int = 24
    ) -> List[ChatView]:
        """
        Get recent views for a chat.
        
        Args:
            chat_id: Chat ID
            hours: Hours to look back
            
        Returns:
            List of recent views
        """
        cutoff_time = get_current_timestamp() - timedelta(hours=hours)
        
        return self.db.query(ChatView).filter(
            ChatView.chat_id == chat_id,
            ChatView.created_at >= cutoff_time
        ).order_by(desc(ChatView.created_at)).all()
    
    def has_user_viewed(self, chat_id: str, user_id: Optional[str]) -> bool:
        """
        Check if user has viewed a chat.
        
        Args:
            chat_id: Chat ID
            user_id: User ID (optional)
            
        Returns:
            True if user has viewed, False otherwise
        """
        if not user_id:
            return False
        
        return self.db.query(ChatView).filter(
            ChatView.chat_id == chat_id,
            ChatView.user_id == user_id
        ).first() is not None
    
    def delete_by_chat_id(self, chat_id: str) -> int:
        """
        Delete all views for a chat in a single query.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Number of deleted views
        """
        deleted_count = self.db.query(ChatView).filter(
            ChatView.chat_id == chat_id
        ).delete(synchronize_session=False)
        self.db.commit()
        return deleted_count


