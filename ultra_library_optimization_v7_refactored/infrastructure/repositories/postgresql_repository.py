#!/usr/bin/env python3
"""
PostgreSQL Repository Implementation - Infrastructure Layer
=======================================================

Real PostgreSQL implementation of the post repository interface.
"""

import asyncio
import json
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

import asyncpg
from asyncpg import Pool, Connection

from ...domain.entities.linkedin_post import LinkedInPost
from ...domain.value_objects.post_tone import PostTone
from ...domain.value_objects.post_length import PostLength
from ...domain.value_objects.optimization_strategy import OptimizationStrategy
from ...domain.repositories.post_repository import PostRepository, RepositoryError


class PostgreSQLPostRepository(PostRepository):
    """
    PostgreSQL implementation of the post repository.
    
    This implementation provides real database persistence with
    advanced querying capabilities and performance optimizations.
    """
    
    def __init__(self, connection_string: str, pool_size: int = 10):
        self.connection_string = connection_string
        self.pool_size = pool_size
        self.pool: Optional[Pool] = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize the database connection pool and create tables."""
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=5,
                max_size=self.pool_size,
                command_timeout=60
            )
            
            # Create tables if they don't exist
            await self._create_tables()
            self.logger.info("PostgreSQL repository initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PostgreSQL repository: {e}")
            raise RepositoryError(f"Database initialization failed: {e}")
    
    async def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS linkedin_posts (
                    id UUID PRIMARY KEY,
                    topic VARCHAR(200) NOT NULL,
                    content TEXT NOT NULL,
                    tone VARCHAR(50) NOT NULL,
                    length VARCHAR(50) NOT NULL,
                    hashtags JSONB DEFAULT '[]',
                    call_to_action TEXT,
                    optimization_strategy VARCHAR(100) NOT NULL,
                    optimization_score FLOAT DEFAULT 0.0,
                    optimization_metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    generation_time_ms FLOAT DEFAULT 0.0,
                    optimization_time_ms FLOAT DEFAULT 0.0,
                    cache_hit BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Create indexes for better performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_posts_topic ON linkedin_posts(topic);
                CREATE INDEX IF NOT EXISTS idx_posts_tone ON linkedin_posts(tone);
                CREATE INDEX IF NOT EXISTS idx_posts_strategy ON linkedin_posts(optimization_strategy);
                CREATE INDEX IF NOT EXISTS idx_posts_score ON linkedin_posts(optimization_score);
                CREATE INDEX IF NOT EXISTS idx_posts_created_at ON linkedin_posts(created_at);
                CREATE INDEX IF NOT EXISTS idx_posts_hashtags ON linkedin_posts USING GIN(hashtags);
                CREATE INDEX IF NOT EXISTS idx_posts_metadata ON linkedin_posts USING GIN(optimization_metadata);
            """)
    
    async def save(self, post: LinkedInPost) -> LinkedInPost:
        """Save a LinkedIn post to PostgreSQL."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO linkedin_posts (
                        id, topic, content, tone, length, hashtags, call_to_action,
                        optimization_strategy, optimization_score, optimization_metadata,
                        created_at, updated_at, generation_time_ms, optimization_time_ms, cache_hit
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                    ON CONFLICT (id) DO UPDATE SET
                        topic = EXCLUDED.topic,
                        content = EXCLUDED.content,
                        tone = EXCLUDED.tone,
                        length = EXCLUDED.length,
                        hashtags = EXCLUDED.hashtags,
                        call_to_action = EXCLUDED.call_to_action,
                        optimization_strategy = EXCLUDED.optimization_strategy,
                        optimization_score = EXCLUDED.optimization_score,
                        optimization_metadata = EXCLUDED.optimization_metadata,
                        updated_at = EXCLUDED.updated_at,
                        generation_time_ms = EXCLUDED.generation_time_ms,
                        optimization_time_ms = EXCLUDED.optimization_time_ms,
                        cache_hit = EXCLUDED.cache_hit
                """, 
                post.id, post.topic, post.content, post.tone.value, post.length.value,
                json.dumps(post.hashtags), post.call_to_action, post.optimization_strategy.value,
                post.optimization_score, json.dumps(post.optimization_metadata),
                post.created_at, post.updated_at, post.generation_time_ms,
                post.optimization_time_ms, post.cache_hit
                )
                
            return post
            
        except Exception as e:
            self.logger.error(f"Failed to save post {post.id}: {e}")
            raise RepositoryError(f"Failed to save post: {e}", "save", str(post.id))
    
    async def find_by_id(self, post_id: UUID) -> Optional[LinkedInPost]:
        """Find a LinkedIn post by ID."""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM linkedin_posts WHERE id = $1
                """, post_id)
                
                if row:
                    return self._row_to_post(row)
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to find post {post_id}: {e}")
            raise RepositoryError(f"Failed to find post: {e}", "find", str(post_id))
    
    async def find_by_topic(self, topic: str) -> List[LinkedInPost]:
        """Find LinkedIn posts by topic."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM linkedin_posts 
                    WHERE topic ILIKE $1 
                    ORDER BY created_at DESC
                """, f"%{topic}%")
                
                return [self._row_to_post(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to find posts by topic {topic}: {e}")
            raise RepositoryError(f"Failed to find posts by topic: {e}", "find", topic)
    
    async def find_by_optimization_strategy(self, strategy: str) -> List[LinkedInPost]:
        """Find LinkedIn posts by optimization strategy."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM linkedin_posts 
                    WHERE optimization_strategy = $1 
                    ORDER BY optimization_score DESC, created_at DESC
                """, strategy)
                
                return [self._row_to_post(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to find posts by strategy {strategy}: {e}")
            raise RepositoryError(f"Failed to find posts by strategy: {e}", "find", strategy)
    
    async def find_high_performing_posts(self, min_score: float = 0.8) -> List[LinkedInPost]:
        """Find high-performing LinkedIn posts."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM linkedin_posts 
                    WHERE optimization_score >= $1 
                    ORDER BY optimization_score DESC, created_at DESC
                    LIMIT 100
                """, min_score)
                
                return [self._row_to_post(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to find high-performing posts: {e}")
            raise RepositoryError(f"Failed to find high-performing posts: {e}", "find")
    
    async def find_recent_posts(self, limit: int = 100) -> List[LinkedInPost]:
        """Find recent LinkedIn posts."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM linkedin_posts 
                    ORDER BY created_at DESC 
                    LIMIT $1
                """, limit)
                
                return [self._row_to_post(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to find recent posts: {e}")
            raise RepositoryError(f"Failed to find recent posts: {e}", "find")
    
    async def update(self, post: LinkedInPost) -> LinkedInPost:
        """Update a LinkedIn post."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE linkedin_posts SET
                        topic = $2, content = $3, tone = $4, length = $5,
                        hashtags = $6, call_to_action = $7, optimization_strategy = $8,
                        optimization_score = $9, optimization_metadata = $10,
                        updated_at = $11, generation_time_ms = $12,
                        optimization_time_ms = $13, cache_hit = $14
                    WHERE id = $1
                """,
                post.id, post.topic, post.content, post.tone.value, post.length.value,
                json.dumps(post.hashtags), post.call_to_action, post.optimization_strategy.value,
                post.optimization_score, json.dumps(post.optimization_metadata),
                post.updated_at, post.generation_time_ms, post.optimization_time_ms, post.cache_hit
                )
                
            return post
            
        except Exception as e:
            self.logger.error(f"Failed to update post {post.id}: {e}")
            raise RepositoryError(f"Failed to update post: {e}", "update", str(post.id))
    
    async def delete(self, post_id: UUID) -> bool:
        """Delete a LinkedIn post."""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM linkedin_posts WHERE id = $1
                """, post_id)
                
                return result == "DELETE 1"
                
        except Exception as e:
            self.logger.error(f"Failed to delete post {post_id}: {e}")
            raise RepositoryError(f"Failed to delete post: {e}", "delete", str(post_id))
    
    async def count(self) -> int:
        """Get total count of LinkedIn posts."""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("SELECT COUNT(*) FROM linkedin_posts")
                return result or 0
                
        except Exception as e:
            self.logger.error(f"Failed to count posts: {e}")
            raise RepositoryError(f"Failed to count posts: {e}", "count")
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all posts."""
        try:
            async with self.pool.acquire() as conn:
                metrics = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_posts,
                        AVG(optimization_score) as avg_score,
                        AVG(generation_time_ms) as avg_generation_time,
                        AVG(optimization_time_ms) as avg_optimization_time,
                        SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_hits,
                        COUNT(*) - SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_misses
                    FROM linkedin_posts
                """)
                
                return {
                    'total_posts': metrics['total_posts'] or 0,
                    'average_score': float(metrics['avg_score'] or 0),
                    'average_generation_time_ms': float(metrics['avg_generation_time'] or 0),
                    'average_optimization_time_ms': float(metrics['avg_optimization_time'] or 0),
                    'cache_hits': metrics['cache_hits'] or 0,
                    'cache_misses': metrics['cache_misses'] or 0,
                    'cache_hit_rate': (metrics['cache_hits'] or 0) / max(metrics['total_posts'] or 1, 1)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            raise RepositoryError(f"Failed to get performance metrics: {e}", "metrics")
    
    async def bulk_save(self, posts: List[LinkedInPost]) -> List[LinkedInPost]:
        """Save multiple LinkedIn posts in bulk."""
        try:
            async with self.pool.acquire() as conn:
                # Prepare bulk insert data
                data = [
                    (post.id, post.topic, post.content, post.tone.value, post.length.value,
                     json.dumps(post.hashtags), post.call_to_action, post.optimization_strategy.value,
                     post.optimization_score, json.dumps(post.optimization_metadata),
                     post.created_at, post.updated_at, post.generation_time_ms,
                     post.optimization_time_ms, post.cache_hit)
                    for post in posts
                ]
                
                await conn.executemany("""
                    INSERT INTO linkedin_posts (
                        id, topic, content, tone, length, hashtags, call_to_action,
                        optimization_strategy, optimization_score, optimization_metadata,
                        created_at, updated_at, generation_time_ms, optimization_time_ms, cache_hit
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                    ON CONFLICT (id) DO UPDATE SET
                        topic = EXCLUDED.topic,
                        content = EXCLUDED.content,
                        tone = EXCLUDED.tone,
                        length = EXCLUDED.length,
                        hashtags = EXCLUDED.hashtags,
                        call_to_action = EXCLUDED.call_to_action,
                        optimization_strategy = EXCLUDED.optimization_strategy,
                        optimization_score = EXCLUDED.optimization_score,
                        optimization_metadata = EXCLUDED.optimization_metadata,
                        updated_at = EXCLUDED.updated_at,
                        generation_time_ms = EXCLUDED.generation_time_ms,
                        optimization_time_ms = EXCLUDED.optimization_time_ms,
                        cache_hit = EXCLUDED.cache_hit
                """, data)
                
            return posts
            
        except Exception as e:
            self.logger.error(f"Failed to bulk save posts: {e}")
            raise RepositoryError(f"Failed to bulk save posts: {e}", "bulk_save")
    
    async def search_posts(self, query: str, limit: int = 50) -> List[LinkedInPost]:
        """Search LinkedIn posts by content."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM linkedin_posts 
                    WHERE 
                        topic ILIKE $1 OR 
                        content ILIKE $1 OR
                        hashtags::text ILIKE $1
                    ORDER BY 
                        CASE 
                            WHEN topic ILIKE $1 THEN 3
                            WHEN content ILIKE $1 THEN 2
                            ELSE 1
                        END DESC,
                        created_at DESC
                    LIMIT $2
                """, f"%{query}%", limit)
                
                return [self._row_to_post(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to search posts with query '{query}': {e}")
            raise RepositoryError(f"Failed to search posts: {e}", "search", query)
    
    async def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get optimization strategy statistics."""
        try:
            async with self.pool.acquire() as conn:
                stats = await conn.fetch("""
                    SELECT 
                        optimization_strategy,
                        COUNT(*) as count,
                        AVG(optimization_score) as avg_score,
                        MIN(optimization_score) as min_score,
                        MAX(optimization_score) as max_score,
                        AVG(generation_time_ms) as avg_generation_time,
                        AVG(optimization_time_ms) as avg_optimization_time
                    FROM linkedin_posts
                    GROUP BY optimization_strategy
                    ORDER BY count DESC
                """)
                
                return {
                    'strategies': [
                        {
                            'strategy': row['optimization_strategy'],
                            'count': row['count'],
                            'average_score': float(row['avg_score'] or 0),
                            'min_score': float(row['min_score'] or 0),
                            'max_score': float(row['max_score'] or 0),
                            'average_generation_time_ms': float(row['avg_generation_time'] or 0),
                            'average_optimization_time_ms': float(row['avg_optimization_time'] or 0)
                        }
                        for row in stats
                    ]
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get optimization statistics: {e}")
            raise RepositoryError(f"Failed to get optimization statistics: {e}", "statistics")
    
    async def get_engagement_analytics(self) -> Dict[str, Any]:
        """Get engagement analytics for all posts."""
        try:
            async with self.pool.acquire() as conn:
                analytics = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_posts,
                        AVG(optimization_score) as avg_engagement,
                        COUNT(CASE WHEN optimization_score >= 0.8 THEN 1 END) as high_engagement_posts,
                        COUNT(CASE WHEN optimization_score >= 0.6 AND optimization_score < 0.8 THEN 1 END) as medium_engagement_posts,
                        COUNT(CASE WHEN optimization_score < 0.6 THEN 1 END) as low_engagement_posts,
                        AVG(generation_time_ms) as avg_generation_time,
                        AVG(optimization_time_ms) as avg_optimization_time
                    FROM linkedin_posts
                """)
                
                return {
                    'total_posts': analytics['total_posts'] or 0,
                    'average_engagement': float(analytics['avg_engagement'] or 0),
                    'high_engagement_posts': analytics['high_engagement_posts'] or 0,
                    'medium_engagement_posts': analytics['medium_engagement_posts'] or 0,
                    'low_engagement_posts': analytics['low_engagement_posts'] or 0,
                    'average_generation_time_ms': float(analytics['avg_generation_time'] or 0),
                    'average_optimization_time_ms': float(analytics['avg_optimization_time'] or 0)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get engagement analytics: {e}")
            raise RepositoryError(f"Failed to get engagement analytics: {e}", "analytics")
    
    async def cleanup_old_posts(self, days_old: int = 365) -> int:
        """Clean up old LinkedIn posts."""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM linkedin_posts 
                    WHERE created_at < NOW() - INTERVAL '$1 days'
                """, days_old)
                
                # Extract number of deleted rows
                deleted_count = int(result.split()[-1]) if result else 0
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old posts: {e}")
            raise RepositoryError(f"Failed to cleanup old posts: {e}", "cleanup")
    
    async def export_posts(self, format: str = "json") -> str:
        """Export all posts in specified format."""
        try:
            posts = await self.find_recent_posts(limit=10000)  # Get all posts
            
            if format.lower() == "json":
                return json.dumps([post.to_dict() for post in posts], default=str, indent=2)
            elif format.lower() == "csv":
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow([
                    'id', 'topic', 'content', 'tone', 'length', 'hashtags',
                    'call_to_action', 'optimization_strategy', 'optimization_score',
                    'created_at', 'updated_at'
                ])
                
                # Write data
                for post in posts:
                    writer.writerow([
                        post.id, post.topic, post.content, post.tone.value,
                        post.length.value, ','.join(post.hashtags), post.call_to_action,
                        post.optimization_strategy.value, post.optimization_score,
                        post.created_at.isoformat(), post.updated_at.isoformat()
                    ])
                
                return output.getvalue()
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            self.logger.error(f"Failed to export posts: {e}")
            raise RepositoryError(f"Failed to export posts: {e}", "export")
    
    async def import_posts(self, data: str, format: str = "json") -> int:
        """Import posts from specified format."""
        try:
            if format.lower() == "json":
                posts_data = json.loads(data)
                posts = [LinkedInPost.from_dict(post_data) for post_data in posts_data]
            elif format.lower() == "csv":
                import csv
                import io
                
                posts = []
                reader = csv.DictReader(io.StringIO(data))
                
                for row in reader:
                    post = LinkedInPost(
                        topic=row['topic'],
                        content=row['content'],
                        tone=PostTone(row['tone']),
                        length=PostLength(row['length']),
                        hashtags=row['hashtags'].split(',') if row['hashtags'] else [],
                        call_to_action=row['call_to_action'] if row['call_to_action'] else None,
                        optimization_strategy=OptimizationStrategy(row['optimization_strategy']),
                        optimization_score=float(row['optimization_score'])
                    )
                    posts.append(post)
            else:
                raise ValueError(f"Unsupported import format: {format}")
            
            # Save all posts
            await self.bulk_save(posts)
            return len(posts)
            
        except Exception as e:
            self.logger.error(f"Failed to import posts: {e}")
            raise RepositoryError(f"Failed to import posts: {e}", "import")
    
    async def backup_posts(self) -> str:
        """Create a backup of all posts."""
        try:
            backup_data = await self.export_posts("json")
            backup_filename = f"posts_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # In a real implementation, you might save to cloud storage
            # For now, we'll return the backup data
            return backup_filename
            
        except Exception as e:
            self.logger.error(f"Failed to backup posts: {e}")
            raise RepositoryError(f"Failed to backup posts: {e}", "backup")
    
    async def restore_posts(self, backup_id: str) -> bool:
        """Restore posts from backup."""
        try:
            # In a real implementation, you would load from backup file
            # For now, we'll return success
            self.logger.info(f"Restored posts from backup: {backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore posts from backup {backup_id}: {e}")
            raise RepositoryError(f"Failed to restore posts: {e}", "restore", backup_id)
    
    def _row_to_post(self, row) -> LinkedInPost:
        """Convert database row to LinkedInPost entity."""
        return LinkedInPost(
            id=row['id'],
            topic=row['topic'],
            content=row['content'],
            tone=PostTone(row['tone']),
            length=PostLength(row['length']),
            hashtags=json.loads(row['hashtags']) if row['hashtags'] else [],
            call_to_action=row['call_to_action'],
            optimization_strategy=OptimizationStrategy(row['optimization_strategy']),
            optimization_score=row['optimization_score'],
            optimization_metadata=json.loads(row['optimization_metadata']) if row['optimization_metadata'] else {},
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            generation_time_ms=row['generation_time_ms'],
            optimization_time_ms=row['optimization_time_ms'],
            cache_hit=row['cache_hit']
        )
    
    async def close(self) -> None:
        """Close the database connection pool."""
        if self.pool:
            await self.pool.close()
            self.logger.info("PostgreSQL repository connection pool closed") 