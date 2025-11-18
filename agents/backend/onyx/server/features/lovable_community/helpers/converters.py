"""
Model to Response converters

Functions for converting database models to Pydantic response schemas.
"""

from typing import Optional, List, Dict
from ..models import PublishedChat, ChatRemix, ChatVote
from ..schemas import PublishedChatResponse, RemixResponse, VoteResponse


def chat_to_response(
    chat: PublishedChat,
    user_id: Optional[str] = None,
    user_vote: Optional[ChatVote] = None
) -> PublishedChatResponse:
    """
    Converts a PublishedChat model to PublishedChatResponse.
    
    Optimized to use model's cached tags list method.
    
    Args:
        chat: PublishedChat model
        user_id: Current user ID (optional)
        user_vote: User's vote (optional)
        
    Returns:
        PublishedChatResponse
    """
    tags_list = chat.get_tags_list() or None
    
    return PublishedChatResponse(
        id=chat.id,
        user_id=chat.user_id,
        title=chat.title,
        description=chat.description,
        chat_content=chat.chat_content,
        tags=tags_list,
        vote_count=chat.vote_count,
        remix_count=chat.remix_count,
        view_count=chat.view_count,
        score=chat.score,
        is_public=chat.is_public,
        is_featured=chat.is_featured,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        original_chat_id=chat.original_chat_id,
        has_user_voted=user_vote is not None if user_id else None,
        user_vote_type=user_vote.vote_type if user_vote else None
    )


def chats_to_responses(
    chats: List[PublishedChat],
    user_id: Optional[str] = None,
    user_votes: Optional[Dict[str, ChatVote]] = None
) -> List[PublishedChatResponse]:
    """
    Converts a list of PublishedChat models to PublishedChatResponse list.
    
    Optimized batch conversion with pre-allocated list.
    
    Args:
        chats: List of PublishedChat models
        user_id: Current user ID (optional)
        user_votes: Dictionary of votes by chat_id (optional)
        
    Returns:
        List of PublishedChatResponse
    """
    if not chats:
        return []
    
    user_votes = user_votes or {}
    
    return [
        chat_to_response(
            chat,
            user_id=user_id,
            user_vote=user_votes.get(chat.id)
        )
        for chat in chats
    ]


def remix_to_response(remix: ChatRemix) -> RemixResponse:
    """
    Converts a ChatRemix model to RemixResponse.
    
    Args:
        remix: ChatRemix model
        
    Returns:
        RemixResponse
    """
    return RemixResponse(
        id=remix.id,
        original_chat_id=remix.original_chat_id,
        remix_chat_id=remix.remix_chat_id,
        user_id=remix.user_id,
        created_at=remix.created_at
    )


def remixes_to_responses(remixes: List[ChatRemix]) -> List[RemixResponse]:
    """
    Converts a list of ChatRemix models to RemixResponse list.
    
    Args:
        remixes: List of ChatRemix models
        
    Returns:
        List of RemixResponse
    """
    return [remix_to_response(remix) for remix in remixes]


def vote_to_response(vote: ChatVote) -> VoteResponse:
    """
    Converts a ChatVote model to VoteResponse.
    
    Args:
        vote: ChatVote model
        
    Returns:
        VoteResponse
    """
    return VoteResponse(
        id=vote.id,
        chat_id=vote.chat_id,
        user_id=vote.user_id,
        vote_type=vote.vote_type,
        created_at=vote.created_at
    )


