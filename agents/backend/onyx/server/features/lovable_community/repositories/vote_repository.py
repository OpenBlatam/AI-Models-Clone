"""
Vote Repository

Repository for ChatVote model with specialized queries.
"""

from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models import ChatVote
from .base import BaseRepository


class VoteRepository(BaseRepository[ChatVote]):
    """
    Repository for ChatVote with specialized query methods.
    """
    
    def __init__(self, db: Session):
        super().__init__(db, ChatVote)
    
    def get_by_chat_id(self, chat_id: str) -> List[ChatVote]:
        """
        Get all votes for a chat.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            List of votes
        """
        return self.db.query(ChatVote).filter(
            ChatVote.chat_id == chat_id
        ).order_by(desc(ChatVote.created_at)).all()
    
    def get_by_user_id(self, user_id: str, limit: int = 100) -> List[ChatVote]:
        """
        Get votes by user ID.
        
        Args:
            user_id: User ID
            limit: Maximum number of votes
            
        Returns:
            List of votes
        """
        return self.db.query(ChatVote).filter(
            ChatVote.user_id == user_id
        ).order_by(desc(ChatVote.created_at)).limit(limit).all()
    
    def get_user_vote(self, chat_id: str, user_id: str) -> Optional[ChatVote]:
        """
        Get user's vote for a specific chat.
        
        Args:
            chat_id: Chat ID
            user_id: User ID
            
        Returns:
            Vote or None if not found
        """
        return self.db.query(ChatVote).filter(
            ChatVote.chat_id == chat_id,
            ChatVote.user_id == user_id
        ).first()
    
    def count_by_chat_id(self, chat_id: str, vote_type: Optional[str] = None) -> int:
        """
        Count votes for a chat.
        
        Args:
            chat_id: Chat ID
            vote_type: Filter by vote type (optional)
            
        Returns:
            Count of votes
        """
        query = self.db.query(ChatVote).filter(ChatVote.chat_id == chat_id)
        
        if vote_type:
            query = query.filter(ChatVote.vote_type == vote_type)
        
        return query.count()
    
    def get_user_votes_batch(
        self,
        chat_ids: List[str],
        user_id: str
    ) -> Dict[str, ChatVote]:
        """
        Get user's votes for multiple chats in a single query.
        
        Args:
            chat_ids: List of chat IDs
            user_id: User ID
            
        Returns:
            Dictionary mapping chat_id to ChatVote
        """
        if not chat_ids:
            return {}
        
        votes = self.db.query(ChatVote).filter(
            ChatVote.chat_id.in_(chat_ids),
            ChatVote.user_id == user_id
        ).all()
        
        return {vote.chat_id: vote for vote in votes}
    
    def delete_by_chat_id(self, chat_id: str) -> int:
        """
        Delete all votes for a chat in a single query.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Number of deleted votes
        """
        deleted_count = self.db.query(ChatVote).filter(
            ChatVote.chat_id == chat_id
        ).delete(synchronize_session=False)
        self.db.commit()
        return deleted_count


