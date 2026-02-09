from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

# Constants
BUFFER_SIZE = 1024

import asyncio
import time
import psutil
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import logging
import json
from pathlib import Path
import argparse
from datetime import datetime, timedelta
        import importlib.util
from typing import Any, List, Dict, Optional
#!/usr/bin/env python3
"""
SQLAlchemy Performance Analyzer
===============================

Comprehensive performance analysis tool for SQLAlchemy 2.0 applications.
Features:
- Query performance benchmarking
- Connection pool analysis
- Memory usage monitoring
- Optimization recommendations
- Performance regression detection
"""


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """Metrics for a single query"""
    query_name: str
    query_sql: str
    execution_time: float
    memory_before: float
    memory_after: float
    memory_delta: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceReport:
    """Complete performance analysis report"""
    total_queries: int
    successful_queries: int
    failed_queries: int
    avg_execution_time: float
    median_execution_time: float
    max_execution_time: float
    min_execution_time: float
    total_memory_usage: float
    avg_memory_per_query: float
    slow_queries: List[QueryMetrics]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class SQLAlchemyPerformanceAnalyzer:
    """SQLAlchemy performance analysis and optimization tool"""
    
    def __init__(self, session_factory, slow_query_threshold: float = 1.0):
        
    """__init__ function."""
self.session_factory = session_factory
        self.slow_query_threshold = slow_query_threshold
        self.metrics: List[QueryMetrics] = []
        self.process = psutil.Process()
        
        # Performance thresholds
        self.thresholds = {
            'slow_query': 1.0,  # seconds
            'memory_spike': 50.0,  # MB
            'connection_timeout': 30.0,  # seconds
            'pool_exhaustion': 0.8,  # 80% pool utilization
        }
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    @asynccontextmanager
    async def monitor_query(self, query_name: str, query_sql: str = ""):
        """Context manager to monitor query performance"""
        memory_before = self.get_memory_usage()
        start_time = time.time()
        success = False
        error_message = None
        
        try:
            yield
            success = True
        except Exception as e:
            error_message = str(e)
            raise
        finally:
            execution_time = time.time() - start_time
            memory_after = self.get_memory_usage()
            memory_delta = memory_after - memory_before
            
            metric = QueryMetrics(
                query_name=query_name,
                query_sql=query_sql,
                execution_time=execution_time,
                memory_before=memory_before,
                memory_after=memory_after,
                memory_delta=memory_delta,
                success=success,
                error_message=error_message
            )
            
            self.metrics.append(metric)
            
            if execution_time > self.slow_query_threshold:
                logger.warning(f"Slow query detected: {query_name} took {execution_time:.2f}s")
    
    async def benchmark_single_query(self, query_name: str, query_func, *args, **kwargs) -> QueryMetrics:
        """Benchmark a single query function"""
        async with self.monitor_query(query_name):
            return await query_func(*args, **kwargs)
    
    async def benchmark_query_batch(self, queries: List[Tuple[str, callable, tuple, dict]]) -> List[QueryMetrics]:
        """Benchmark multiple queries"""
        results = []
        
        for query_name, query_func, args, kwargs in queries:
            try:
                async with self.monitor_query(query_name):
                    await query_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Query {query_name} failed: {e}")
        
        return self.metrics[-len(queries):]
    
    async def benchmark_common_operations(self) -> Dict[str, Any]:
        """Benchmark common database operations"""
        benchmarks = {}
        
        # Sample data for testing
        test_data = [
            {"name": f"User{i}", "email": f"user{i}@example.com"} 
            for i in range(100)
        ]
        
        # Insert benchmark
        async def insert_benchmark():
            
    """insert_benchmark function."""
async with self.session_factory() as session:
                for data in test_data:
                    # This would be your actual model
                    # user = User(**data)
                    # session.add(user)
                    pass
                await session.commit()
        
        async with self.monitor_query("bulk_insert_100_users"):
            await insert_benchmark()
        
        benchmarks["insert"] = {
            "operation": "bulk_insert_100_users",
            "execution_time": self.metrics[-1].execution_time,
            "memory_usage": self.metrics[-1].memory_delta
        }
        
        # Select benchmark
        async def select_benchmark():
            
    """select_benchmark function."""
async with self.session_factory() as session:
                # This would be your actual query
                # result = await session.execute(select(User).limit(100))
                # users = result.scalars().all()
                pass
        
        async with self.monitor_query("select_100_users"):
            await select_benchmark()
        
        benchmarks["select"] = {
            "operation": "select_100_users",
            "execution_time": self.metrics[-1].execution_time,
            "memory_usage": self.metrics[-1].memory_delta
        }
        
        # Update benchmark
        async def update_benchmark():
            
    """update_benchmark function."""
async with self.session_factory() as session:
                # This would be your actual update
                # await session.execute(update(User).where(User.id == 1).values(name="Updated"))
                # await session.commit()
                pass
        
        async with self.monitor_query("update_user"):
            await update_benchmark()
        
        benchmarks["update"] = {
            "operation": "update_user",
            "execution_time": self.metrics[-1].execution_time,
            "memory_usage": self.metrics[-1].memory_delta
        }
        
        return benchmarks
    
    async def analyze_connection_pool(self) -> Dict[str, Any]:
        """Analyze connection pool performance"""
        pool_analysis = {
            "pool_size": 0,
            "checked_out_connections": 0,
            "available_connections": 0,
            "overflow_connections": 0,
            "connection_wait_time": 0.0,
            "pool_exhaustion_events": 0
        }
        
        # This would require access to the engine's pool
        # For now, we'll simulate the analysis
        try:
            # Get pool info from engine
            # engine = self.session_factory.kw.get('bind')
            # pool = engine.pool
            # pool_analysis.update({
            #     "pool_size": pool.size(),
            #     "checked_out_connections": pool.checkedout(),
            #     "available_connections": pool.checkedin(),
            #     "overflow_connections": pool.overflow()
            # })
            pass
        except Exception as e:
            logger.warning(f"Could not analyze connection pool: {e}")
        
        return pool_analysis
    
    def generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on metrics"""
        recommendations = []
        
        if not self.metrics:
            return ["No metrics available for analysis"]
        
        # Analyze execution times
        execution_times = [m.execution_time for m in self.metrics if m.success]
        if execution_times:
            avg_time = statistics.mean(execution_times)
            max_time = max(execution_times)
            
            if avg_time > 0.5:
                recommendations.append(f"Average query time is {avg_time:.2f}s - consider query optimization")
            
            if max_time > 5.0:
                recommendations.append(f"Maximum query time is {max_time:.2f}s - investigate slow queries")
        
        # Analyze memory usage
        memory_deltas = [m.memory_delta for m in self.metrics if m.success]
        if memory_deltas:
            avg_memory = statistics.mean(memory_deltas)
            max_memory = max(memory_deltas)
            
            if avg_memory > 10.0:
                recommendations.append(f"Average memory usage per query is {avg_memory:.2f}MB - consider memory optimization")
            
            if max_memory > 50.0:
                recommendations.append(f"Maximum memory spike is {max_memory:.2f}MB - investigate memory leaks")
        
        # Analyze failure rate
        failed_queries = [m for m in self.metrics if not m.success]
        failure_rate = len(failed_queries) / len(self.metrics) if self.metrics else 0
        
        if failure_rate > 0.05:  # 5% failure rate
            recommendations.append(f"Query failure rate is {failure_rate:.1%} - investigate error handling")
        
        # General recommendations
        recommendations.extend([
            "Consider implementing query result caching for frequently accessed data",
            "Use bulk operations for large datasets",
            "Implement connection pooling optimization",
            "Add database indexes for frequently queried columns",
            "Consider read replicas for read-heavy workloads"
        ])
        
        return recommendations
    
    def generate_report(self) -> PerformanceReport:
        """Generate comprehensive performance report"""
        if not self.metrics:
            return PerformanceReport(
                total_queries=0,
                successful_queries=0,
                failed_queries=0,
                avg_execution_time=0.0,
                median_execution_time=0.0,
                max_execution_time=0.0,
                min_execution_time=0.0,
                total_memory_usage=0.0,
                avg_memory_per_query=0.0,
                slow_queries=[],
                recommendations=["No metrics available"]
            )
        
        successful_metrics = [m for m in self.metrics if m.success]
        failed_metrics = [m for m in self.metrics if not m.success]
        
        execution_times = [m.execution_time for m in successful_metrics]
        memory_deltas = [m.memory_delta for m in successful_metrics]
        
        slow_queries = [m for m in successful_metrics if m.execution_time > self.slow_query_threshold]
        
        return PerformanceReport(
            total_queries=len(self.metrics),
            successful_queries=len(successful_metrics),
            failed_queries=len(failed_metrics),
            avg_execution_time=statistics.mean(execution_times) if execution_times else 0.0,
            median_execution_time=statistics.median(execution_times) if execution_times else 0.0,
            max_execution_time=max(execution_times) if execution_times else 0.0,
            min_execution_time=min(execution_times) if execution_times else 0.0,
            total_memory_usage=sum(memory_deltas) if memory_deltas else 0.0,
            avg_memory_per_query=statistics.mean(memory_deltas) if memory_deltas else 0.0,
            slow_queries=slow_queries,
            recommendations=self.generate_recommendations()
        )
    
    def save_report(self, report: PerformanceReport, output_path: str):
        """Save performance report to file"""
        report_data = {
            "timestamp": report.timestamp.isoformat(),
            "summary": {
                "total_queries": report.total_queries,
                "successful_queries": report.successful_queries,
                "failed_queries": report.failed_queries,
                "avg_execution_time": report.avg_execution_time,
                "median_execution_time": report.median_execution_time,
                "max_execution_time": report.max_execution_time,
                "min_execution_time": report.min_execution_time,
                "total_memory_usage": report.total_memory_usage,
                "avg_memory_per_query": report.avg_memory_per_query,
            },
            "slow_queries": [
                {
                    "query_name": q.query_name,
                    "execution_time": q.execution_time,
                    "memory_delta": q.memory_delta,
                    "timestamp": q.timestamp.isoformat()
                }
                for q in report.slow_queries
            ],
            "recommendations": report.recommendations
        }
        
        with open(output_path, 'w') as f:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Performance report saved to {output_path}")
    
    def print_report(self, report: PerformanceReport):
        """Print performance report to console"""
        print("=" * 80)
        print("SQLAlchemy Performance Analysis Report")
        print("=" * 80)
        print(f"Generated: {report.timestamp}")
        print()
        
        print("📊 SUMMARY")
        print("-" * 40)
        print(f"Total Queries: {report.total_queries}")
        print(f"Successful: {report.successful_queries}")
        print(f"Failed: {report.failed_queries}")
        print(f"Success Rate: {report.successful_queries/report.total_queries*100:.1f}%" if report.total_queries > 0 else "N/A")
        print()
        
        print("⏱️ EXECUTION TIMES")
        print("-" * 40)
        print(f"Average: {report.avg_execution_time:.3f}s")
        print(f"Median: {report.median_execution_time:.3f}s")
        print(f"Minimum: {report.min_execution_time:.3f}s")
        print(f"Maximum: {report.max_execution_time:.3f}s")
        print()
        
        print("💾 MEMORY USAGE")
        print("-" * 40)
        print(f"Total Memory Used: {report.total_memory_usage:.2f}MB")
        print(f"Average per Query: {report.avg_memory_per_query:.2f}MB")
        print()
        
        if report.slow_queries:
            print("🐌 SLOW QUERIES")
            print("-" * 40)
            for query in report.slow_queries[:5]:  # Show top 5
                print(f"• {query.query_name}: {query.execution_time:.3f}s")
            print()
        
        print("💡 RECOMMENDATIONS")
        print("-" * 40)
        for i, rec in enumerate(report.recommendations, 1):
            print(f"{i}. {rec}")
        print()


class PerformanceMonitor:
    """Real-time performance monitoring"""
    
    def __init__(self, analyzer: SQLAlchemyPerformanceAnalyzer):
        
    """__init__ function."""
self.analyzer = analyzer
        self.monitoring = False
        self.metrics_buffer = []
    
    async def start_monitoring(self, duration: int = 300):
        """Start real-time performance monitoring"""
        self.monitoring = True
        start_time = time.time()
        
        logger.info(f"Starting performance monitoring for {duration} seconds")
        
        while self.monitoring and (time.time() - start_time) < duration:
            # Collect current metrics
            current_memory = self.analyzer.get_memory_usage()
            
            # Store metrics
            self.metrics_buffer.append({
                "timestamp": datetime.now(),
                "memory_usage": current_memory,
                "active_queries": len(self.analyzer.metrics)
            })
            
            # Wait before next collection
            await asyncio.sleep(5)  # Collect every 5 seconds
        
        self.monitoring = False
        logger.info("Performance monitoring stopped")
    
    def stop_monitoring(self) -> Any:
        """Stop real-time monitoring"""
        self.monitoring = False
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get summary of monitoring data"""
        if not self.metrics_buffer:
            return {"error": "No monitoring data available"}
        
        memory_usage = [m["memory_usage"] for m in self.metrics_buffer]
        
        return {
            "monitoring_duration": len(self.metrics_buffer) * 5,  # seconds
            "avg_memory_usage": statistics.mean(memory_usage),
            "max_memory_usage": max(memory_usage),
            "min_memory_usage": min(memory_usage),
            "total_metrics_collected": len(self.metrics_buffer)
        }


async def main():
    """Main entry point for performance analysis"""
    parser = argparse.ArgumentParser(description='SQLAlchemy Performance Analyzer')
    parser.add_argument('--session-factory', required=True, help='Path to session factory module')
    parser.add_argument('--output', default='performance_report.json', help='Output file for report')
    parser.add_argument('--monitor', type=int, help='Enable real-time monitoring for N seconds')
    parser.add_argument('--slow-threshold', type=float, default=1.0, help='Slow query threshold in seconds')
    
    args = parser.parse_args()
    
    # Import session factory
    try:
        spec = importlib.util.spec_from_file_location("session_factory", args.session_factory)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        session_factory = module.session_factory
    except Exception as e:
        logger.error(f"Failed to import session factory: {e}")
        return
    
    # Create analyzer
    analyzer = SQLAlchemyPerformanceAnalyzer(
        session_factory=session_factory,
        slow_query_threshold=args.slow_threshold
    )
    
    try:
        # Run benchmarks
        logger.info("Running performance benchmarks...")
        benchmarks = await analyzer.benchmark_common_operations()
        
        # Generate report
        report = analyzer.generate_report()
        
        # Print report
        analyzer.print_report(report)
        
        # Save report
        analyzer.save_report(report, args.output)
        
        # Real-time monitoring if requested
        if args.monitor:
            monitor = PerformanceMonitor(analyzer)
            await monitor.start_monitoring(args.monitor)
            
            # Print monitoring summary
            summary = monitor.get_monitoring_summary()
            print("\n📈 MONITORING SUMMARY")
            print("-" * 40)
            for key, value in summary.items():
                print(f"{key}: {value}")
        
    except Exception as e:
        logger.error(f"Performance analysis failed: {e}")


match __name__:
    case '__main__':
    asyncio.run(main()) 