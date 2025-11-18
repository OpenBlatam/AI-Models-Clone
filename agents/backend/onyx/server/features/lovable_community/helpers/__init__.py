"""
Helpers module for Lovable Community

Organized into specific submodules for better maintainability.
"""

from .converters import (
    chat_to_response,
    chats_to_responses,
    remix_to_response,
    remixes_to_responses,
    vote_to_response,
)

from .tags import (
    parse_tags_string,
    format_tags_list,
    extract_tags_from_text,
)

from .text import (
    sanitize_text,
    truncate_text,
    format_datetime,
    get_chat_summary,
)

from .pagination import (
    calculate_pagination_metadata,
    validate_and_calculate_pagination,
)

from .search import (
    normalize_search_query,
)

from .engagement import (
    calculate_engagement_rate,
    calculate_trending_score,
)

from .filters import (
    group_chats_by_user,
    sort_chats_by_score,
    filter_public_chats,
    filter_featured_chats,
)

from .validation import (
    validate_uuid_format,
)

from .common import (
    generate_id,
    get_current_timestamp,
)

from .database import (
    handle_db_error,
    safe_db_operation,
)

from .responses import (
    build_chat_list_response,
    get_chats_with_votes,
)

__all__ = [
    # Converters
    "chat_to_response",
    "chats_to_responses",
    "remix_to_response",
    "remixes_to_responses",
    "vote_to_response",
    # Tags
    "parse_tags_string",
    "format_tags_list",
    "extract_tags_from_text",
    # Text
    "sanitize_text",
    "truncate_text",
    "format_datetime",
    "get_chat_summary",
    # Pagination
    "calculate_pagination_metadata",
    "validate_and_calculate_pagination",
    # Search
    "normalize_search_query",
    # Engagement
    "calculate_engagement_rate",
    "calculate_trending_score",
    # Filters
    "group_chats_by_user",
    "sort_chats_by_score",
    "filter_public_chats",
    "filter_featured_chats",
    # Validation
    "validate_uuid_format",
    # Common
    "generate_id",
    "get_current_timestamp",
    # Database
    "handle_db_error",
    "safe_db_operation",
    # Responses
    "build_chat_list_response",
    "get_chats_with_votes",
]



