"""
Repository Factory

Factory for creating repository instances with dependency injection.
"""

from typing import Optional
from sqlalchemy.orm import Session

from ..repositories import (
    ChatRepository,
    RemixRepository,
    VoteRepository,
    ViewRepository,
)


class RepositoryFactory:
    """
    Factory for creating repository instances.
    
    Implements Factory Pattern for repository creation.
    """
    
    def __init__(self, db: Session):
        """
        Initialize factory with database session.
        
        Args:
            db: Database session
        """
        self.db = db
        self._chat_repository: Optional[ChatRepository] = None
        self._remix_repository: Optional[RemixRepository] = None
        self._vote_repository: Optional[VoteRepository] = None
        self._view_repository: Optional[ViewRepository] = None
    
    def get_chat_repository(self) -> ChatRepository:
        """
        Get or create chat repository (singleton per factory instance).
        
        Returns:
            ChatRepository instance
        """
        if self._chat_repository is None:
            self._chat_repository = ChatRepository(self.db)
        return self._chat_repository
    
    def get_remix_repository(self) -> RemixRepository:
        """
        Get or create remix repository (singleton per factory instance).
        
        Returns:
            RemixRepository instance
        """
        if self._remix_repository is None:
            self._remix_repository = RemixRepository(self.db)
        return self._remix_repository
    
    def get_vote_repository(self) -> VoteRepository:
        """
        Get or create vote repository (singleton per factory instance).
        
        Returns:
            VoteRepository instance
        """
        if self._vote_repository is None:
            self._vote_repository = VoteRepository(self.db)
        return self._vote_repository
    
    def get_view_repository(self) -> ViewRepository:
        """
        Get or create view repository (singleton per factory instance).
        
        Returns:
            ViewRepository instance
        """
        if self._view_repository is None:
            self._view_repository = ViewRepository(self.db)
        return self._view_repository








