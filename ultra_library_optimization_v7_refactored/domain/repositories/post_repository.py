#!/usr/bin/env python3
"""
Post Repository Interface - Domain Layer
=======================================

Repository interface for LinkedIn post persistence operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from ..entities.linkedin_post import LinkedInPost


class PostRepository(ABC):
    """
    Abstract repository interface for LinkedIn post persistence.
    
    This interface defines the contract for post repository implementations
    and ensures separation of concerns between domain and infrastructure layers.
    """
    
    @abstractmethod
    async def save(self, post: LinkedInPost) -> LinkedInPost:
        """
        Save a LinkedIn post.
        
        Args:
            post: The LinkedIn post to save
            
        Returns:
            The saved LinkedIn post with updated metadata
            
        Raises:
            RepositoryError: If save operation fails
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, post_id: UUID) -> Optional[LinkedInPost]:
        """
        Find a LinkedIn post by ID.
        
        Args:
            post_id: The UUID of the post to find
            
        Returns:
            The LinkedIn post if found, None otherwise
            
        Raises:
            RepositoryError: If find operation fails
        """
        pass
    
    @abstractmethod
    async def find_by_topic(self, topic: str) -> List[LinkedInPost]:
        """
        Find LinkedIn posts by topic.
        
        Args:
            topic: The topic to search for
            
        Returns:
            List of LinkedIn posts matching the topic
            
        Raises:
            RepositoryError: If find operation fails
        """
        pass
    
    @abstractmethod
    async def find_by_optimization_strategy(self, strategy: str) -> List[LinkedInPost]:
        """
        Find LinkedIn posts by optimization strategy.
        
        Args:
            strategy: The optimization strategy to search for
            
        Returns:
            List of LinkedIn posts using the specified strategy
            
        Raises:
            RepositoryError: If find operation fails
        """
        pass
    
    @abstractmethod
    async def find_high_performing_posts(self, min_score: float = 0.8) -> List[LinkedInPost]:
        """
        Find high-performing LinkedIn posts.
        
        Args:
            min_score: Minimum optimization score threshold
            
        Returns:
            List of high-performing LinkedIn posts
            
        Raises:
            RepositoryError: If find operation fails
        """
        pass
    
    @abstractmethod
    async def find_recent_posts(self, limit: int = 100) -> List[LinkedInPost]:
        """
        Find recent LinkedIn posts.
        
        Args:
            limit: Maximum number of posts to return
            
        Returns:
            List of recent LinkedIn posts
            
        Raises:
            RepositoryError: If find operation fails
        """
        pass
    
    @abstractmethod
    async def update(self, post: LinkedInPost) -> LinkedInPost:
        """
        Update a LinkedIn post.
        
        Args:
            post: The LinkedIn post to update
            
        Returns:
            The updated LinkedIn post
            
        Raises:
            RepositoryError: If update operation fails
        """
        pass
    
    @abstractmethod
    async def delete(self, post_id: UUID) -> bool:
        """
        Delete a LinkedIn post.
        
        Args:
            post_id: The UUID of the post to delete
            
        Returns:
            True if deleted successfully, False otherwise
            
        Raises:
            RepositoryError: If delete operation fails
        """
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """
        Get total count of LinkedIn posts.
        
        Returns:
            Total number of LinkedIn posts
            
        Raises:
            RepositoryError: If count operation fails
        """
        pass
    
    @abstractmethod
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for all posts.
        
        Returns:
            Dictionary containing performance metrics
            
        Raises:
            RepositoryError: If metrics operation fails
        """
        pass
    
    @abstractmethod
    async def bulk_save(self, posts: List[LinkedInPost]) -> List[LinkedInPost]:
        """
        Save multiple LinkedIn posts in bulk.
        
        Args:
            posts: List of LinkedIn posts to save
            
        Returns:
            List of saved LinkedIn posts
            
        Raises:
            RepositoryError: If bulk save operation fails
        """
        pass
    
    @abstractmethod
    async def search_posts(self, query: str, limit: int = 50) -> List[LinkedInPost]:
        """
        Search LinkedIn posts by content.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of LinkedIn posts matching the search query
            
        Raises:
            RepositoryError: If search operation fails
        """
        pass
    
    @abstractmethod
    async def get_optimization_statistics(self) -> Dict[str, Any]:
        """
        Get optimization strategy statistics.
        
        Returns:
            Dictionary containing optimization statistics
            
        Raises:
            RepositoryError: If statistics operation fails
        """
        pass
    
    @abstractmethod
    async def get_engagement_analytics(self) -> Dict[str, Any]:
        """
        Get engagement analytics for all posts.
        
        Returns:
            Dictionary containing engagement analytics
            
        Raises:
            RepositoryError: If analytics operation fails
        """
        pass
    
    @abstractmethod
    async def cleanup_old_posts(self, days_old: int = 365) -> int:
        """
        Clean up old LinkedIn posts.
        
        Args:
            days_old: Posts older than this many days will be deleted
            
        Returns:
            Number of posts deleted
            
        Raises:
            RepositoryError: If cleanup operation fails
        """
        pass
    
    @abstractmethod
    async def export_posts(self, format: str = "json") -> str:
        """
        Export all posts in specified format.
        
        Args:
            format: Export format (json, csv, xml)
            
        Returns:
            Exported data as string
            
        Raises:
            RepositoryError: If export operation fails
        """
        pass
    
    @abstractmethod
    async def import_posts(self, data: str, format: str = "json") -> int:
        """
        Import posts from specified format.
        
        Args:
            data: Data to import
            format: Import format (json, csv, xml)
            
        Returns:
            Number of posts imported
            
        Raises:
            RepositoryError: If import operation fails
        """
        pass
    
    @abstractmethod
    async def backup_posts(self) -> str:
        """
        Create a backup of all posts.
        
        Returns:
            Backup file path or identifier
            
        Raises:
            RepositoryError: If backup operation fails
        """
        pass
    
    @abstractmethod
    async def restore_posts(self, backup_id: str) -> bool:
        """
        Restore posts from backup.
        
        Args:
            backup_id: Backup identifier
            
        Returns:
            True if restore successful, False otherwise
            
        Raises:
            RepositoryError: If restore operation fails
        """
        pass


class RepositoryError(Exception):
    """Base exception for repository operations."""
    
    def __init__(self, message: str, operation: str = None, entity_id: str = None):
        self.message = message
        self.operation = operation
        self.entity_id = entity_id
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.operation and self.entity_id:
            return f"RepositoryError: {self.message} (Operation: {self.operation}, Entity: {self.entity_id})"
        elif self.operation:
            return f"RepositoryError: {self.message} (Operation: {self.operation})"
        else:
            return f"RepositoryError: {self.message}"


class PostNotFoundError(RepositoryError):
    """Exception raised when a post is not found."""
    
    def __init__(self, post_id: str):
        super().__init__(f"Post with ID {post_id} not found", "find", post_id)


class PostSaveError(RepositoryError):
    """Exception raised when post save operation fails."""
    
    def __init__(self, post_id: str, reason: str):
        super().__init__(f"Failed to save post {post_id}: {reason}", "save", post_id)


class PostUpdateError(RepositoryError):
    """Exception raised when post update operation fails."""
    
    def __init__(self, post_id: str, reason: str):
        super().__init__(f"Failed to update post {post_id}: {reason}", "update", post_id)


class PostDeleteError(RepositoryError):
    """Exception raised when post delete operation fails."""
    
    def __init__(self, post_id: str, reason: str):
        super().__init__(f"Failed to delete post {post_id}: {reason}", "delete", post_id) 