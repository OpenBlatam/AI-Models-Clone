#!/usr/bin/env python3
"""
Pydantic Performance Analyzer
Analyze and optimize Pydantic model performance across the codebase.
"""

import time
import sys
import json
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional, Type, Tuple
import argparse
import logging
import importlib.util
import inspect
from dataclasses import dataclass, asdict
from collections import defaultdict
import psutil
import gc

from pydantic import BaseModel, ValidationError
import orjson

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for a Pydantic model."""
    model_name: str
    field_count: int
    validation_time_ms: float
    serialization_time_ms: float
    deserialization_time_ms: float
    memory_usage_kb: float
    error_rate: float
    sample_size: int
    config_type: str
    has_custom_validators: bool
    uses_orjson: bool
    uses_config_dict: bool

@dataclass
class OptimizationRecommendation:
    """Recommendation for model optimization."""
    model_name: str
    issue_type: str
    description: str
    impact: str  # "high", "medium", "low"
    suggested_fix: str
    expected_improvement: str

class PydanticPerformanceAnalyzer:
    """Analyzer for Pydantic model performance."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.recommendations: List[OptimizationRecommendation] = []
        self.test_data_cache: Dict[str, Dict] = {}
    
    def analyze_model(self, model_class: Type[BaseModel], iterations: int = 100) -> PerformanceMetrics:
        """Analyze performance of a single model."""
        model_name = model_class.__name__
        
        # Generate test data
        test_data = self._generate_test_data(model_class)
        
        # Measure validation time
        validation_times = []
        errors = 0
        
        for _ in range(iterations):
            try:
                start_time = time.perf_counter()
                instance = model_class(**test_data)
                end_time = time.perf_counter()
                validation_times.append((end_time - start_time) * 1000)
            except Exception:
                errors += 1
        
        # Measure serialization time
        instance = model_class(**test_data)
        serialization_times = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            instance.model_dump()
            end_time = time.perf_counter()
            serialization_times.append((end_time - start_time) * 1000)
        
        # Measure deserialization time
        json_data = instance.model_dump_json()
        deserialization_times = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            model_class.model_validate_json(json_data)
            end_time = time.perf_counter()
            deserialization_times.append((end_time - start_time) * 1000)
        
        # Measure memory usage
        memory_before = psutil.Process().memory_info().rss
        instances = [model_class(**test_data) for _ in range(100)]
        memory_after = psutil.Process().memory_info().rss
        memory_per_instance = (memory_after - memory_before) / 100 / 1024  # KB
        
        # Analyze model configuration
        config_analysis = self._analyze_model_config(model_class)
        
        metrics = PerformanceMetrics(
            model_name=model_name,
            field_count=len(model_class.model_fields),
            validation_time_ms=statistics.mean(validation_times),
            serialization_time_ms=statistics.mean(serialization_times),
            deserialization_time_ms=statistics.mean(deserialization_times),
            memory_usage_kb=memory_per_instance,
            error_rate=errors / iterations,
            sample_size=iterations,
            config_type=config_analysis['config_type'],
            has_custom_validators=config_analysis['has_custom_validators'],
            uses_orjson=config_analysis['uses_orjson'],
            uses_config_dict=config_analysis['uses_config_dict']
        )
        
        self.metrics.append(metrics)
        return metrics
    
    def _generate_test_data(self, model_class: Type[BaseModel]) -> Dict[str, Any]:
        """Generate test data for a model."""
        cache_key = model_class.__name__
        if cache_key in self.test_data_cache:
            return self.test_data_cache[cache_key]
        
        test_data = {}
        
        for field_name, field_info in model_class.model_fields.items():
            field_type = field_info.annotation
            
            # Generate appropriate test data based on field type
            if field_type == str:
                test_data[field_name] = f"test_{field_name}_value"
            elif field_type == int:
                test_data[field_name] = 42
            elif field_type == float:
                test_data[field_name] = 3.14
            elif field_type == bool:
                test_data[field_name] = True
            elif field_type == list:
                test_data[field_name] = ["item1", "item2"]
            elif field_type == dict:
                test_data[field_name] = {"key": "value"}
            elif hasattr(field_type, '__origin__') and field_type.__origin__ == list:
                # Handle List[T]
                inner_type = field_type.__args__[0]
                if inner_type == str:
                    test_data[field_name] = ["string1", "string2"]
                elif inner_type == int:
                    test_data[field_name] = [1, 2, 3]
                else:
                    test_data[field_name] = []
            elif hasattr(field_type, '__origin__') and field_type.__origin__ == dict:
                # Handle Dict[K, V]
                test_data[field_name] = {"key1": "value1", "key2": "value2"}
            else:
                # Default to None for complex types
                test_data[field_name] = None
        
        self.test_data_cache[cache_key] = test_data
        return test_data
    
    def _analyze_model_config(self, model_class: Type[BaseModel]) -> Dict[str, Any]:
        """Analyze model configuration for optimization opportunities."""
        config = getattr(model_class, 'model_config', None)
        
        analysis = {
            'config_type': 'none',
            'has_custom_validators': False,
            'uses_orjson': False,
            'uses_config_dict': False
        }
        
        if config:
            if hasattr(config, 'json_loads'):
                analysis['uses_orjson'] = 'orjson' in str(config.json_loads)
            analysis['uses_config_dict'] = True
            analysis['config_type'] = 'ConfigDict'
        else:
            # Check for old Config class
            for attr_name in dir(model_class):
                if attr_name == 'Config':
                    analysis['config_type'] = 'Config'
                    break
        
        # Check for custom validators
        for method_name in dir(model_class):
            method = getattr(model_class, method_name)
            if hasattr(method, '__validator__') or hasattr(method, '__field_validator__'):
                analysis['has_custom_validators'] = True
                break
        
        return analysis
    
    def generate_recommendations(self) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on analysis."""
        recommendations = []
        
        for metric in self.metrics:
            # Check for slow validation
            if metric.validation_time_ms > 1.0:
                recommendations.append(OptimizationRecommendation(
                    model_name=metric.model_name,
                    issue_type="slow_validation",
                    description=f"Validation takes {metric.validation_time_ms:.2f}ms (target: <1ms)",
                    impact="high" if metric.validation_time_ms > 5.0 else "medium",
                    suggested_fix="Consider using field caching or optimizing validators",
                    expected_improvement="50-80% reduction in validation time"
                ))
            
            # Check for slow serialization
            if metric.serialization_time_ms > 2.0:
                recommendations.append(OptimizationRecommendation(
                    model_name=metric.model_name,
                    issue_type="slow_serialization",
                    description=f"Serialization takes {metric.serialization_time_ms:.2f}ms (target: <2ms)",
                    impact="medium",
                    suggested_fix="Use ORJSON for faster serialization",
                    expected_improvement="30-50% reduction in serialization time"
                ))
            
            # Check for high memory usage
            if metric.memory_usage_kb > 1.0:
                recommendations.append(OptimizationRecommendation(
                    model_name=metric.model_name,
                    issue_type="high_memory",
                    description=f"Memory usage is {metric.memory_usage_kb:.2f}KB per instance (target: <1KB)",
                    impact="medium",
                    suggested_fix="Consider using frozen models or optimizing field types",
                    expected_improvement="20-40% reduction in memory usage"
                ))
            
            # Check for missing ORJSON
            if not metric.uses_orjson:
                recommendations.append(OptimizationRecommendation(
                    model_name=metric.model_name,
                    issue_type="missing_orjson",
                    description="Not using ORJSON for serialization",
                    impact="medium",
                    suggested_fix="Add ORJSON configuration to model_config",
                    expected_improvement="30-50% faster JSON operations"
                ))
            
            # Check for old Config class
            if metric.config_type == 'Config':
                recommendations.append(OptimizationRecommendation(
                    model_name=metric.model_name,
                    issue_type="old_config",
                    description="Using deprecated Config class instead of ConfigDict",
                    impact="low",
                    suggested_fix="Migrate to ConfigDict for better performance",
                    expected_improvement="10-20% improvement in model creation"
                ))
            
            # Check for high error rate
            if metric.error_rate > 0.01:
                recommendations.append(OptimizationRecommendation(
                    model_name=metric.model_name,
                    issue_type="high_error_rate",
                    description=f"Error rate is {metric.error_rate:.2%} (target: <1%)",
                    impact="high",
                    suggested_fix="Review validation logic and error handling",
                    expected_improvement="Reduced validation failures"
                ))
        
        self.recommendations = recommendations
        return recommendations
    
    def analyze_file(self, file_path: Path) -> List[PerformanceMetrics]:
        """Analyze all Pydantic models in a file."""
        try:
            # Load module
            spec = importlib.util.spec_from_file_location("temp_module", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            metrics = []
            
            # Find all BaseModel subclasses
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseModel) and 
                    obj != BaseModel):
                    
                    try:
                        metric = self.analyze_model(obj)
                        metrics.append(metric)
                        logger.info(f"Analyzed model: {name}")
                    except Exception as e:
                        logger.warning(f"Failed to analyze model {name}: {e}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return []
    
    def analyze_directory(self, directory: Path) -> List[PerformanceMetrics]:
        """Analyze all Python files in a directory."""
        all_metrics = []
        
        for file_path in directory.rglob("*.py"):
            if ("migrations" not in str(file_path) and 
                "venv" not in str(file_path) and
                "test" not in str(file_path).lower()):
                
                metrics = self.analyze_file(file_path)
                all_metrics.extend(metrics)
        
        return all_metrics
    
    def generate_report(self, output_file: Optional[Path] = None) -> str:
        """Generate comprehensive performance report."""
        if not self.metrics:
            return "No models analyzed."
        
        # Calculate summary statistics
        total_models = len(self.metrics)
        avg_validation_time = statistics.mean(m.validation_time_ms for m in self.metrics)
        avg_serialization_time = statistics.mean(m.serialization_time_ms for m in self.metrics)
        avg_memory_usage = statistics.mean(m.memory_usage_kb for m in self.metrics)
        
        # Generate recommendations
        recommendations = self.generate_recommendations()
        
        report_lines = [
            "# Pydantic Performance Analysis Report",
            "",
            "## Summary",
            f"- Total models analyzed: {total_models}",
            f"- Average validation time: {avg_validation_time:.2f}ms",
            f"- Average serialization time: {avg_serialization_time:.2f}ms",
            f"- Average memory usage: {avg_memory_usage:.2f}KB",
            f"- Optimization recommendations: {len(recommendations)}",
            "",
            "## Detailed Metrics",
            ""
        ]
        
        # Sort metrics by validation time (slowest first)
        sorted_metrics = sorted(self.metrics, key=lambda m: m.validation_time_ms, reverse=True)
        
        for metric in sorted_metrics:
            report_lines.extend([
                f"### {metric.model_name}",
                f"- Fields: {metric.field_count}",
                f"- Validation time: {metric.validation_time_ms:.2f}ms",
                f"- Serialization time: {metric.serialization_time_ms:.2f}ms",
                f"- Deserialization time: {metric.deserialization_time_ms:.2f}ms",
                f"- Memory usage: {metric.memory_usage_kb:.2f}KB",
                f"- Error rate: {metric.error_rate:.2%}",
                f"- Config type: {metric.config_type}",
                f"- Uses ORJSON: {metric.uses_orjson}",
                f"- Has custom validators: {metric.has_custom_validators}",
                ""
            ])
        
        # Add recommendations
        if recommendations:
            report_lines.extend([
                "## Optimization Recommendations",
                ""
            ])
            
            # Group by impact
            for impact in ["high", "medium", "low"]:
                impact_recs = [r for r in recommendations if r.impact == impact]
                if impact_recs:
                    report_lines.extend([
                        f"### {impact.title()} Impact",
                        ""
                    ])
                    
                    for rec in impact_recs:
                        report_lines.extend([
                            f"**{rec.model_name}** - {rec.issue_type}",
                            f"- {rec.description}",
                            f"- Suggested fix: {rec.suggested_fix}",
                            f"- Expected improvement: {rec.expected_improvement}",
                            ""
                        ])
        
        report_content = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Performance report written to: {output_file}")
        
        return report_content
    
    def export_metrics_json(self, output_file: Path) -> None:
        """Export metrics to JSON format."""
        data = {
            'metrics': [asdict(m) for m in self.metrics],
            'recommendations': [asdict(r) for r in self.recommendations],
            'summary': {
                'total_models': len(self.metrics),
                'avg_validation_time_ms': statistics.mean(m.validation_time_ms for m in self.metrics) if self.metrics else 0,
                'avg_serialization_time_ms': statistics.mean(m.serialization_time_ms for m in self.metrics) if self.metrics else 0,
                'avg_memory_usage_kb': statistics.mean(m.memory_usage_kb for m in self.metrics) if self.metrics else 0,
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Metrics exported to: {output_file}")

def compare_models(model1: Type[BaseModel], model2: Type[BaseModel], iterations: int = 100) -> Dict[str, Any]:
    """Compare performance between two models."""
    analyzer = PydanticPerformanceAnalyzer()
    
    metrics1 = analyzer.analyze_model(model1, iterations)
    metrics2 = analyzer.analyze_model(model2, iterations)
    
    comparison = {
        'model1': {
            'name': metrics1.model_name,
            'validation_time_ms': metrics1.validation_time_ms,
            'serialization_time_ms': metrics1.serialization_time_ms,
            'memory_usage_kb': metrics1.memory_usage_kb
        },
        'model2': {
            'name': metrics2.model_name,
            'validation_time_ms': metrics2.validation_time_ms,
            'serialization_time_ms': metrics2.serialization_time_ms,
            'memory_usage_kb': metrics2.memory_usage_kb
        },
        'improvements': {
            'validation_time': ((metrics1.validation_time_ms - metrics2.validation_time_ms) / metrics1.validation_time_ms) * 100,
            'serialization_time': ((metrics1.serialization_time_ms - metrics2.serialization_time_ms) / metrics1.serialization_time_ms) * 100,
            'memory_usage': ((metrics1.memory_usage_kb - metrics2.memory_usage_kb) / metrics1.memory_usage_kb) * 100
        }
    }
    
    return comparison

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Analyze Pydantic model performance")
    parser.add_argument("path", help="Path to file or directory to analyze")
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument("--json", help="Export metrics to JSON file")
    parser.add_argument("--iterations", type=int, default=100, help="Number of iterations for testing")
    parser.add_argument("--compare", help="Compare with another model file")
    
    args = parser.parse_args()
    
    path = Path(args.path)
    if not path.exists():
        logger.error(f"Path does not exist: {path}")
        sys.exit(1)
    
    analyzer = PydanticPerformanceAnalyzer()
    
    if path.is_file():
        metrics = analyzer.analyze_file(path)
    else:
        metrics = analyzer.analyze_directory(path)
    
    if not metrics:
        logger.warning("No Pydantic models found to analyze")
        return
    
    # Generate report
    report = analyzer.generate_report(args.output)
    if not args.output:
        print(report)
    
    # Export JSON if requested
    if args.json:
        analyzer.export_metrics_json(Path(args.json))
    
    # Compare models if requested
    if args.compare:
        compare_path = Path(args.compare)
        if compare_path.exists():
            # This would need to be implemented based on specific comparison needs
            logger.info(f"Comparison with {args.compare} would be implemented here")

if __name__ == "__main__":
    main() 