"""
Database optimization service following functional patterns
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text, Index, MetaData
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import UUID
import uuid
import asyncio
import json
import psutil
import gc

from app.core.logging import get_logger
from app.core.errors import handle_validation_error, handle_internal_error
from app.models.optimization import DatabaseOptimization, QueryOptimization, IndexOptimization
from app.schemas.optimization import (
    DatabaseOptimizationResponse, QueryOptimizationResponse, IndexOptimizationResponse,
    DatabaseStatsResponse, QueryAnalysisResponse, IndexAnalysisResponse
)
from app.utils.validators import validate_query_complexity
from app.utils.helpers import calculate_query_cost, format_database_size
from app.utils.cache import cache_optimization_data, get_cached_optimization_data

logger = get_logger(__name__)

# Query optimization cache
_query_cache: Dict[str, Any] = {}
_query_stats: Dict[str, Dict[str, Any]] = {}


async def analyze_database_performance(
    db: AsyncSession
) -> DatabaseStatsResponse:
    """Analyze database performance and statistics."""
    try:
        # Get database size
        size_query = text("SELECT pg_database_size(current_database()) as size")
        size_result = await db.execute(size_query)
        db_size = size_result.scalar()
        
        # Get connection statistics
        conn_query = text("""
            SELECT 
                count(*) as total_connections,
                count(*) FILTER (WHERE state = 'active') as active_connections,
                count(*) FILTER (WHERE state = 'idle') as idle_connections,
                count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
            FROM pg_stat_activity
        """)
        conn_result = await db.execute(conn_query)
        conn_stats = conn_result.fetchone()
        
        # Get table statistics
        table_query = text("""
            SELECT 
                schemaname,
                tablename,
                n_tup_ins as inserts,
                n_tup_upd as updates,
                n_tup_del as deletes,
                n_live_tup as live_tuples,
                n_dead_tup as dead_tuples,
                n_tup_hot_upd as hot_updates,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
            FROM pg_stat_user_tables
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """)
        table_result = await db.execute(table_query)
        table_stats = [
            {
                "schema": row[0],
                "table": row[1],
                "inserts": row[2],
                "updates": row[3],
                "deletes": row[4],
                "live_tuples": row[5],
                "dead_tuples": row[6],
                "hot_updates": row[7],
                "size": row[8],
                "size_bytes": row[9]
            }
            for row in table_result.fetchall()
        ]
        
        # Get index statistics
        index_query = text("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_tup_read as tuples_read,
                idx_tup_fetch as tuples_fetched,
                pg_size_pretty(pg_relation_size(indexrelid)) as size,
                pg_relation_size(indexrelid) as size_bytes
            FROM pg_stat_user_indexes
            ORDER BY pg_relation_size(indexrelid) DESC
        """)
        index_result = await db.execute(index_query)
        index_stats = [
            {
                "schema": row[0],
                "table": row[1],
                "index": row[2],
                "tuples_read": row[3],
                "tuples_fetched": row[4],
                "size": row[5],
                "size_bytes": row[6]
            }
            for row in index_result.fetchall()
        ]
        
        # Get slow queries
        slow_queries = await get_slow_queries(db)
        
        # Get lock statistics
        lock_query = text("""
            SELECT 
                mode,
                count(*) as count
            FROM pg_locks
            GROUP BY mode
            ORDER BY count DESC
        """)
        lock_result = await db.execute(lock_query)
        lock_stats = {row[0]: row[1] for row in lock_result.fetchall()}
        
        # Calculate performance metrics
        total_tables = len(table_stats)
        total_indexes = len(index_stats)
        dead_tuple_ratio = sum(t["dead_tuples"] for t in table_stats) / max(sum(t["live_tuples"] for t in table_stats), 1) * 100
        
        return DatabaseStatsResponse(
            database_size_mb=round(db_size / 1024 / 1024, 2),
            total_connections=conn_stats[0],
            active_connections=conn_stats[1],
            idle_connections=conn_stats[2],
            idle_in_transaction=conn_stats[3],
            total_tables=total_tables,
            total_indexes=total_indexes,
            dead_tuple_ratio=round(dead_tuple_ratio, 2),
            table_stats=table_stats,
            index_stats=index_stats,
            slow_queries=slow_queries,
            lock_stats=lock_stats,
            analyzed_at=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to analyze database performance: {e}")
        raise handle_internal_error(f"Failed to analyze database performance: {str(e)}")


async def get_slow_queries(
    db: AsyncSession,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Get slow queries from pg_stat_statements."""
    try:
        slow_query = text("""
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                stddev_time,
                rows,
                100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
            FROM pg_stat_statements
            ORDER BY mean_time DESC
            LIMIT :limit
        """)
        
        result = await db.execute(slow_query, {"limit": limit})
        slow_queries = [
            {
                "query": row[0][:200] + "..." if len(row[0]) > 200 else row[0],
                "calls": row[1],
                "total_time": row[2],
                "mean_time": row[3],
                "stddev_time": row[4],
                "rows": row[5],
                "hit_percent": row[6]
            }
            for row in result.fetchall()
        ]
        
        return slow_queries
    
    except Exception as e:
        logger.error(f"Failed to get slow queries: {e}")
        return []


async def optimize_database_queries(
    db: AsyncSession
) -> List[QueryOptimizationResponse]:
    """Optimize database queries."""
    try:
        optimizations = []
        
        # Analyze slow queries
        slow_queries = await get_slow_queries(db, 20)
        
        for query_info in slow_queries:
            if query_info["mean_time"] > 100:  # Queries slower than 100ms
                optimization = await analyze_query_optimization(query_info, db)
                if optimization:
                    optimizations.append(optimization)
        
        # Analyze missing indexes
        missing_indexes = await find_missing_indexes(db)
        for missing_index in missing_indexes:
            optimizations.append(QueryOptimizationResponse(
                query_id=str(uuid.uuid4()),
                query_text=missing_index["query"],
                optimization_type="missing_index",
                current_cost=missing_index["cost"],
                optimized_cost=missing_index["optimized_cost"],
                improvement_percent=missing_index["improvement_percent"],
                recommendation=missing_index["recommendation"],
                estimated_impact="high"
            ))
        
        return optimizations
    
    except Exception as e:
        logger.error(f"Failed to optimize database queries: {e}")
        return []


async def analyze_query_optimization(
    query_info: Dict[str, Any],
    db: AsyncSession
) -> Optional[QueryOptimizationResponse]:
    """Analyze a specific query for optimization opportunities."""
    try:
        query_text = query_info["query"]
        
        # Skip if query is too short or not a SELECT
        if len(query_text) < 20 or not query_text.strip().upper().startswith("SELECT"):
            return None
        
        # Get query execution plan
        try:
            explain_query = text(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query_text}")
            explain_result = await db.execute(explain_query)
            plan = explain_result.scalar()
            
            if plan and len(plan) > 0:
                execution_plan = plan[0]
                total_cost = execution_plan.get("Total Cost", 0)
                execution_time = execution_plan.get("Execution Time", 0)
                
                # Analyze plan for optimization opportunities
                optimization_type = "unknown"
                recommendation = "No specific optimization found"
                estimated_improvement = 0
                
                # Check for sequential scans
                if "Seq Scan" in str(execution_plan):
                    optimization_type = "sequential_scan"
                    recommendation = "Consider adding an index to avoid sequential scan"
                    estimated_improvement = 50
                
                # Check for nested loops
                elif "Nested Loop" in str(execution_plan):
                    optimization_type = "nested_loop"
                    recommendation = "Consider optimizing join conditions or adding indexes"
                    estimated_improvement = 30
                
                # Check for hash joins
                elif "Hash Join" in str(execution_plan):
                    optimization_type = "hash_join"
                    recommendation = "Hash join is generally efficient, but check if indexes can help"
                    estimated_improvement = 10
                
                return QueryOptimizationResponse(
                    query_id=str(uuid.uuid4()),
                    query_text=query_text[:100] + "..." if len(query_text) > 100 else query_text,
                    optimization_type=optimization_type,
                    current_cost=total_cost,
                    optimized_cost=total_cost * (1 - estimated_improvement / 100),
                    improvement_percent=estimated_improvement,
                    recommendation=recommendation,
                    estimated_impact="medium" if estimated_improvement > 20 else "low"
                )
        
        except Exception:
            # Query might not be executable in EXPLAIN context
            pass
        
        return None
    
    except Exception as e:
        logger.error(f"Failed to analyze query optimization: {e}")
        return None


async def find_missing_indexes(
    db: AsyncSession
) -> List[Dict[str, Any]]:
    """Find missing indexes that could improve performance."""
    try:
        # This is a simplified version - in practice, you'd analyze query patterns
        missing_indexes = []
        
        # Check for tables with high sequential scan activity
        seq_scan_query = text("""
            SELECT 
                schemaname,
                tablename,
                seq_scan,
                seq_tup_read,
                idx_scan,
                idx_tup_fetch
            FROM pg_stat_user_tables
            WHERE seq_scan > idx_scan * 2
            AND seq_tup_read > 1000
            ORDER BY seq_tup_read DESC
        """)
        
        result = await db.execute(seq_scan_query)
        for row in result.fetchall():
            if row[1] > row[3] * 2:  # More sequential scans than index scans
                missing_indexes.append({
                    "table": f"{row[0]}.{row[1]}",
                    "query": f"SELECT * FROM {row[0]}.{row[1]} WHERE ...",
                    "cost": row[2] * 0.1,  # Estimated cost
                    "optimized_cost": row[2] * 0.01,  # Estimated cost with index
                    "improvement_percent": 90,
                    "recommendation": f"Consider adding indexes on frequently queried columns in {row[0]}.{row[1]}"
                })
        
        return missing_indexes
    
    except Exception as e:
        logger.error(f"Failed to find missing indexes: {e}")
        return []


async def optimize_database_indexes(
    db: AsyncSession
) -> List[IndexOptimizationResponse]:
    """Optimize database indexes."""
    try:
        optimizations = []
        
        # Find unused indexes
        unused_indexes = await find_unused_indexes(db)
        for unused_index in unused_indexes:
            optimizations.append(IndexOptimizationResponse(
                index_id=str(uuid.uuid4()),
                table_name=unused_index["table"],
                index_name=unused_index["index"],
                optimization_type="unused_index",
                current_size_mb=unused_index["size_mb"],
                optimized_size_mb=0,
                improvement_percent=100,
                recommendation=f"Consider dropping unused index {unused_index['index']}",
                estimated_impact="medium"
            ))
        
        # Find duplicate indexes
        duplicate_indexes = await find_duplicate_indexes(db)
        for duplicate_index in duplicate_indexes:
            optimizations.append(IndexOptimizationResponse(
                index_id=str(uuid.uuid4()),
                table_name=duplicate_index["table"],
                index_name=duplicate_index["index"],
                optimization_type="duplicate_index",
                current_size_mb=duplicate_index["size_mb"],
                optimized_size_mb=0,
                improvement_percent=100,
                recommendation=f"Consider dropping duplicate index {duplicate_index['index']}",
                estimated_impact="low"
            ))
        
        # Find oversized indexes
        oversized_indexes = await find_oversized_indexes(db)
        for oversized_index in oversized_indexes:
            optimizations.append(IndexOptimizationResponse(
                index_id=str(uuid.uuid4()),
                table_name=oversized_index["table"],
                index_name=oversized_index["index"],
                optimization_type="oversized_index",
                current_size_mb=oversized_index["size_mb"],
                optimized_size_mb=oversized_index["size_mb"] * 0.5,
                improvement_percent=50,
                recommendation=f"Consider optimizing oversized index {oversized_index['index']}",
                estimated_impact="low"
            ))
        
        return optimizations
    
    except Exception as e:
        logger.error(f"Failed to optimize database indexes: {e}")
        return []


async def find_unused_indexes(
    db: AsyncSession
) -> List[Dict[str, Any]]:
    """Find unused indexes."""
    try:
        unused_query = text("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan,
                pg_size_pretty(pg_relation_size(indexrelid)) as size,
                pg_relation_size(indexrelid) / 1024 / 1024 as size_mb
            FROM pg_stat_user_indexes
            WHERE idx_scan = 0
            AND pg_relation_size(indexrelid) > 1024 * 1024  -- Larger than 1MB
            ORDER BY pg_relation_size(indexrelid) DESC
        """)
        
        result = await db.execute(unused_query)
        unused_indexes = [
            {
                "schema": row[0],
                "table": f"{row[0]}.{row[1]}",
                "index": row[2],
                "scans": row[3],
                "size": row[4],
                "size_mb": row[5]
            }
            for row in result.fetchall()
        ]
        
        return unused_indexes
    
    except Exception as e:
        logger.error(f"Failed to find unused indexes: {e}")
        return []


async def find_duplicate_indexes(
    db: AsyncSession
) -> List[Dict[str, Any]]:
    """Find duplicate indexes."""
    try:
        # This is a simplified version - in practice, you'd compare index definitions
        duplicate_query = text("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                pg_size_pretty(pg_relation_size(indexrelid)) as size,
                pg_relation_size(indexrelid) / 1024 / 1024 as size_mb
            FROM pg_stat_user_indexes
            WHERE indexname LIKE '%_idx_%'  -- Look for potential duplicates
            ORDER BY pg_relation_size(indexrelid) DESC
        """)
        
        result = await db.execute(duplicate_query)
        duplicate_indexes = [
            {
                "schema": row[0],
                "table": f"{row[0]}.{row[1]}",
                "index": row[2],
                "size": row[3],
                "size_mb": row[4]
            }
            for row in result.fetchall()
        ]
        
        return duplicate_indexes
    
    except Exception as e:
        logger.error(f"Failed to find duplicate indexes: {e}")
        return []


async def find_oversized_indexes(
    db: AsyncSession
) -> List[Dict[str, Any]]:
    """Find oversized indexes."""
    try:
        oversized_query = text("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                pg_size_pretty(pg_relation_size(indexrelid)) as size,
                pg_relation_size(indexrelid) / 1024 / 1024 as size_mb
            FROM pg_stat_user_indexes
            WHERE pg_relation_size(indexrelid) > 100 * 1024 * 1024  -- Larger than 100MB
            ORDER BY pg_relation_size(indexrelid) DESC
        """)
        
        result = await db.execute(oversized_query)
        oversized_indexes = [
            {
                "schema": row[0],
                "table": f"{row[0]}.{row[1]}",
                "index": row[2],
                "size": row[3],
                "size_mb": row[4]
            }
            for row in result.fetchall()
        ]
        
        return oversized_indexes
    
    except Exception as e:
        logger.error(f"Failed to find oversized indexes: {e}")
        return []


async def vacuum_and_analyze_database(
    db: AsyncSession,
    tables: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Run VACUUM and ANALYZE on database."""
    try:
        results = []
        
        if tables:
            # Vacuum specific tables
            for table in tables:
                try:
                    vacuum_query = text(f"VACUUM ANALYZE {table}")
                    await db.execute(vacuum_query)
                    results.append(f"VACUUM ANALYZE completed for {table}")
                except Exception as e:
                    results.append(f"Failed to vacuum {table}: {str(e)}")
        else:
            # Vacuum entire database
            try:
                vacuum_query = text("VACUUM ANALYZE")
                await db.execute(vacuum_query)
                results.append("VACUUM ANALYZE completed for entire database")
            except Exception as e:
                results.append(f"Failed to vacuum database: {str(e)}")
        
        # Update statistics
        try:
            analyze_query = text("ANALYZE")
            await db.execute(analyze_query)
            results.append("ANALYZE completed")
        except Exception as e:
            results.append(f"Failed to analyze: {str(e)}")
        
        return {
            "operations": results,
            "completed_at": datetime.utcnow(),
            "success": all("Failed" not in result for result in results)
        }
    
    except Exception as e:
        logger.error(f"Failed to vacuum and analyze database: {e}")
        return {
            "operations": [f"Failed to vacuum and analyze: {str(e)}"],
            "completed_at": datetime.utcnow(),
            "success": False
        }


async def optimize_database_connections(
    db: AsyncSession
) -> Dict[str, Any]:
    """Optimize database connections."""
    try:
        # Get current connection stats
        conn_query = text("""
            SELECT 
                count(*) as total_connections,
                count(*) FILTER (WHERE state = 'active') as active_connections,
                count(*) FILTER (WHERE state = 'idle') as idle_connections,
                count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction,
                count(*) FILTER (WHERE state = 'idle in transaction (aborted)') as idle_in_transaction_aborted
            FROM pg_stat_activity
        """)
        
        result = await db.execute(conn_query)
        conn_stats = result.fetchone()
        
        # Get long-running queries
        long_query = text("""
            SELECT 
                pid,
                state,
                query_start,
                state_change,
                query
            FROM pg_stat_activity
            WHERE state != 'idle'
            AND query_start < now() - interval '5 minutes'
            ORDER BY query_start
        """)
        
        long_result = await db.execute(long_query)
        long_queries = [
            {
                "pid": row[0],
                "state": row[1],
                "query_start": row[2],
                "state_change": row[3],
                "query": row[4][:100] + "..." if len(row[4]) > 100 else row[4]
            }
            for row in long_result.fetchall()
        ]
        
        # Get connection recommendations
        recommendations = []
        
        if conn_stats[2] > conn_stats[1] * 2:  # Too many idle connections
            recommendations.append("Consider reducing idle connection timeout")
        
        if conn_stats[3] > 5:  # Too many idle in transaction
            recommendations.append("Consider reducing idle in transaction timeout")
        
        if len(long_queries) > 0:
            recommendations.append(f"Found {len(long_queries)} long-running queries that may need optimization")
        
        return {
            "connection_stats": {
                "total_connections": conn_stats[0],
                "active_connections": conn_stats[1],
                "idle_connections": conn_stats[2],
                "idle_in_transaction": conn_stats[3],
                "idle_in_transaction_aborted": conn_stats[4]
            },
            "long_running_queries": long_queries,
            "recommendations": recommendations,
            "analyzed_at": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Failed to optimize database connections: {e}")
        return {
            "connection_stats": {},
            "long_running_queries": [],
            "recommendations": [f"Failed to analyze connections: {str(e)}"],
            "analyzed_at": datetime.utcnow()
        }


async def create_database_optimization_report(
    db: AsyncSession
) -> DatabaseOptimizationResponse:
    """Create comprehensive database optimization report."""
    try:
        # Get database statistics
        db_stats = await analyze_database_performance(db)
        
        # Get query optimizations
        query_optimizations = await optimize_database_queries(db)
        
        # Get index optimizations
        index_optimizations = await optimize_database_indexes(db)
        
        # Get connection optimizations
        connection_optimizations = await optimize_database_connections(db)
        
        # Calculate overall optimization score
        total_optimizations = len(query_optimizations) + len(index_optimizations)
        high_impact_optimizations = len([
            opt for opt in query_optimizations + index_optimizations
            if opt.estimated_impact == "high"
        ])
        
        optimization_score = min(100, (high_impact_optimizations * 20) + (total_optimizations * 5))
        
        # Generate recommendations
        recommendations = []
        
        if db_stats.dead_tuple_ratio > 10:
            recommendations.append("High dead tuple ratio detected. Consider running VACUUM more frequently.")
        
        if db_stats.active_connections > db_stats.total_connections * 0.8:
            recommendations.append("High connection utilization. Consider connection pooling optimization.")
        
        if len(query_optimizations) > 5:
            recommendations.append("Multiple slow queries detected. Consider query optimization.")
        
        if len(index_optimizations) > 3:
            recommendations.append("Index optimization opportunities found. Consider index cleanup.")
        
        return DatabaseOptimizationResponse(
            optimization_score=optimization_score,
            database_stats=db_stats,
            query_optimizations=query_optimizations,
            index_optimizations=index_optimizations,
            connection_optimizations=connection_optimizations,
            recommendations=recommendations,
            total_optimizations=total_optimizations,
            high_impact_optimizations=high_impact_optimizations,
            generated_at=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to create database optimization report: {e}")
        raise handle_internal_error(f"Failed to create database optimization report: {str(e)}")


async def apply_database_optimizations(
    optimizations: List[Dict[str, Any]],
    db: AsyncSession
) -> Dict[str, Any]:
    """Apply database optimizations."""
    try:
        applied_optimizations = []
        failed_optimizations = []
        
        for optimization in optimizations:
            try:
                optimization_type = optimization.get("type")
                
                if optimization_type == "vacuum":
                    result = await vacuum_and_analyze_database(db, optimization.get("tables"))
                    applied_optimizations.append({
                        "type": "vacuum",
                        "result": result
                    })
                
                elif optimization_type == "index_drop":
                    index_name = optimization.get("index_name")
                    drop_query = text(f"DROP INDEX IF EXISTS {index_name}")
                    await db.execute(drop_query)
                    applied_optimizations.append({
                        "type": "index_drop",
                        "index_name": index_name
                    })
                
                elif optimization_type == "index_create":
                    index_name = optimization.get("index_name")
                    table_name = optimization.get("table_name")
                    columns = optimization.get("columns")
                    create_query = text(f"CREATE INDEX {index_name} ON {table_name} ({columns})")
                    await db.execute(create_query)
                    applied_optimizations.append({
                        "type": "index_create",
                        "index_name": index_name,
                        "table_name": table_name
                    })
                
                else:
                    failed_optimizations.append({
                        "type": optimization_type,
                        "error": "Unknown optimization type"
                    })
            
            except Exception as e:
                failed_optimizations.append({
                    "type": optimization.get("type", "unknown"),
                    "error": str(e)
                })
        
        await db.commit()
        
        return {
            "applied_optimizations": applied_optimizations,
            "failed_optimizations": failed_optimizations,
            "total_applied": len(applied_optimizations),
            "total_failed": len(failed_optimizations),
            "completed_at": datetime.utcnow()
        }
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to apply database optimizations: {e}")
        raise handle_internal_error(f"Failed to apply database optimizations: {str(e)}")


async def monitor_database_health(
    db: AsyncSession
) -> Dict[str, Any]:
    """Monitor database health in real-time."""
    try:
        # Get current database metrics
        db_stats = await analyze_database_performance(db)
        
        # Check for health issues
        health_issues = []
        health_score = 100
        
        # Check connection health
        if db_stats.active_connections > db_stats.total_connections * 0.9:
            health_issues.append("High connection utilization")
            health_score -= 20
        
        # Check dead tuple ratio
        if db_stats.dead_tuple_ratio > 20:
            health_issues.append("High dead tuple ratio")
            health_score -= 15
        
        # Check for long-running queries
        if len(db_stats.slow_queries) > 5:
            health_issues.append("Multiple slow queries")
            health_score -= 10
        
        # Check for locks
        if db_stats.lock_stats.get("ExclusiveLock", 0) > 0:
            health_issues.append("Exclusive locks detected")
            health_score -= 25
        
        # Determine health status
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 75:
            status = "good"
        elif health_score >= 50:
            status = "fair"
        else:
            status = "poor"
        
        return {
            "status": status,
            "health_score": health_score,
            "health_issues": health_issues,
            "database_stats": db_stats,
            "monitored_at": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Failed to monitor database health: {e}")
        return {
            "status": "unknown",
            "health_score": 0,
            "health_issues": [f"Failed to monitor: {str(e)}"],
            "database_stats": None,
            "monitored_at": datetime.utcnow()
        }




