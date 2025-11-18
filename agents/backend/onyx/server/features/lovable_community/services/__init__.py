from .ranking import RankingService

# Try to import modular service first, fallback to refactored, then original
try:
    from .chat import ChatService
except ImportError:
    try:
        from .chat_refactored import ChatService
    except ImportError:
        from .chat import ChatService

__all__ = ["RankingService", "ChatService"]

