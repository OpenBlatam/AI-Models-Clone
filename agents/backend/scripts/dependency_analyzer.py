#!/usr/bin/env python3
"""
Dependency Analyzer for Blatam Academy Backend
Analyzes dependencies, checks for vulnerabilities, and provides recommendations.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import pkg_resources
import re

@dataclass
class DependencyInfo:
    """Information about a dependency."""
    name: str
    version: str
    version_spec: str
    file: str
    category: str
    description: str = ""
    size_mb: Optional[float] = None
    vulnerabilities: List[str] = None
    last_updated: Optional[str] = None
    maintainers: List[str] = None

@dataclass
class AnalysisResult:
    """Result of dependency analysis."""
    total_dependencies: int
    production_dependencies: int
    development_dependencies: int
    security_issues: int
    outdated_packages: int
    heavy_packages: List[str]
    recommendations: List[str]
    dependencies: List[DependencyInfo]

class DependencyAnalyzer:
    """Analyzes project dependencies and provides recommendations."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.requirements_dir = project_root / "requirements"
        self.results = []
        
        # Categories for dependency classification
        self.categories = {
            "web_framework": ["fastapi", "uvicorn", "starlette", "django", "flask"],
            "database": ["sqlalchemy", "alembic", "asyncpg", "psycopg2", "redis"],
            "ai_ml": ["torch", "transformers", "openai", "langchain", "sentence-transformers"],
            "cloud": ["boto3", "aioboto3", "google-cloud", "azure"],
            "monitoring": ["sentry", "prometheus", "structlog", "ddtrace"],
            "security": ["cryptography", "passlib", "jwt", "argon2"],
            "testing": ["pytest", "unittest", "coverage"],
            "development": ["black", "ruff", "mypy", "pre-commit"],
            "http": ["httpx", "aiohttp", "requests", "urllib3"],
            "data_processing": ["pandas", "numpy", "dask", "vaex"],
            "image_processing": ["pillow", "opencv", "rembg", "pyvips"],
            "caching": ["redis", "aioredis", "cachetools", "aiocache"],
        }
    
    def analyze_requirements_file(self, file_path: Path) -> List[DependencyInfo]:
        """Analyze a single requirements file."""
        dependencies = []
        
        if not file_path.exists():
            print(f"Warning: {file_path} does not exist")
            return dependencies
        
        with open(file_path) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                
                # Skip -r directives (we'll handle them separately)
                if line.startswith("-r "):
                    continue
                
                try:
                    # Parse the requirement
                    req = pkg_resources.Requirement.parse(line)
                    
                    # Determine category
                    category = self._categorize_dependency(req.name)
                    
                    # Get version spec
                    version_spec = str(req.specifier) if req.specifier else "any"
                    
                    # Extract version if available
                    version = ""
                    if req.specifier:
                        for spec in req.specifier:
                            if spec.operator == "==":
                                version = spec.version
                                break
                    
                    dependency = DependencyInfo(
                        name=req.name,
                        version=version,
                        version_spec=version_spec,
                        file=file_path.name,
                        category=category,
                        vulnerabilities=[],
                        maintainers=[]
                    )
                    
                    dependencies.append(dependency)
                    
                except Exception as e:
                    print(f"Error parsing line {line_num} in {file_path}: {line} - {e}")
        
        return dependencies
    
    def _categorize_dependency(self, package_name: str) -> str:
        """Categorize a dependency based on its name."""
        package_lower = package_name.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in package_lower:
                    return category
        
        return "other"
    
    def analyze_all_requirements(self) -> List[DependencyInfo]:
        """Analyze all requirements files."""
        all_dependencies = []
        
        # Analyze each requirements file
        for req_file in self.requirements_dir.glob("*.txt"):
            if req_file.name == "combined.txt":
                continue  # Skip combined file
            
            dependencies = self.analyze_requirements_file(req_file)
            all_dependencies.extend(dependencies)
        
        # Remove duplicates (keep first occurrence)
        seen = set()
        unique_dependencies = []
        
        for dep in all_dependencies:
            if dep.name not in seen:
                seen.add(dep.name)
                unique_dependencies.append(dep)
        
        return unique_dependencies
    
    def check_vulnerabilities(self, dependencies: List[DependencyInfo]) -> None:
        """Check for known vulnerabilities in dependencies."""
        try:
            # Try to use safety if available
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                vulnerabilities = json.loads(result.stdout)
                
                for vuln in vulnerabilities:
                    package_name = vuln.get("package", "")
                    for dep in dependencies:
                        if dep.name.lower() == package_name.lower():
                            dep.vulnerabilities.append({
                                "cve": vuln.get("cve", ""),
                                "description": vuln.get("description", ""),
                                "severity": vuln.get("severity", ""),
                                "fixed_in": vuln.get("fixed_in", "")
                            })
            
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            print("Warning: Could not check vulnerabilities. Install 'safety' package.")
    
    def identify_heavy_packages(self, dependencies: List[DependencyInfo]) -> List[str]:
        """Identify packages that are known to be heavy/large."""
        heavy_packages = [
            "torch", "transformers", "tensorflow", "pandas", "numpy",
            "opencv-python", "pillow", "scikit-learn", "matplotlib",
            "seaborn", "plotly", "bokeh", "jupyter", "ipython"
        ]
        
        return [dep.name for dep in dependencies if dep.name.lower() in heavy_packages]
    
    def generate_recommendations(self, dependencies: List[DependencyInfo]) -> List[str]:
        """Generate recommendations based on dependency analysis."""
        recommendations = []
        
        # Check for duplicate functionality
        http_clients = [dep.name for dep in dependencies if dep.category == "http"]
        if len(http_clients) > 2:
            recommendations.append(
                f"Consider consolidating HTTP clients: {', '.join(http_clients)}. "
                "Recommend standardizing on httpx for async operations."
            )
        
        caching_libs = [dep.name for dep in dependencies if dep.category == "caching"]
        if len(caching_libs) > 2:
            recommendations.append(
                f"Multiple caching libraries detected: {', '.join(caching_libs)}. "
                "Consider consolidating to redis + aioredis."
            )
        
        # Check for outdated packages
        outdated_count = len([dep for dep in dependencies if "dev" in dep.file])
        if outdated_count > 0:
            recommendations.append(
                f"Found {outdated_count} development dependencies in production requirements. "
                "Review and separate dev dependencies."
            )
        
        # Check for security packages
        security_packages = [dep.name for dep in dependencies if dep.category == "security"]
        if not security_packages:
            recommendations.append(
                "No security packages detected. Consider adding cryptography, passlib, or similar."
            )
        
        # Check for monitoring
        monitoring_packages = [dep.name for dep in dependencies if dep.category == "monitoring"]
        if not monitoring_packages:
            recommendations.append(
                "No monitoring packages detected. Consider adding sentry-sdk, prometheus-client, or similar."
            )
        
        return recommendations
    
    def analyze(self) -> AnalysisResult:
        """Perform complete dependency analysis."""
        print("Analyzing dependencies...")
        
        # Analyze all dependencies
        dependencies = self.analyze_all_requirements()
        
        # Check for vulnerabilities
        self.check_vulnerabilities(dependencies)
        
        # Count by type
        production_deps = len([d for d in dependencies if d.file == "default.txt"])
        dev_deps = len([d for d in dependencies if d.file == "dev.txt"])
        
        # Identify heavy packages
        heavy_packages = self.identify_heavy_packages(dependencies)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(dependencies)
        
        # Count security issues
        security_issues = sum(len(dep.vulnerabilities) for dep in dependencies)
        
        # Count outdated packages (simplified check)
        outdated_packages = len([d for d in dependencies if "dev" in d.file])
        
        return AnalysisResult(
            total_dependencies=len(dependencies),
            production_dependencies=production_deps,
            development_dependencies=dev_deps,
            security_issues=security_issues,
            outdated_packages=outdated_packages,
            heavy_packages=heavy_packages,
            recommendations=recommendations,
            dependencies=dependencies
        )
    
    def generate_report(self, result: AnalysisResult, output_file: Optional[Path] = None) -> str:
        """Generate a comprehensive report."""
        report = []
        report.append("# Dependency Analysis Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        # Summary
        report.append("## Summary")
        report.append(f"- Total Dependencies: {result.total_dependencies}")
        report.append(f"- Production Dependencies: {result.production_dependencies}")
        report.append(f"- Development Dependencies: {result.development_dependencies}")
        report.append(f"- Security Issues: {result.security_issues}")
        report.append(f"- Outdated Packages: {result.outdated_packages}")
        report.append("")
        
        # Heavy packages
        if result.heavy_packages:
            report.append("## Heavy Packages")
            report.append("These packages may impact startup time and memory usage:")
            for package in result.heavy_packages:
                report.append(f"- {package}")
            report.append("")
        
        # Security issues
        if result.security_issues > 0:
            report.append("## Security Issues")
            for dep in result.dependencies:
                if dep.vulnerabilities:
                    report.append(f"### {dep.name} ({dep.version})")
                    for vuln in dep.vulnerabilities:
                        report.append(f"- {vuln.get('cve', 'Unknown CVE')}: {vuln.get('description', 'No description')}")
            report.append("")
        
        # Recommendations
        if result.recommendations:
            report.append("## Recommendations")
            for i, rec in enumerate(result.recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        # Dependencies by category
        report.append("## Dependencies by Category")
        categories = {}
        for dep in result.dependencies:
            if dep.category not in categories:
                categories[dep.category] = []
            categories[dep.category].append(dep)
        
        for category, deps in sorted(categories.items()):
            report.append(f"### {category.replace('_', ' ').title()} ({len(deps)})")
            for dep in sorted(deps, key=lambda x: x.name):
                report.append(f"- {dep.name} ({dep.version}) - {dep.file}")
            report.append("")
        
        # Detailed dependency list
        report.append("## Detailed Dependency List")
        for dep in sorted(result.dependencies, key=lambda x: x.name):
            report.append(f"### {dep.name}")
            report.append(f"- Version: {dep.version}")
            report.append(f"- File: {dep.file}")
            report.append(f"- Category: {dep.category}")
            if dep.vulnerabilities:
                report.append(f"- Vulnerabilities: {len(dep.vulnerabilities)}")
            report.append("")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"Report saved to {output_file}")
        
        return report_text
    
    def export_json(self, result: AnalysisResult, output_file: Path) -> None:
        """Export analysis results as JSON."""
        data = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_dependencies": result.total_dependencies,
                "production_dependencies": result.production_dependencies,
                "development_dependencies": result.development_dependencies,
                "security_issues": result.security_issues,
                "outdated_packages": result.outdated_packages,
                "heavy_packages": result.heavy_packages,
            },
            "recommendations": result.recommendations,
            "dependencies": [asdict(dep) for dep in result.dependencies]
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"JSON export saved to {output_file}")

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python dependency_analyzer.py <project_root> [--json] [--output <file>]")
        sys.exit(1)
    
    project_root = Path(sys.argv[1])
    if not project_root.exists():
        print(f"Error: Project root {project_root} does not exist")
        sys.exit(1)
    
    # Parse arguments
    export_json = "--json" in sys.argv
    output_file = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_file = Path(sys.argv[idx + 1])
    
    # Run analysis
    analyzer = DependencyAnalyzer(project_root)
    result = analyzer.analyze()
    
    # Generate report
    if output_file:
        report = analyzer.generate_report(result, output_file)
    else:
        report = analyzer.generate_report(result)
        print(report)
    
    # Export JSON if requested
    if export_json:
        json_file = output_file.with_suffix('.json') if output_file else Path("dependency_analysis.json")
        analyzer.export_json(result, json_file)

if __name__ == "__main__":
    main() 