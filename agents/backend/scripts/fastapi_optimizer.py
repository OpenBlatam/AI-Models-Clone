from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import argparse
import logging
from dataclasses import dataclass, field
from datetime import datetime
import json
        from collections import Counter
from typing import Any, List, Dict, Optional
import asyncio
#!/usr/bin/env python3
"""
FastAPI Optimizer
================

Comprehensive FastAPI application analysis and optimization tool.
Features:
- Application structure analysis
- Performance optimization recommendations
- Security audit
- Best practices compliance check
- Dependency injection analysis
- Error handling assessment
"""


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class FastAPIAnalysis:
    """Analysis results for a FastAPI application"""
    file_path: Path
    app_name: str
    fastapi_imports: List[str] = field(default_factory=list)
    endpoints: List[Dict[str, Any]] = field(default_factory=list)
    middleware: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    models: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    score: float = 0.0


@dataclass
class OptimizationReport:
    """Complete optimization report"""
    total_apps: int
    analyzed_apps: int
    average_score: float
    applications: List[FastAPIAnalysis]
    common_issues: List[str]
    global_recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class FastAPIOptimizer:
    """FastAPI application optimizer and analyzer"""
    
    def __init__(self, project_root: str):
        
    """__init__ function."""
self.project_root = Path(project_root)
        self.analysis_results: List[FastAPIAnalysis] = []
        
        # Best practices patterns
        self.best_practices = {
            'async_endpoints': r'async def.*\(.*\):',
            'dependency_injection': r'Depends\(',
            'pydantic_models': r'class.*\(BaseModel\):',
            'error_handling': r'@.*\.exception_handler',
            'rate_limiting': r'@limiter\.limit',
            'middleware': r'add_middleware\(',
            'health_checks': r'/health',
            'metrics': r'/metrics',
            'cors': r'CORSMiddleware',
            'security_headers': r'X-Content-Type-Options',
        }
        
        # Anti-patterns to detect
        self.anti_patterns = {
            'sync_endpoints': r'def.*\(.*\):.*return.*Response',
            'blocking_operations': r'time\.sleep\(|requests\.get\(',
            'hardcoded_values': r'localhost|127\.0\.0\.1',
            'missing_validation': r'request\.body\(\)',
            'insecure_headers': r'Access-Control-Allow-Origin.*\*',
        }
    
    async def find_fastapi_apps(self) -> List[Path]:
        """Find all FastAPI applications in the project"""
        fastapi_files = []
        
        for pattern in ['**/*.py']:
            python_files = self.project_root.glob(pattern)
            
            for file_path in python_files:
                if self._is_fastapi_app(file_path):
                    fastapi_files.append(file_path)
        
        return fastapi_files
    
    async def _is_fastapi_app(self, file_path: Path) -> bool:
        """Check if file contains FastAPI application"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
                content = f.read()
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            
            # Check for FastAPI imports and app creation
            fastapi_indicators = [
                'from fastapi import',
                'import fastapi',
                'FastAPI(',
                'app = FastAPI',
                '@app.',
                '@api_router.',
            ]
            
            return any(indicator in content for indicator in fastapi_indicators)
            
        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")
            return False
    
    def analyze_app(self, file_path: Path) -> FastAPIAnalysis:
        """Analyze a single FastAPI application"""
        analysis = FastAPIAnalysis(file_path=file_path, app_name=file_path.stem)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
                content = f.read()
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            
            # Parse AST
            tree = ast.parse(content)
            
            # Analyze imports
            analysis.fastapi_imports = self._analyze_imports(tree)
            
            # Analyze endpoints
            analysis.endpoints = self._analyze_endpoints(tree, content)
            
            # Analyze middleware
            analysis.middleware = self._analyze_middleware(content)
            
            # Analyze dependencies
            analysis.dependencies = self._analyze_dependencies(content)
            
            # Analyze models
            analysis.models = self._analyze_models(content)
            
            # Check for issues
            analysis.issues = self._check_issues(content)
            
            # Generate recommendations
            analysis.recommendations = self._generate_recommendations(analysis)
            
            # Calculate score
            analysis.score = self._calculate_score(analysis)
            
        except Exception as e:
            error_msg = f"Error analyzing {file_path}: {e}"
            logger.error(error_msg)
            analysis.issues.append(error_msg)
        
        return analysis
    
    def _analyze_imports(self, tree: ast.AST) -> List[str]:
        """Analyze FastAPI imports"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if 'fastapi' in alias.name:
                        imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if 'fastapi' in node.module:
                    for alias in node.names:
                        imports.append(f"{node.module}.{alias.name}")
        
        return imports
    
    def _analyze_endpoints(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Analyze API endpoints"""
        endpoints = []
        
        # Find endpoint decorators
        endpoint_patterns = [
            r'@app\.(get|post|put|delete|patch)\(([^)]+)\)',
            r'@api_router\.(get|post|put|delete|patch)\(([^)]+)\)',
            r'@router\.(get|post|put|delete|patch)\(([^)]+)\)',
        ]
        
        for pattern in endpoint_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                method = match.group(1)
                path = match.group(2).strip('"\'')
                
                # Check if endpoint is async
                is_async = self._is_endpoint_async(content, match.start())
                
                endpoints.append({
                    'method': method.upper(),
                    'path': path,
                    'is_async': is_async,
                    'has_dependencies': 'Depends(' in content[match.start():match.start()+500],
                    'has_validation': 'BaseModel' in content[match.start():match.start()+500],
                })
        
        return endpoints
    
    def _is_endpoint_async(self, content: str, decorator_pos: int) -> bool:
        """Check if endpoint function is async"""
        # Find the function definition after the decorator
        func_pattern = r'async def|def '
        matches = list(re.finditer(func_pattern, content[decorator_pos:]))
        
        if matches:
            return 'async def' in matches[0].group()
        
        return False
    
    def _analyze_middleware(self, content: str) -> List[str]:
        """Analyze middleware usage"""
        middleware = []
        
        middleware_patterns = [
            r'add_middleware\(([^)]+)\)',
            r'@app\.middleware\("([^"]+)"\)',
        ]
        
        for pattern in middleware_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                middleware.append(match.group(1))
        
        return middleware
    
    def _analyze_dependencies(self, content: str) -> List[str]:
        """Analyze dependency injection usage"""
        dependencies = []
        
        # Find dependency functions
        dep_patterns = [
            r'def get_([^:]+)\([^)]*\):',
            r'async def get_([^:]+)\([^)]*\):',
        ]
        
        for pattern in dep_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                dependencies.append(match.group(1))
        
        return dependencies
    
    def _analyze_models(self, content: str) -> List[str]:
        """Analyze Pydantic models"""
        models = []
        
        # Find model classes
        model_pattern = r'class ([^(]+)\(BaseModel\):'
        matches = re.finditer(model_pattern, content)
        
        for match in matches:
            models.append(match.group(1))
        
        return models
    
    def _check_issues(self, content: str) -> List[str]:
        """Check for common issues and anti-patterns"""
        issues = []
        
        # Check for anti-patterns
        for pattern_name, pattern in self.anti_patterns.items():
            if re.search(pattern, content):
                issues.append(f"Anti-pattern detected: {pattern_name}")
        
        # Check for missing best practices
        if 'async def' not in content and 'def ' in content:
            issues.append("Sync endpoints detected - consider using async")
        
        if 'Depends(' not in content and '@app.' in content:
            issues.append("No dependency injection detected")
        
        if 'BaseModel' not in content and '@app.' in content:
            issues.append("No Pydantic models detected")
        
        if 'exception_handler' not in content and '@app.' in content:
            issues.append("No custom exception handlers detected")
        
        if 'health' not in content and '@app.' in content:
            issues.append("No health check endpoints detected")
        
        if 'metrics' not in content and '@app.' in content:
            issues.append("No metrics endpoints detected")
        
        return issues
    
    def _generate_recommendations(self, analysis: FastAPIAnalysis) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Based on issues found
        if not analysis.endpoints:
            recommendations.append("No endpoints found - ensure proper route definitions")
        
        sync_endpoints = [ep for ep in analysis.endpoints if not ep['is_async']]
        if sync_endpoints:
            recommendations.append(f"Convert {len(sync_endpoints)} sync endpoints to async")
        
        if not analysis.dependencies:
            recommendations.append("Implement dependency injection for better testability")
        
        if not analysis.models:
            recommendations.append("Use Pydantic models for request/response validation")
        
        if not analysis.middleware:
            recommendations.append("Add middleware for CORS, security headers, and logging")
        
        if not any('health' in ep['path'] for ep in analysis.endpoints):
            recommendations.append("Add health check endpoints")
        
        if not any('metrics' in ep['path'] for ep in analysis.endpoints):
            recommendations.append("Add metrics endpoints for monitoring")
        
        # Performance recommendations
        if len(analysis.endpoints) > 20:
            recommendations.append("Consider splitting into multiple routers for better organization")
        
        # Security recommendations
        if not any('cors' in mw.lower() for mw in analysis.middleware):
            recommendations.append("Add CORS middleware for cross-origin requests")
        
        if not any('security' in mw.lower() for mw in analysis.middleware):
            recommendations.append("Add security headers middleware")
        
        return recommendations
    
    def _calculate_score(self, analysis: FastAPIAnalysis) -> float:
        """Calculate application quality score (0-100)"""
        score = 100.0
        
        # Deduct points for issues
        score -= len(analysis.issues) * 5
        
        # Deduct points for missing best practices
        if not analysis.endpoints:
            score -= 20
        
        sync_endpoints = [ep for ep in analysis.endpoints if not ep['is_async']]
        score -= len(sync_endpoints) * 3
        
        if not analysis.dependencies:
            score -= 10
        
        if not analysis.models:
            score -= 10
        
        if not analysis.middleware:
            score -= 10
        
        if not any('health' in ep['path'] for ep in analysis.endpoints):
            score -= 5
        
        if not any('metrics' in ep['path'] for ep in analysis.endpoints):
            score -= 5
        
        # Add bonus points for good practices
        if len(analysis.dependencies) > 5:
            score += 5
        
        if len(analysis.models) > 5:
            score += 5
        
        if len(analysis.middleware) > 3:
            score += 5
        
        return max(0.0, min(100.0, score))
    
    def analyze_project(self) -> OptimizationReport:
        """Analyze entire project"""
        logger.info(f"Analyzing FastAPI applications in {self.project_root}")
        
        fastapi_apps = self.find_fastapi_apps()
        logger.info(f"Found {len(fastapi_apps)} FastAPI applications")
        
        for app_path in fastapi_apps:
            logger.info(f"Analyzing {app_path}")
            analysis = self.analyze_app(app_path)
            self.analysis_results.append(analysis)
        
        # Generate report
        return self._generate_report()
    
    def _generate_report(self) -> OptimizationReport:
        """Generate comprehensive optimization report"""
        if not self.analysis_results:
            return OptimizationReport(
                total_apps=0,
                analyzed_apps=0,
                average_score=0.0,
                applications=[],
                common_issues=[],
                global_recommendations=[]
            )
        
        # Calculate statistics
        total_apps = len(self.analysis_results)
        average_score = sum(app.score for app in self.analysis_results) / total_apps
        
        # Find common issues
        all_issues = []
        for app in self.analysis_results:
            all_issues.extend(app.issues)
        
        common_issues = self._get_common_items(all_issues)
        
        # Generate global recommendations
        global_recommendations = self._generate_global_recommendations()
        
        return OptimizationReport(
            total_apps=total_apps,
            analyzed_apps=total_apps,
            average_score=average_score,
            applications=self.analysis_results,
            common_issues=common_issues,
            global_recommendations=global_recommendations
        )
    
    def _get_common_items(self, items: List[str], min_count: int = 2) -> List[str]:
        """Get items that appear multiple times"""
        counter = Counter(items)
        return [item for item, count in counter.most_common() if count >= min_count]
    
    def _generate_global_recommendations(self) -> List[str]:
        """Generate project-wide recommendations"""
        recommendations = []
        
        # Analyze patterns across all applications
        total_endpoints = sum(len(app.endpoints) for app in self.analysis_results)
        total_models = sum(len(app.models) for app in self.analysis_results)
        total_dependencies = sum(len(app.dependencies) for app in self.analysis_results)
        
        if total_endpoints > 100:
            recommendations.append("Large number of endpoints detected - consider API versioning")
        
        if total_models < total_endpoints / 2:
            recommendations.append("Low model coverage - implement request/response models")
        
        if total_dependencies < total_endpoints / 3:
            recommendations.append("Low dependency injection usage - implement more dependencies")
        
        # Check for consistency issues
        app_scores = [app.score for app in self.analysis_results]
        if max(app_scores) - min(app_scores) > 30:
            recommendations.append("High score variance - standardize practices across applications")
        
        return recommendations
    
    def save_report(self, report: OptimizationReport, output_path: str):
        """Save optimization report to file"""
        report_data = {
            "timestamp": report.timestamp.isoformat(),
            "summary": {
                "total_apps": report.total_apps,
                "analyzed_apps": report.analyzed_apps,
                "average_score": report.average_score,
            },
            "applications": [
                {
                    "file_path": str(app.file_path),
                    "app_name": app.app_name,
                    "score": app.score,
                    "endpoints_count": len(app.endpoints),
                    "models_count": len(app.models),
                    "dependencies_count": len(app.dependencies),
                    "middleware_count": len(app.middleware),
                    "issues": app.issues,
                    "recommendations": app.recommendations,
                }
                for app in report.applications
            ],
            "common_issues": report.common_issues,
            "global_recommendations": report.global_recommendations
        }
        
        with open(output_path, 'w') as f:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Optimization report saved to {output_path}")
    
    def print_report(self, report: OptimizationReport):
        """Print optimization report to console"""
        print("=" * 80)
        print("FastAPI Optimization Report")
        print("=" * 80)
        print(f"Generated: {report.timestamp}")
        print()
        
        print("📊 SUMMARY")
        print("-" * 40)
        print(f"Total Applications: {report.total_apps}")
        print(f"Analyzed Applications: {report.analyzed_apps}")
        print(f"Average Score: {report.average_score:.1f}/100")
        print()
        
        print("🏆 TOP APPLICATIONS")
        print("-" * 40)
        sorted_apps = sorted(report.applications, key=lambda x: x.score, reverse=True)
        for i, app in enumerate(sorted_apps[:5], 1):
            print(f"{i}. {app.app_name} ({app.file_path.name}) - Score: {app.score:.1f}")
        print()
        
        if report.common_issues:
            print("⚠️ COMMON ISSUES")
            print("-" * 40)
            for issue in report.common_issues[:5]:
                print(f"• {issue}")
            print()
        
        if report.global_recommendations:
            print("💡 GLOBAL RECOMMENDATIONS")
            print("-" * 40)
            for rec in report.global_recommendations:
                print(f"• {rec}")
            print()
        
        print("📋 DETAILED ANALYSIS")
        print("-" * 40)
        for app in sorted_apps:
            print(f"\n{app.app_name} (Score: {app.score:.1f})")
            print(f"  File: {app.file_path}")
            print(f"  Endpoints: {len(app.endpoints)}")
            print(f"  Models: {len(app.models)}")
            print(f"  Dependencies: {len(app.dependencies)}")
            print(f"  Middleware: {len(app.middleware)}")
            
            if app.issues:
                print(f"  Issues: {len(app.issues)}")
                for issue in app.issues[:3]:
                    print(f"    • {issue}")
            
            if app.recommendations:
                print(f"  Recommendations: {len(app.recommendations)}")
                for rec in app.recommendations[:3]:
                    print(f"    • {rec}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='FastAPI Application Optimizer')
    parser.add_argument('project_root', help='Path to project root directory')
    parser.add_argument('--output', default='fastapi_optimization_report.json', help='Output file for report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate project root
    project_root = Path(args.project_root)
    if not project_root.exists():
        logger.error(f"Project root does not exist: {project_root}")
        sys.exit(1)
    
    # Create optimizer and run analysis
    optimizer = FastAPIOptimizer(project_root=str(project_root))
    
    try:
        report = optimizer.analyze_project()
        
        # Print report
        optimizer.print_report(report)
        
        # Save report
        optimizer.save_report(report, args.output)
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        sys.exit(1)


match __name__:
    case '__main__':
    main() 