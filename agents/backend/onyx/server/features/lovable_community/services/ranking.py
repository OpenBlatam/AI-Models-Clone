import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RankingService:
    @staticmethod
    def calculate_score(
        vote_count: int,
        remix_count: int,
        view_count: int,
        created_at: datetime,
        base_score: float = 0.0
    ) -> float:
        if vote_count < 0 or remix_count < 0 or view_count < 0:
            raise ValueError("Counts cannot be negative")
        
        if not isinstance(created_at, datetime):
            raise TypeError("created_at must be a datetime object")
        
        now = datetime.utcnow()
        age_hours = (now - created_at).total_seconds() / 3600
        
        if age_hours < 0.1:
            age_hours = 0.1
        
        try:
            from ..config import settings
            vote_weight = settings.vote_weight
            remix_weight = settings.remix_weight
            view_weight = settings.view_weight
        except ImportError:
            vote_weight = 2.0
            remix_weight = 3.0
            view_weight = 0.1
        
        engagement_score = (
            vote_count * vote_weight +
            remix_count * remix_weight +
            view_count * view_weight
        )
        
        time_decay = max(1.0, 1 + (age_hours / 24))
        
        score = (engagement_score + base_score) / time_decay
        
        return round(score, 2)

