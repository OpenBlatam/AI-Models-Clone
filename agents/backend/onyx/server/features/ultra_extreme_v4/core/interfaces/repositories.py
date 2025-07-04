"""
🚀 ULTRA-EXTREME REPOSITORY INTERFACES V4
=========================================

Ultra-extreme repository interfaces with:
- Generic repository pattern
- CRUD operations
- Batch operations
- Query optimization
- Caching integration
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


# Type variables for generic repositories
T = TypeVar('T')  # Entity type
ID = TypeVar('ID')  # ID type


class SortOrder(Enum):
    """Sort order enumeration"""
    ASC = "asc"
    DESC = "desc"


@dataclass
class PaginationParams:
    """Pagination parameters"""
    page: int = 1
    size: int = 20
    max_size: int = 100


@dataclass
class SortParams:
    """Sort parameters"""
    field: str
    order: SortOrder = SortOrder.ASC


@dataclass
class FilterParams:
    """Filter parameters"""
    field: str
    operator: str  # eq, ne, gt, gte, lt, lte, in, nin, like, ilike
    value: Any


@dataclass
class QueryParams:
    """Query parameters"""
    pagination: Optional[PaginationParams] = None
    sorting: Optional[List[SortParams]] = None
    filters: Optional[List[FilterParams]] = None
    includes: Optional[List[str]] = None
    excludes: Optional[List[str]] = None


@dataclass
class QueryResult(Generic[T]):
    """Query result with pagination"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool


class Repository(ABC, Generic[T, ID]):
    """Base repository interface"""
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity"""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: ID) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def get_all(self, query_params: Optional[QueryParams] = None) -> QueryResult[T]:
        """Get all entities with optional filtering and pagination"""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing entity"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: ID) -> bool:
        """Delete entity by ID"""
        pass
    
    @abstractmethod
    async def exists(self, entity_id: ID) -> bool:
        """Check if entity exists"""
        pass
    
    @abstractmethod
    async def count(self, query_params: Optional[QueryParams] = None) -> int:
        """Count entities with optional filtering"""
        pass
    
    # Batch operations
    @abstractmethod
    async def create_many(self, entities: List[T]) -> List[T]:
        """Create multiple entities"""
        pass
    
    @abstractmethod
    async def update_many(self, entities: List[T]) -> List[T]:
        """Update multiple entities"""
        pass
    
    @abstractmethod
    async def delete_many(self, entity_ids: List[ID]) -> int:
        """Delete multiple entities"""
        pass
    
    @abstractmethod
    async def get_many(self, entity_ids: List[ID]) -> List[T]:
        """Get multiple entities by IDs"""
        pass
    
    # Advanced operations
    @abstractmethod
    async def find_by_field(self, field: str, value: Any) -> List[T]:
        """Find entities by field value"""
        pass
    
    @abstractmethod
    async def find_one_by_field(self, field: str, value: Any) -> Optional[T]:
        """Find single entity by field value"""
        pass
    
    @abstractmethod
    async def search(self, search_term: str, fields: Optional[List[str]] = None) -> List[T]:
        """Search entities by term"""
        pass
    
    @abstractmethod
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform aggregation operations"""
        pass


class CachedRepository(Repository[T, ID]):
    """Repository with caching capabilities"""
    
    def __init__(self, repository: Repository[T, ID], cache_service: 'CacheService'):
        self.repository = repository
        self.cache_service = cache_service
        self.cache_ttl = 3600  # 1 hour default
    
    async def get_by_id(self, entity_id: ID) -> Optional[T]:
        """Get entity by ID with cache"""
        cache_key = f"{self._get_cache_prefix()}:{entity_id}"
        
        # Try cache first
        cached = await self.cache_service.get(cache_key)
        if cached is not None:
            return cached
        
        # Get from repository
        entity = await self.repository.get_by_id(entity_id)
        
        # Cache the result
        if entity is not None:
            await self.cache_service.set(cache_key, entity, ttl=self.cache_ttl)
        
        return entity
    
    async def create(self, entity: T) -> T:
        """Create entity and invalidate cache"""
        result = await self.repository.create(entity)
        await self._invalidate_cache()
        return result
    
    async def update(self, entity: T) -> T:
        """Update entity and invalidate cache"""
        result = await self.repository.update(entity)
        await self._invalidate_cache()
        return result
    
    async def delete(self, entity_id: ID) -> bool:
        """Delete entity and invalidate cache"""
        result = await self.repository.delete(entity_id)
        if result:
            await self._invalidate_cache()
        return result
    
    async def _invalidate_cache(self):
        """Invalidate cache for this repository"""
        cache_pattern = f"{self._get_cache_prefix()}:*"
        await self.cache_service.clear_pattern(cache_pattern)
    
    def _get_cache_prefix(self) -> str:
        """Get cache prefix for this repository"""
        return f"repo:{self.__class__.__name__.lower()}"


class OptimizedRepository(Repository[T, ID]):
    """Repository with optimization capabilities"""
    
    def __init__(self, repository: Repository[T, ID]):
        self.repository = repository
        self.query_cache: Dict[str, Any] = {}
    
    async def get_all(self, query_params: Optional[QueryParams] = None) -> QueryResult[T]:
        """Get all entities with query optimization"""
        # Generate cache key for query
        cache_key = self._generate_query_cache_key(query_params)
        
        # Check query cache
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]
        
        # Execute query
        result = await self.repository.get_all(query_params)
        
        # Cache result
        self.query_cache[cache_key] = result
        
        return result
    
    async def search(self, search_term: str, fields: Optional[List[str]] = None) -> List[T]:
        """Search with optimization"""
        # Implement search optimization
        return await self.repository.search(search_term, fields)
    
    def _generate_query_cache_key(self, query_params: Optional[QueryParams]) -> str:
        """Generate cache key for query"""
        if query_params is None:
            return "all"
        
        # Create a hash of query parameters
        import hashlib
        import json
        
        query_str = json.dumps(query_params.__dict__, sort_keys=True, default=str)
        return hashlib.md5(query_str.encode()).hexdigest()


class TransactionalRepository(Repository[T, ID]):
    """Repository with transaction support"""
    
    def __init__(self, repository: Repository[T, ID]):
        self.repository = repository
    
    async def create_with_transaction(self, entities: List[T]) -> List[T]:
        """Create entities within a transaction"""
        # Implementation would depend on the specific database
        # This is a placeholder for transaction logic
        results = []
        for entity in entities:
            result = await self.repository.create(entity)
            results.append(result)
        return results
    
    async def update_with_transaction(self, entities: List[T]) -> List[T]:
        """Update entities within a transaction"""
        results = []
        for entity in entities:
            result = await self.repository.update(entity)
            results.append(result)
        return results
    
    async def delete_with_transaction(self, entity_ids: List[ID]) -> int:
        """Delete entities within a transaction"""
        deleted_count = 0
        for entity_id in entity_ids:
            if await self.repository.delete(entity_id):
                deleted_count += 1
        return deleted_count


# Specific repository interfaces for different entities

class ContentRepository(Repository['UltraContent', str]):
    """Content repository interface"""
    
    async def get_by_title(self, title: str) -> Optional['UltraContent']:
        """Get content by title"""
        pass
    
    async def get_by_type(self, content_type: str) -> List['UltraContent']:
        """Get content by type"""
        pass
    
    async def get_by_language(self, language: str) -> List['UltraContent']:
        """Get content by language"""
        pass
    
    async def get_recent(self, limit: int = 10) -> List['UltraContent']:
        """Get recent content"""
        pass
    
    async def get_popular(self, limit: int = 10) -> List['UltraContent']:
        """Get popular content"""
        pass
    
    async def search_by_keywords(self, keywords: List[str]) -> List['UltraContent']:
        """Search content by keywords"""
        pass


class OptimizationRepository(Repository['UltraOptimization', str]):
    """Optimization repository interface"""
    
    async def get_by_type(self, optimization_type: str) -> List['UltraOptimization']:
        """Get optimizations by type"""
        pass
    
    async def get_by_status(self, status: str) -> List['UltraOptimization']:
        """Get optimizations by status"""
        pass
    
    async def get_recent_optimizations(self, limit: int = 10) -> List['UltraOptimization']:
        """Get recent optimizations"""
        pass
    
    async def get_optimization_metrics(self, time_range: str) -> Dict[str, Any]:
        """Get optimization metrics"""
        pass


class AIRepository(Repository['UltraAI', str]):
    """AI repository interface"""
    
    async def get_by_model(self, model: str) -> List['UltraAI']:
        """Get AI records by model"""
        pass
    
    async def get_by_provider(self, provider: str) -> List['UltraAI']:
        """Get AI records by provider"""
        pass
    
    async def get_ai_metrics(self, time_range: str) -> Dict[str, Any]:
        """Get AI metrics"""
        pass
    
    async def get_model_performance(self, model: str) -> Dict[str, Any]:
        """Get model performance metrics"""
        pass


# Repository factory for creating repositories

class RepositoryFactory:
    """Factory for creating repositories"""
    
    def __init__(self):
        self._repositories: Dict[str, Repository] = {}
    
    def register_repository(self, name: str, repository: Repository):
        """Register a repository"""
        self._repositories[name] = repository
    
    def get_repository(self, name: str) -> Repository:
        """Get a repository by name"""
        if name not in self._repositories:
            raise ValueError(f"Repository '{name}' not found")
        return self._repositories[name]
    
    def create_cached_repository(self, name: str, cache_service: 'CacheService') -> CachedRepository:
        """Create a cached repository"""
        repository = self.get_repository(name)
        return CachedRepository(repository, cache_service)
    
    def create_optimized_repository(self, name: str) -> OptimizedRepository:
        """Create an optimized repository"""
        repository = self.get_repository(name)
        return OptimizedRepository(repository)
    
    def create_transactional_repository(self, name: str) -> TransactionalRepository:
        """Create a transactional repository"""
        repository = self.get_repository(name)
        return TransactionalRepository(repository)


# Import the cache service interface
from .cache import CacheService 