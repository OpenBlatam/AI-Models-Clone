"""
Engagement and trending helper functions

Functions for calculating engagement rates and trending scores.
"""

from typing import Optional
from datetime import datetime, timedelta


def calculate_engagement_rate(views: int, votes: int) -> Optional[float]:
    """
    Calculates engagement rate.
    
    Args:
        views: Number of views
        votes: Number of votes
        
    Returns:
        Engagement rate or None if cannot be calculated
    """
    if votes == 0:
        return None
    
    return round(views / votes, 2) if votes > 0 else None


def calculate_trending_score(
    vote_count: int,
    remix_count: int,
    view_count: int,
    created_at: datetime,
    hours_ago: int = 24
) -> float:
    """
    Calculates a trending score based on recent activity.
    
    Args:
        vote_count: Number of votes
        remix_count: Number of remixes
        view_count: Number of views
        created_at: Creation date
        hours_ago: Hours back to consider "recent"
        
    Returns:
        Trending score
    """
    now = datetime.utcnow()
    age_hours = (now - created_at).total_seconds() / 3600
    
    # If too old, low score
    if age_hours > hours_ago:
        return 0.0
    
    # Score based on recent engagement
    engagement = (vote_count * 2.0) + (remix_count * 3.0) + (view_count * 0.1)
    
    # Bonus for being recent
    recency_bonus = max(0, 1 - (age_hours / hours_ago))
    
    return round(engagement * (1 + recency_bonus), 2)








