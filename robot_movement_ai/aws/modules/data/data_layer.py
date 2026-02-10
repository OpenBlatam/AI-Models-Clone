"""
Data Layer
==========

Main data layer class.
"""

import logging
from typing import Optional
from aws.modules.data.repository_factory import RepositoryFactory
from aws.modules.data.cache_factory import CacheFactory
from aws.modules.data.messaging_factory import MessagingFactory
from aws.modules.ports.repository_port import RepositoryPort
from aws.modules.ports.cache_port import CachePort
from aws.modules.ports.messaging_port import MessagingPort

logger = logging.getLogger(__name__)


class DataLayer:
    """Data layer manager."""
    
    def __init__(
        self,
        repository: Optional[RepositoryPort] = None,
        cache: Optional[CachePort] = None,
        messaging: Optional[MessagingPort] = None
    ):
        self.repository = repository
        self.cache = cache
        self.messaging = messaging
    
    @classmethod
    def from_env(cls, service_name: str) -> "DataLayer":
        """Create data layer from environment variables."""
        repository = RepositoryFactory.create_from_env(service_name)
        cache = CacheFactory.create_from_env()
        messaging = MessagingFactory.create_from_env()
        
        return cls(
            repository=repository,
            cache=cache,
            messaging=messaging
        )
    
    def get_repository(self) -> Optional[RepositoryPort]:
        """Get repository."""
        return self.repository
    
    def get_cache(self) -> Optional[CachePort]:
        """Get cache."""
        return self.cache
    
    def get_messaging(self) -> Optional[MessagingPort]:
        """Get messaging."""
        return self.messaging















