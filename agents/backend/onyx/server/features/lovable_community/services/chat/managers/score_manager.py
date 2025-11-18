"""
Chat Score Management

Handles score calculation and updates for chats.
"""

from typing import Optional
from ....models import PublishedChat
from ...ranking import RankingService


class ScoreManager:
    """Manages chat score calculations and updates."""
    
    def __init__(self, ranking_service: RankingService):
        """
        Initialize score manager.
        
        Args:
            ranking_service: Ranking service for score calculations
        """
        self.ranking_service = ranking_service
    
    def calculate_score(
        self,
        chat: PublishedChat,
        vote_count: Optional[int] = None,
        remix_count: Optional[int] = None,
        view_count: Optional[int] = None
    ) -> float:
        """
        Calculate chat score.
        
        Args:
            chat: Chat object
            vote_count: Optional new vote count
            remix_count: Optional new remix count
            view_count: Optional new view count
            
        Returns:
            Calculated score
        """
        vote_count = vote_count if vote_count is not None else chat.vote_count
        remix_count = remix_count if remix_count is not None else chat.remix_count
        view_count = view_count if view_count is not None else chat.view_count
        
        return self.ranking_service.calculate_score(
            vote_count,
            remix_count,
            view_count,
            chat.created_at
        )






