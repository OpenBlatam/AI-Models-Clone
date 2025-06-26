"""
Copywriting Model Benchmark - Performance Testing for AI Content Generation.

Comprehensive benchmarking suite specifically for testing copywriting model
performance, accuracy, and optimization in production environments.
"""

import asyncio
import time
import statistics
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import numpy as np

import structlog
from .copywriting_model import (
    CopywritingModel, ContentRequest, ContentType, ContentTone, 
    ContentLanguage, create_copywriting_model
)
from .benchmark import BenchmarkResult

logger = structlog.get_logger(__name__)


@dataclass
class CopywritingBenchmarkResult:
    """Specialized benchmark result for copywriting operations."""
    test_name: str
    avg_generation_time_ms: float
    median_generation_time_ms: float
    p95_generation_time_ms: float
    avg_content_length: int
    avg_readability_score: float
    avg_engagement_prediction: float
    success_rate: float
    error_count: int
    throughput_content_per_second: float
    model_distribution: Dict[str, int]  # Which AI models were used
    details: Dict[str, Any]


class CopywritingSpeedBenchmark:
    """Benchmark copywriting generation speed and throughput."""
    
    def __init__(self):
        self.copywriting_model = create_copywriting_model()
        self.test_requests = self._generate_test_requests()
    
    def _generate_test_requests(self) -> List[ContentRequest]:
        """Generate diverse test requests for benchmarking."""
        requests = []
        
        # Test different content types and complexity levels
        test_scenarios = [
            {
                "content_type": ContentType.AD_COPY,
                "target_audience": "Young professionals aged 25-35",
                "key_message": "Revolutionary productivity app that saves 2 hours daily",
                "tone": ContentTone.URGENT,
                "keywords": ["productivity", "efficiency", "time-saving"]
            },
            {
                "content_type": ContentType.SOCIAL_POST,
                "target_audience": "Tech enthusiasts and early adopters",
                "key_message": "AI-powered code optimization tool launches today",
                "tone": ContentTone.PLAYFUL,
                "keywords": ["AI", "coding", "optimization", "developer"]
            },
            {
                "content_type": ContentType.EMAIL_SUBJECT,
                "target_audience": "B2B decision makers",
                "key_message": "Reduce operational costs by 40% with our solution",
                "tone": ContentTone.PROFESSIONAL,
                "keywords": ["cost-reduction", "efficiency", "ROI"]
            },
            {
                "content_type": ContentType.PRODUCT_DESCRIPTION,
                "target_audience": "Health-conscious consumers",
                "key_message": "Organic superfood blend with 20+ vitamins and minerals",
                "tone": ContentTone.FRIENDLY,
                "keywords": ["organic", "superfood", "healthy", "vitamins"]
            },
            {
                "content_type": ContentType.BLOG_TITLE,
                "target_audience": "Digital marketers and content creators",
                "key_message": "10 proven strategies to increase content engagement",
                "tone": ContentTone.AUTHORITATIVE,
                "keywords": ["marketing", "engagement", "content", "strategy"]
            }
        ]
        
        # Create multiple requests for each scenario
        for scenario in test_scenarios:
            for i in range(20):  # 20 variations per scenario
                request = ContentRequest(
                    content_type=scenario["content_type"],
                    target_audience=scenario["target_audience"],
                    key_message=scenario["key_message"],
                    tone=scenario["tone"],
                    keywords=scenario["keywords"],
                    call_to_action=f"Learn more today! #{i}",
                    max_length=200 if scenario["content_type"] == ContentType.AD_COPY else None,
                    include_hashtags=scenario["content_type"] == ContentType.SOCIAL_POST,
                    include_emojis=scenario["tone"] == ContentTone.PLAYFUL
                )
                requests.append(request)
        
        return requests
    
    async def benchmark_sequential_generation(self) -> CopywritingBenchmarkResult:
        """Benchmark sequential content generation."""
        generation_times = []
        content_lengths = []
        readability_scores = []
        engagement_predictions = []
        model_usage = {}
        errors = 0
        
        start_time = time.perf_counter()
        
        for request in self.test_requests:
            try:
                gen_start = time.perf_counter()
                generated = await self.copywriting_model.create_content(request)
                gen_time = (time.perf_counter() - gen_start) * 1000
                
                generation_times.append(gen_time)
                content_lengths.append(len(generated.content))
                
                # Track model usage
                model_usage[generated.model_used] = model_usage.get(generated.model_used, 0) + 1
                
                # Track metrics if available
                if generated.metrics:
                    readability_scores.append(generated.metrics.readability_score)
                    engagement_predictions.append(generated.metrics.engagement_prediction)
                
            except Exception as e:
                errors += 1
                logger.warning(f"Generation failed: {e}")
        
        total_time = time.perf_counter() - start_time
        successful_generations = len(generation_times)
        
        return CopywritingBenchmarkResult(
            test_name="Sequential Generation",
            avg_generation_time_ms=statistics.mean(generation_times) if generation_times else 0,
            median_generation_time_ms=statistics.median(generation_times) if generation_times else 0,
            p95_generation_time_ms=np.percentile(generation_times, 95) if generation_times else 0,
            avg_content_length=int(statistics.mean(content_lengths)) if content_lengths else 0,
            avg_readability_score=statistics.mean(readability_scores) if readability_scores else 0,
            avg_engagement_prediction=statistics.mean(engagement_predictions) if engagement_predictions else 0,
            success_rate=successful_generations / len(self.test_requests) if self.test_requests else 0,
            error_count=errors,
            throughput_content_per_second=successful_generations / total_time if total_time > 0 else 0,
            model_distribution=model_usage,
            details={
                "total_requests": len(self.test_requests),
                "total_time_seconds": total_time,
                "generation_time_std": statistics.stdev(generation_times) if len(generation_times) > 1 else 0
            }
        )
    
    async def benchmark_concurrent_generation(self, concurrency: int = 10) -> CopywritingBenchmarkResult:
        """Benchmark concurrent content generation."""
        # Limit requests for concurrent testing
        concurrent_requests = self.test_requests[:50]  # Use subset for concurrent testing
        
        generation_times = []
        content_lengths = []
        readability_scores = []
        engagement_predictions = []
        model_usage = {}
        errors = 0
        
        async def generate_content(request):
            try:
                gen_start = time.perf_counter()
                generated = await self.copywriting_model.create_content(request)
                gen_time = (time.perf_counter() - gen_start) * 1000
                
                return {
                    "success": True,
                    "generation_time": gen_time,
                    "content_length": len(generated.content),
                    "model_used": generated.model_used,
                    "metrics": generated.metrics
                }
            except Exception as e:
                logger.warning(f"Concurrent generation failed: {e}")
                return {"success": False, "error": str(e)}
        
        # Run concurrent generation
        start_time = time.perf_counter()
        
        semaphore = asyncio.Semaphore(concurrency)
        
        async def controlled_generate(request):
            async with semaphore:
                return await generate_content(request)
        
        tasks = [controlled_generate(req) for req in concurrent_requests]
        results = await asyncio.gather(*tasks)
        
        total_time = time.perf_counter() - start_time
        
        # Process results
        successful_results = [r for r in results if r["success"]]
        errors = len([r for r in results if not r["success"]])
        
        for result in successful_results:
            generation_times.append(result["generation_time"])
            content_lengths.append(result["content_length"])
            model_usage[result["model_used"]] = model_usage.get(result["model_used"], 0) + 1
            
            if result["metrics"]:
                readability_scores.append(result["metrics"].readability_score)
                engagement_predictions.append(result["metrics"].engagement_prediction)
        
        return CopywritingBenchmarkResult(
            test_name=f"Concurrent Generation (concurrency={concurrency})",
            avg_generation_time_ms=statistics.mean(generation_times) if generation_times else 0,
            median_generation_time_ms=statistics.median(generation_times) if generation_times else 0,
            p95_generation_time_ms=np.percentile(generation_times, 95) if generation_times else 0,
            avg_content_length=int(statistics.mean(content_lengths)) if content_lengths else 0,
            avg_readability_score=statistics.mean(readability_scores) if readability_scores else 0,
            avg_engagement_prediction=statistics.mean(engagement_predictions) if engagement_predictions else 0,
            success_rate=len(successful_results) / len(concurrent_requests) if concurrent_requests else 0,
            error_count=errors,
            throughput_content_per_second=len(successful_results) / total_time if total_time > 0 else 0,
            model_distribution=model_usage,
            details={
                "concurrency_level": concurrency,
                "total_requests": len(concurrent_requests),
                "total_time_seconds": total_time
            }
        )


class CopywritingQualityBenchmark:
    """Benchmark copywriting content quality and consistency."""
    
    def __init__(self):
        self.copywriting_model = create_copywriting_model()
    
    async def benchmark_content_consistency(self) -> CopywritingBenchmarkResult:
        """Test consistency of generated content for similar requests."""
        base_request = ContentRequest(
            content_type=ContentType.AD_COPY,
            target_audience="Small business owners",
            key_message="Affordable CRM solution that grows with your business",
            tone=ContentTone.PROFESSIONAL,
            keywords=["CRM", "affordable", "business growth"],
            call_to_action="Start your free trial today"
        )
        
        # Generate multiple variations
        variations = []
        generation_times = []
        
        for i in range(20):
            start_time = time.perf_counter()
            generated = await self.copywriting_model.create_content(base_request)
            gen_time = (time.perf_counter() - start_time) * 1000
            
            variations.append({
                "content": generated.content,
                "length": len(generated.content),
                "generation_time": gen_time,
                "metrics": generated.metrics
            })
            generation_times.append(gen_time)
        
        # Analyze consistency
        lengths = [v["length"] for v in variations]
        readability_scores = [v["metrics"].readability_score for v in variations if v["metrics"]]
        engagement_scores = [v["metrics"].engagement_prediction for v in variations if v["metrics"]]
        
        length_std = statistics.stdev(lengths) if len(lengths) > 1 else 0
        readability_std = statistics.stdev(readability_scores) if len(readability_scores) > 1 else 0
        engagement_std = statistics.stdev(engagement_scores) if len(engagement_scores) > 1 else 0
        
        # Calculate consistency score (lower std deviation = higher consistency)
        consistency_score = 1.0 / (1.0 + length_std/100 + readability_std/10 + engagement_std)
        
        return CopywritingBenchmarkResult(
            test_name="Content Consistency",
            avg_generation_time_ms=statistics.mean(generation_times),
            median_generation_time_ms=statistics.median(generation_times),
            p95_generation_time_ms=np.percentile(generation_times, 95),
            avg_content_length=int(statistics.mean(lengths)),
            avg_readability_score=statistics.mean(readability_scores) if readability_scores else 0,
            avg_engagement_prediction=statistics.mean(engagement_scores) if engagement_scores else 0,
            success_rate=1.0,  # All generations succeeded
            error_count=0,
            throughput_content_per_second=len(variations) / sum(generation_times) * 1000,
            model_distribution={"consistency_test": len(variations)},
            details={
                "consistency_score": consistency_score,
                "length_std_deviation": length_std,
                "readability_std_deviation": readability_std,
                "engagement_std_deviation": engagement_std,
                "unique_content_ratio": len(set(v["content"] for v in variations)) / len(variations)
            }
        )
    
    async def benchmark_ab_test_performance(self) -> CopywritingBenchmarkResult:
        """Benchmark A/B test variant generation performance."""
        request = ContentRequest(
            content_type=ContentType.EMAIL_SUBJECT,
            target_audience="E-commerce professionals",
            key_message="Boost your online sales with AI-powered recommendations",
            tone=ContentTone.URGENT,
            keywords=["sales", "AI", "recommendations", "e-commerce"]
        )
        
        ab_tests = []
        generation_times = []
        
        # Generate multiple A/B tests
        for i in range(10):
            start_time = time.perf_counter()
            variants = await self.copywriting_model.a_b_test_content(request, variants=3)
            gen_time = (time.perf_counter() - start_time) * 1000
            
            ab_tests.append(variants)
            generation_times.append(gen_time)
        
        # Analyze A/B test quality
        total_variants = sum(len(test) for test in ab_tests)
        avg_variants_per_test = total_variants / len(ab_tests)
        
        # Check diversity of variants
        all_content = []
        all_confidences = []
        
        for test in ab_tests:
            test_content = [v.content for v in test]
            test_confidences = [v.confidence_score for v in test]
            
            all_content.extend(test_content)
            all_confidences.extend(test_confidences)
        
        unique_content_ratio = len(set(all_content)) / len(all_content)
        
        return CopywritingBenchmarkResult(
            test_name="A/B Test Performance",
            avg_generation_time_ms=statistics.mean(generation_times),
            median_generation_time_ms=statistics.median(generation_times),
            p95_generation_time_ms=np.percentile(generation_times, 95),
            avg_content_length=int(statistics.mean([len(c) for c in all_content])),
            avg_readability_score=0,  # Not applicable for this test
            avg_engagement_prediction=statistics.mean(all_confidences),
            success_rate=1.0,
            error_count=0,
            throughput_content_per_second=total_variants / sum(generation_times) * 1000,
            model_distribution={"ab_test": len(ab_tests)},
            details={
                "avg_variants_per_test": avg_variants_per_test,
                "unique_content_ratio": unique_content_ratio,
                "total_variants_generated": total_variants,
                "diversity_score": unique_content_ratio
            }
        )


class ComprehensiveCopywritingBenchmark:
    """Main copywriting benchmark orchestrator."""
    
    def __init__(self):
        self.speed_benchmark = CopywritingSpeedBenchmark()
        self.quality_benchmark = CopywritingQualityBenchmark()
    
    async def run_all_benchmarks(self) -> Dict[str, CopywritingBenchmarkResult]:
        """Run comprehensive copywriting benchmarks."""
        logger.info("🚀 Starting comprehensive copywriting benchmarks")
        
        results = {}
        
        # Speed benchmarks
        logger.info("Running sequential generation benchmark...")
        results["sequential"] = await self.speed_benchmark.benchmark_sequential_generation()
        
        logger.info("Running concurrent generation benchmark...")
        results["concurrent_low"] = await self.speed_benchmark.benchmark_concurrent_generation(5)
        results["concurrent_high"] = await self.speed_benchmark.benchmark_concurrent_generation(15)
        
        # Quality benchmarks
        logger.info("Running content consistency benchmark...")
        results["consistency"] = await self.quality_benchmark.benchmark_content_consistency()
        
        logger.info("Running A/B test performance benchmark...")
        results["ab_test"] = await self.quality_benchmark.benchmark_ab_test_performance()
        
        logger.info("✅ Copywriting benchmarks completed")
        return results
    
    def generate_copywriting_report(self, results: Dict[str, CopywritingBenchmarkResult]) -> str:
        """Generate comprehensive copywriting benchmark report."""
        report = ["# Copywriting Model Performance Report\n"]
        report.append(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Summary metrics
        avg_generation_time = statistics.mean([r.avg_generation_time_ms for r in results.values()])
        avg_success_rate = statistics.mean([r.success_rate for r in results.values()])
        max_throughput = max([r.throughput_content_per_second for r in results.values()])
        
        report.append("## Executive Summary\n")
        report.append(f"- **Average Generation Time**: {avg_generation_time:.2f}ms\n")
        report.append(f"- **Average Success Rate**: {avg_success_rate:.1%}\n")
        report.append(f"- **Peak Throughput**: {max_throughput:.1f} content/sec\n\n")
        
        # Detailed results
        for test_name, result in results.items():
            report.append(f"## {result.test_name}\n")
            report.append(f"- **Generation Time**: {result.avg_generation_time_ms:.2f}ms (median: {result.median_generation_time_ms:.2f}ms)\n")
            report.append(f"- **P95 Response Time**: {result.p95_generation_time_ms:.2f}ms\n")
            report.append(f"- **Success Rate**: {result.success_rate:.1%}\n")
            report.append(f"- **Throughput**: {result.throughput_content_per_second:.2f} content/sec\n")
            report.append(f"- **Average Content Length**: {result.avg_content_length} characters\n")
            
            if result.avg_readability_score > 0:
                report.append(f"- **Readability Score**: {result.avg_readability_score:.1f}\n")
            
            if result.avg_engagement_prediction > 0:
                report.append(f"- **Engagement Prediction**: {result.avg_engagement_prediction:.1%}\n")
            
            if result.model_distribution:
                report.append(f"- **Model Usage**: {result.model_distribution}\n")
            
            if result.details:
                report.append(f"- **Additional Details**: {result.details}\n")
            
            report.append("\n")
        
        # Performance grade
        if avg_generation_time < 100:
            grade = "A+ (Excellent)"
        elif avg_generation_time < 300:
            grade = "A (Very Good)"
        elif avg_generation_time < 500:
            grade = "B (Good)"
        elif avg_generation_time < 1000:
            grade = "C (Acceptable)"
        else:
            grade = "D (Needs Improvement)"
        
        report.append(f"## Overall Performance Grade: **{grade}**\n\n")
        
        # Recommendations
        report.append("## Recommendations\n")
        
        if avg_generation_time > 500:
            report.append("- Consider optimizing AI model or using caching for better response times\n")
        
        if avg_success_rate < 0.95:
            report.append("- Investigate and fix error causes to improve reliability\n")
        
        if max_throughput < 5:
            report.append("- Consider implementing better concurrency or caching strategies\n")
        
        if avg_generation_time < 200 and avg_success_rate > 0.98:
            report.append("- 🎉 Excellent performance! System is production-ready\n")
        
        return "".join(report)


# Factory function
def create_copywriting_benchmark() -> ComprehensiveCopywritingBenchmark:
    """Create comprehensive copywriting benchmark suite."""
    return ComprehensiveCopywritingBenchmark()


# CLI function
async def main():
    """Main function for running copywriting benchmarks."""
    benchmark = create_copywriting_benchmark()
    results = await benchmark.run_all_benchmarks()
    report = benchmark.generate_copywriting_report(results)
    
    print(report)
    
    # Save report
    with open("copywriting_benchmark_report.md", "w") as f:
        f.write(report)
    
    print("\n📊 Copywriting benchmark report saved to: copywriting_benchmark_report.md")


if __name__ == "__main__":
    asyncio.run(main())


# Export components
__all__ = [
    "CopywritingBenchmarkResult",
    "CopywritingSpeedBenchmark",
    "CopywritingQualityBenchmark", 
    "ComprehensiveCopywritingBenchmark",
    "create_copywriting_benchmark"
] 