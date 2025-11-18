"""
Chat Repository

Repository for PublishedChat model with specialized queries.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_, func, desc, asc

from ..models import PublishedChat
from .base import BaseRepository
from .optimizations import QueryOptimizer
from .query_helpers import apply_ordering


class ChatRepository(BaseRepository[PublishedChat]):
    """
    Repository for PublishedChat with specialized query methods.
    """
    
    def __init__(self, db: Session):
        super().__init__(db, PublishedChat)
    
    def get_by_user_id(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        is_public: Optional[bool] = None
    ) -> List[PublishedChat]:
        """
        Get chats by user ID.
        
        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records
            is_public: Filter by public status (optional)
            
        Returns:
            List of chats
        """
        query = self.db.query(PublishedChat).filter(
            PublishedChat.user_id == user_id
        )
        
        if is_public is not None:
            query = query.filter(PublishedChat.is_public == is_public)
        
        query = apply_ordering(query, "created_at", "desc", PublishedChat)
        return query.offset(skip).limit(limit).all()
    
    def get_public_chats(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "score",
        order: str = "desc"
    ) -> List[PublishedChat]:
        """
        Get public chats with sorting (optimized).
        
        Uses optimized query with proper indexing.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            sort_by: Field to sort by
            order: Sort order (asc/desc)
            
        Returns:
            List of public chats
        """
        # Use optimized batch query
        chats, _ = QueryOptimizer.get_chats_batch_optimized(
            self.db,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        return chats
    
    def get_featured_chats(self, limit: int = 10) -> List[PublishedChat]:
        """
        Get featured chats.
        
        Args:
            limit: Maximum number of featured chats
            
        Returns:
            List of featured chats
        """
        query = self.db.query(PublishedChat).filter(
            PublishedChat.is_featured == True,
            PublishedChat.is_public == True
        )
        query = apply_ordering(query, "score", "desc", PublishedChat)
        return query.limit(limit).all()
    
    def search_by_query(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[PublishedChat]:
        """
        Search chats by query string.
        
        Args:
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of matching chats
        """
        search_term = f"%{query.lower()}%"
        query_obj = self.db.query(PublishedChat).filter(
            PublishedChat.is_public == True,
            or_(
                PublishedChat.title.ilike(search_term),
                PublishedChat.description.ilike(search_term),
                PublishedChat.tags.ilike(search_term)
            )
        )
        query_obj = apply_ordering(query_obj, "score", "desc", PublishedChat)
        return query_obj.offset(skip).limit(limit).all()
    
    def get_by_tags(
        self,
        tags: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> List[PublishedChat]:
        """
        Get chats by tags.
        
        Args:
            tags: List of tags
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of matching chats
        """
        query = self.db.query(PublishedChat).filter(
            PublishedChat.is_public == True
        )
        
        tag_filters = []
        for tag in tags:
            tag_filters.append(PublishedChat.tags.ilike(f"%{tag}%"))
        
        if tag_filters:
            query = query.filter(or_(*tag_filters))
        
        query = apply_ordering(query, "score", "desc", PublishedChat)
        return query.offset(skip).limit(limit).all()
    
    def get_trending(
        self,
        hours: int = 24,
        limit: int = 10
    ) -> List[PublishedChat]:
        """
        Get trending chats.
        
        Args:
            hours: Hours to look back
            limit: Maximum number of chats
            
        Returns:
            List of trending chats
        """
        from datetime import timedelta
        from ..helpers import get_current_timestamp
        
        cutoff_time = get_current_timestamp() - timedelta(hours=hours)
        
        query = self.db.query(PublishedChat).filter(
            PublishedChat.is_public == True,
            PublishedChat.created_at >= cutoff_time
        )
        query = apply_ordering(query, "score", "desc", PublishedChat)
        return query.limit(limit).all()
    
    def increment_vote_count(self, chat_id: str, increment: int = 1) -> bool:
        """
        Increment vote count for a chat.
        
        Args:
            chat_id: Chat ID
            increment: Amount to increment (can be negative)
            
        Returns:
            True if updated, False if not found
        """
        chat = self.get_by_id(chat_id)
        if not chat:
            return False
        
        chat.vote_count = max(0, chat.vote_count + increment)
        self.db.commit()
        return True
    
    def increment_remix_count(self, chat_id: str) -> bool:
        """
        Increment remix count for a chat.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            True if updated, False if not found
        """
        chat = self.get_by_id(chat_id)
        if not chat:
            return False
        
        chat.remix_count += 1
        self.db.commit()
        return True
    
    def increment_view_count(self, chat_id: str) -> bool:
        """
        Increment view count for a chat.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            True if updated, False if not found
        """
        chat = self.get_by_id(chat_id)
        if not chat:
            return False
        
        chat.view_count += 1
        self.db.commit()
        return True
    
    def update_score(self, chat_id: str, score: float) -> bool:
        """
        Update score for a chat.
        
        Args:
            chat_id: Chat ID
            score: New score
            
        Returns:
            True if updated, False if not found
        """
        chat = self.get_by_id(chat_id)
        if not chat:
            return False
        
        chat.score = score
        self.db.commit()
        return True
    
    def increment_view_count_and_score(
        self,
        chat_id: str,
        score: float
    ) -> bool:
        """
        Increment view count and update score in a single operation.
        
        Args:
            chat_id: Chat ID
            score: New score to set
            
        Returns:
            True if updated, False if not found
        """
        chat = self.get_by_id(chat_id)
        if not chat:
            return False
        
        chat.view_count += 1
        chat.score = score
        self.db.commit()
        return True
    
    def increment_vote_count_and_score(
        self,
        chat_id: str,
        vote_increment: int,
        score: float
    ) -> bool:
        """
        Increment vote count and update score in a single operation.
        
        Args:
            chat_id: Chat ID
            vote_increment: Amount to increment vote count (can be negative)
            score: New score to set
            
        Returns:
            True if updated, False if not found
        """
        chat = self.get_by_id(chat_id)
        if not chat:
            return False
        
        chat.vote_count = max(0, chat.vote_count + vote_increment)
        chat.score = score
        self.db.commit()
        return True
    
    def increment_remix_count_and_score(
        self,
        chat_id: str,
        score: float
    ) -> bool:
        """
        Increment remix count and update score in a single operation.
        
        Args:
            chat_id: Chat ID
            score: New score to set
            
        Returns:
            True if updated, False if not found
        """
        chat = self.get_by_id(chat_id)
        if not chat:
            return False
        
        chat.remix_count += 1
        chat.score = score
        self.db.commit()
        return True
    
    def get_rank_by_score(self, score: float) -> int:
        """
        Get rank based on score (number of chats with higher score + 1).
        
        Args:
            score: Chat score
            
        Returns:
            Rank (1-based)
        """
        from sqlalchemy import func
        rank = self.db.query(
            func.count(PublishedChat.id)
        ).filter(
            PublishedChat.score > score,
            PublishedChat.is_public == True
        ).scalar() + 1
        
        return rank
    
    def _build_search_query(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        user_id: Optional[str] = None
    ):
        """
        Build base search query with filters.
        
        Args:
            query: Search query string
            tags: Filter by tags
            user_id: Filter by user ID
            
        Returns:
            SQLAlchemy query object
        """
        from sqlalchemy import or_
        
        db_query = self.db.query(PublishedChat).filter(
            PublishedChat.is_public == True
        )
        
        if query and query.strip():
            search_term = f"%{query.strip().lower()}%"
            db_query = db_query.filter(
                or_(
                    PublishedChat.title.ilike(search_term),
                    PublishedChat.description.ilike(search_term),
                    PublishedChat.tags.ilike(search_term)
                )
            )
        elif tags:
            tag_filters = [PublishedChat.tags.ilike(f"%{tag}%") for tag in tags if tag]
            if tag_filters:
                db_query = db_query.filter(or_(*tag_filters))
        elif user_id:
            db_query = db_query.filter(PublishedChat.user_id == user_id)
        
        return db_query
    
    def count_search_results(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        user_id: Optional[str] = None
    ) -> int:
        """
        Count search results for accurate pagination.
        
        Args:
            query: Search query string
            tags: Filter by tags
            user_id: Filter by user ID
            
        Returns:
            Total count of matching chats
        """
        return self._build_search_query(query, tags, user_id).count()

