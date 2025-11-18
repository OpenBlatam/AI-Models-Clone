"""
Response helper functions

Utility functions for building API responses with common patterns.
"""

from typing import List, Optional, Dict
from ..models import PublishedChat, ChatVote
from ..schemas import ChatListResponse, PublishedChatResponse
from ..services import ChatService
from .converters import chats_to_responses
from .pagination import calculate_pagination_metadata


def build_chat_list_response(
    chats: List[PublishedChat],
    total: int,
    page: int,
    page_size: int,
    current_user_id: Optional[str] = None,
    service: Optional[ChatService] = None
) -> ChatListResponse:
    """
    Build a ChatListResponse with pagination and user votes.
    
    Args:
        chats: List of chat models
        total: Total count of chats
        page: Current page number
        page_size: Page size
        current_user_id: Optional current user ID
        service: Optional ChatService for getting user votes
        
    Returns:
        ChatListResponse with pagination metadata
    """
    user_votes: Dict[str, ChatVote] = {}
    
    if current_user_id and chats and service:
        chat_ids = [chat.id for chat in chats]
        user_votes = service.get_user_votes_batch(chat_ids, current_user_id)
    
    chat_responses = chats_to_responses(chats, current_user_id, user_votes)
    pagination_meta = calculate_pagination_metadata(total, page, page_size)
    
    return ChatListResponse(
        chats=chat_responses,
        total=pagination_meta["total"],
        page=pagination_meta["page"],
        page_size=pagination_meta["page_size"],
        has_more=pagination_meta["has_more"]
    )


def get_chats_with_votes(
    chats: List[PublishedChat],
    current_user_id: Optional[str],
    service: ChatService
) -> tuple[List[PublishedChatResponse], Dict[str, ChatVote]]:
    """
    Get chats converted to responses with user votes.
    
    Args:
        chats: List of chat models
        current_user_id: Optional current user ID
        service: ChatService instance
        
    Returns:
        Tuple of (chat_responses, user_votes_dict)
    """
    user_votes: Dict[str, ChatVote] = {}
    
    if current_user_id and chats:
        chat_ids = [chat.id for chat in chats]
        user_votes = service.get_user_votes_batch(chat_ids, current_user_id)
    
    chat_responses = chats_to_responses(chats, current_user_id, user_votes)
    return chat_responses, user_votes






