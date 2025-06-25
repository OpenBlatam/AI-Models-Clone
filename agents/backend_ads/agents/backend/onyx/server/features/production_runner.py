#!/usr/bin/env python3
"""
Production Runner for Onyx Features - Optimized Deployment.

Production-ready runner script that demonstrates the full power of the
optimized Onyx Features system with comprehensive monitoring and benchmarking.
"""

import asyncio
import argparse
import time
import sys
from pathlib import Path
from typing import Dict, Any, List

import structlog
import uvicorn

# Import our optimized modules
from .startup import initialize_onyx_optimizations, shutdown_onyx_optimizations
from .benchmark import create_benchmark_suite
from .performance_optimizers import OptimizationConfig
from .config import get_config, Environment
from .app import create_app

# Configure logging
logger = structlog.get_logger(__name__)


class ProductionRunner:
    """Production runner with full optimization capabilities."""
    
    def __init__(self, optimization_config: OptimizationConfig = None):
        self.optimization_config = optimization_config or OptimizationConfig()
        self.app_config = get_config()
        self.benchmark_suite = None
        
    async def run_system_check(self) -> Dict[str, Any]:
        """Run comprehensive system check before deployment."""
        logger.info("🔍 Running production system check...")
        
        # Initialize optimizations
        optimization_report = await initialize_onyx_optimizations(self.optimization_config)
        
        # Run benchmarks
        self.benchmark_suite = create_benchmark_suite()
        benchmark_results = await self.benchmark_suite.run_all_benchmarks()
        
        # Generate reports
        benchmark_report = self.benchmark_suite.generate_benchmark_report(benchmark_results)
        
        system_check = {
            "optimization_report": optimization_report,
            "benchmark_results": benchmark_results,
            "benchmark_report": benchmark_report,
            "system_ready": self._evaluate_system_readiness(optimization_report, benchmark_results)
        }
        
        return system_check
    
    def _evaluate_system_readiness(self, opt_report: Dict, bench_results: Dict) -> Dict[str, Any]:
        """Evaluate if system is ready for production deployment."""
        # Check optimization grade
        grade = opt_report.get('performance_grade', 'D')
        optimization_score = self._grade_to_score(grade)
        
        # Check benchmark performance
        speedups = []
        for category, tests in bench_results.items():
            for test_name, result in tests.items():
                if hasattr(result, 'details') and 'speedup' in result.details:
                    speedup_str = result.details['speedup'].replace('x', '')
                    try:
                        speedups.append(float(speedup_str))
                    except ValueError:
                        pass
        
        avg_speedup = sum(speedups) / len(speedups) if speedups else 1.0
        
        # Overall readiness assessment
        ready = optimization_score >= 0.7 and avg_speedup >= 1.5
        
        return {
            "ready_for_production": ready,
            "optimization_score": optimization_score,
            "average_speedup": avg_speedup,
            "recommendation": self._get_recommendation(optimization_score, avg_speedup),
            "missing_optimizations": self._get_missing_optimizations(opt_report)
        }
    
    def _grade_to_score(self, grade: str) -> float:
        """Convert grade to numeric score."""
        grade_map = {
            "A+": 1.0, "A": 0.9, "B": 0.8, "C": 0.7, "D": 0.6
        }
        for g, score in grade_map.items():
            if g in grade:
                return score
        return 0.5
    
    def _get_recommendation(self, opt_score: float, speedup: float) -> str:
        """Get deployment recommendation."""
        if opt_score >= 0.9 and speedup >= 2.0:
            return "🚀 EXCELLENT - Ready for high-performance production deployment"
        elif opt_score >= 0.8 and speedup >= 1.5:
            return "✅ GOOD - Ready for production with minor optimizations pending"
        elif opt_score >= 0.7 and speedup >= 1.2:
            return "⚠️ ACCEPTABLE - Production ready but consider installing missing libraries"
        else:
            return "❌ NOT READY - Install optimization libraries before production deployment"
    
    def _get_missing_optimizations(self, opt_report: Dict) -> List[str]:
        """Get list of missing critical optimizations."""
        critical_features = ["uvloop", "orjson", "numba", "polars"]
        features = opt_report.get('features_available', {})
        
        missing = []
        for feature in critical_features:
            if not features.get(feature, False):
                missing.append(feature)
        
        return missing
    
    async def run_performance_demo(self) -> None:
        """Run a performance demonstration."""
        logger.info("🎯 Running performance demonstration...")
        
        from .data_processing import create_data_processor, process_json_data_fast
        from .optimization import FastSerializer, FastHasher
        
        # Demonstrate serialization performance
        test_data = [{"id": i, "value": f"test_{i}"} for i in range(10000)]
        
        start_time = time.perf_counter()
        serialized = FastSerializer.serialize_json(test_data)
        serialization_time = (time.perf_counter() - start_time) * 1000
        
        logger.info(f"Serialized 10k objects in {serialization_time:.2f}ms")
        
        # Demonstrate hash performance
        test_strings = [f"test_string_{i}" for i in range(10000)]
        
        start_time = time.perf_counter()
        hashes = [FastHasher.hash_fast(s) for s in test_strings]
        hash_time = (time.perf_counter() - start_time) * 1000
        
        logger.info(f"Hashed 10k strings in {hash_time:.2f}ms")
        
        # Demonstrate data processing
        start_time = time.perf_counter()
        result = await process_json_data_fast(test_data, ["filter_nulls", "normalize"])
        processing_time = (time.perf_counter() - start_time) * 1000
        
        logger.info(f"Processed 10k records in {processing_time:.2f}ms")
        
        total_demo_time = serialization_time + hash_time + processing_time
        logger.info(f"🎉 Demo completed in {total_demo_time:.2f}ms total")
    
    async def start_production_server(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Start the production server with all optimizations."""
        logger.info("🚀 Starting optimized production server...")
        
        # Create optimized app
        app = create_app(self.app_config)
        
        # Configure uvicorn with optimizations
        uvicorn_config = {
            "host": host,
            "port": port,
            "loop": "uvloop" if self.optimization_config.enable_jit else "asyncio",
            "http": "httptools",
            "log_level": "info",
            "access_log": True
        }
        
        if self.app_config.environment == Environment.PRODUCTION:
            uvicorn_config.update({
                "workers": self.optimization_config.max_workers,
                "worker_class": "uvicorn.workers.UvicornWorker"
            })
        
        logger.info(f"Server starting on {host}:{port} with {uvicorn_config.get('workers', 1)} workers")
        
        # Start server
        server = uvicorn.Server(uvicorn.Config(app, **uvicorn_config))
        await server.serve()


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Onyx Features Production Runner")
    parser.add_argument("--mode", choices=["check", "demo", "serve", "benchmark"], 
                       default="check", help="Operation mode")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--enable-gpu", action="store_true", help="Enable GPU acceleration")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum workers")
    parser.add_argument("--output-report", help="Save reports to file")
    
    args = parser.parse_args()
    
    # Create optimization config
    opt_config = OptimizationConfig(
        enable_gpu=args.enable_gpu,
        max_workers=args.max_workers
    )
    
    runner = ProductionRunner(opt_config)
    
    try:
        if args.mode == "check":
            print("🔍 Running system check...")
            system_check = await runner.run_system_check()
            
            print("\n" + "="*60)
            print("PRODUCTION READINESS REPORT")
            print("="*60)
            
            readiness = system_check["system_ready"]
            print(f"Status: {readiness['recommendation']}")
            print(f"Optimization Score: {readiness['optimization_score']:.1%}")
            print(f"Average Speedup: {readiness['average_speedup']:.2f}x")
            
            if readiness["missing_optimizations"]:
                print(f"\nMissing optimizations: {', '.join(readiness['missing_optimizations'])}")
                print("Install with: pip install " + " ".join(readiness['missing_optimizations']))
            
            print(f"\nDetailed report:")
            print(system_check["benchmark_report"])
            
            if args.output_report:
                with open(args.output_report, 'w') as f:
                    f.write(system_check["benchmark_report"])
                print(f"\nReport saved to: {args.output_report}")
        
        elif args.mode == "demo":
            await runner.run_system_check()  # Initialize first
            await runner.run_performance_demo()
        
        elif args.mode == "benchmark":
            print("🏃 Running comprehensive benchmarks...")
            await runner.run_system_check()
            print("✅ Benchmarks completed - check system check results above")
        
        elif args.mode == "serve":
            system_check = await runner.run_system_check()
            readiness = system_check["system_ready"]
            
            if not readiness["ready_for_production"]:
                print("⚠️ WARNING: System not optimally configured for production")
                print(readiness["recommendation"])
                
                response = input("Continue anyway? (y/N): ")
                if response.lower() != 'y':
                    print("Deployment cancelled. Install missing optimizations first.")
                    sys.exit(1)
            
            await runner.start_production_server(args.host, args.port)
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        logger.error(f"Production runner failed: {e}")
        sys.exit(1)
    finally:
        await shutdown_onyx_optimizations()


if __name__ == "__main__":
    # Add current directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
    
    asyncio.run(main())


# Export for programmatic use
__all__ = ["ProductionRunner"] 