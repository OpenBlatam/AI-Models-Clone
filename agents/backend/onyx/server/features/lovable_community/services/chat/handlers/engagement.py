"""
Chat Engagement Operations

Handles engagement operations: votes, views, and remixes.
"""

import logging
from typing import Optional, Tuple
from ....models import PublishedChat, ChatVote, ChatRemix
from ....exceptions import InvalidChatError
from ....helpers import generate_id, get_current_timestamp

logger = logging.getLogger(__name__)


class VoteHandler:
    """Handles voting operations."""
    
    @staticmethod
    def calculate_vote_increment(
        existing_vote: Optional[ChatVote],
        new_vote_type: str
    ) -> Tuple[int, Optional[ChatVote]]:
        """
        Calculate vote increment.
        
        Args:
            existing_vote: Existing vote or None
            new_vote_type: New vote type ('upvote' or 'downvote')
            
        Returns:
            Tuple of (vote_increment, existing_vote_or_none)
        """
        if existing_vote:
            if existing_vote.vote_type == new_vote_type:
                return 0, existing_vote
            
            if existing_vote.vote_type == "upvote" and new_vote_type == "downvote":
                return -2, existing_vote
            elif existing_vote.vote_type == "downvote" and new_vote_type == "upvote":
                return 2, existing_vote
            else:
                return 0, existing_vote
        else:
            increment = 1 if new_vote_type == "upvote" else -1
            return increment, None
    
    @staticmethod
    def validate_vote_type(vote_type: str) -> None:
        """Validate vote type."""
        if vote_type not in ("upvote", "downvote"):
            raise InvalidChatError(f"Invalid vote type: {vote_type}")


class ViewHandler:
    """Handles view operations."""
    
    @staticmethod
    def create_view_record(view_repository, chat_id: str, user_id: Optional[str]) -> str:
        """
        Create a view record.
        
        Args:
            view_repository: View repository
            chat_id: Chat ID
            user_id: Optional user ID
            
        Returns:
            View ID
        """
        view_id = generate_id()
        view_repository.create(
            id=view_id,
            chat_id=chat_id,
            user_id=user_id.strip() if user_id else None,
            created_at=get_current_timestamp()
        )
        return view_id


class RemixHandler:
    """Handles remix operations."""
    
    @staticmethod
    def create_remix_record(
        remix_repository,
        original_chat_id: str,
        remix_chat_id: str,
        user_id: str
    ) -> ChatRemix:
        """
        Create a remix record.
        
        Args:
            remix_repository: Remix repository
            original_chat_id: Original chat ID
            remix_chat_id: Remix chat ID
            user_id: User ID
            
        Returns:
            Remix record
        """
        remix_id = generate_id()
        return remix_repository.create(
            id=remix_id,
            original_chat_id=original_chat_id,
            remix_chat_id=remix_chat_id,
            user_id=user_id,
            created_at=get_current_timestamp()
        )






