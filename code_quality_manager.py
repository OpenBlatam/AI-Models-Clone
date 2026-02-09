#!/usr/bin/env python3
"""
Code Quality Manager
Comprehensive code quality management system with formatting, linting, and metrics
"""

import os
import sys
import subprocess
import asyncio
import logging
import time
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import black
import isort
import flake8.api
import mypy.api
from loguru import logger

class QualityLevel(Enum):
    """Quality levels for code standards."""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    ENTERPRISE = "enterprise"

class CodeIssue(Enum):
    """Types of code quality issues."""
    FORMATTING = "formatting"
    LINTING = "linting"
    TYPE_CHECKING = "type_checking"
    COMPLEXITY = "complexity"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    PERFORMANCE = "performance"

@dataclass
class QualityIssue:
    """Represents a code quality issue."""
    file_path: str
    line_number: int
    column: int
    issue_type: CodeIssue
    message: str
    severity: str
    rule_id: Optional[str] = None
    fix_suggestion: Optional[str] = None

@dataclass
class QualityMetrics:
    """Code quality metrics."""
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    functions: int = 0
    classes: int = 0
    complexity_score: float = 0.0
    maintainability_index: float = 0.0
    documentation_coverage: float = 0.0
    type_coverage: float = 0.0
    test_coverage: float = 0.0
    security_score: float = 0.0
    performance_score: float = 0.0

@dataclass
class QualityConfig:
    """Configuration for code quality checks."""
    max_line_length: int = 88
    max_complexity: int = 10
    max_function_length: int = 50
    max_class_length: int = 200
    min_documentation_coverage: float = 80.0
    min_type_coverage: float = 90.0
    min_test_coverage: float = 95.0
    quality_level: QualityLevel = QualityLevel.STRICT
    ignore_patterns: List[str] = field(default_factory=list)
    exclude_dirs: List[str] = field(default_factory=lambda: ["__pycache__", ".git", "venv", "node_modules"])

class CodeQualityManager:
    """Comprehensive code quality management system."""
    
    def __init__(self, config: QualityConfig):
        self.config = config
        self.issues: List[QualityIssue] = []
        self.metrics: Dict[str, QualityMetrics] = {}
        self.executor = ThreadPoolExecutor(max_workers=os.cpu_count())
        
    async def analyze_codebase(self, root_path: str) -> Dict[str, Any]:
        """Analyze entire codebase for quality issues."""
        logger.info(f"Starting codebase analysis: {root_path}")
        
        start_time = time.time()
        python_files = self._find_python_files(root_path)
        
        # Run all quality checks in parallel
        tasks = [
            self._check_formatting(python_files),
            self._check_linting(python_files),
            self._check_type_safety(python_files),
            self._check_complexity(python_files),
            self._check_documentation(python_files),
            self._check_security(python_files),
            self._check_performance(python_files)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Compile results
        analysis_result = {
            "total_files": len(python_files),
            "total_issues": len(self.issues),
            "analysis_time": time.time() - start_time,
            "metrics": self.metrics,
            "issues_by_type": self._group_issues_by_type(),
            "quality_score": self._calculate_quality_score(),
            "recommendations": self._generate_recommendations()
        }
        
        logger.info(f"Analysis completed: {len(self.issues)} issues found")
        return analysis_result
    
    async def _check_formatting(self, files: List[str]) -> List[QualityIssue]:
        """Check code formatting using Black."""
        issues = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file needs formatting
                try:
                    black.format_file_contents(content, fast=False, mode=black.FileMode())
                except black.NothingChanged:
                    pass  # File is already properly formatted
                except Exception as e:
                    issues.append(QualityIssue(
                        file_path=file_path,
                        line_number=1,
                        column=1,
                        issue_type=CodeIssue.FORMATTING,
                        message=f"Formatting issue: {str(e)}",
                        severity="warning"
                    ))
                    
            except Exception as e:
                logger.error(f"Error checking formatting for {file_path}: {e}")
        
        self.issues.extend(issues)
        return issues
    
    async def _check_linting(self, files: List[str]) -> List[QualityIssue]:
        """Check code using flake8."""
        issues = []
        
        for file_path in files:
            try:
                # Run flake8 on the file
                result = subprocess.run(
                    [sys.executable, "-m", "flake8", file_path, "--format=json"],
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    lint_results = json.loads(result.stdout)
                    for lint_issue in lint_results:
                        issues.append(QualityIssue(
                            file_path=file_path,
                            line_number=lint_issue["line_number"],
                            column=lint_issue["column_number"],
                            issue_type=CodeIssue.LINTING,
                            message=lint_issue["text"],
                            severity="warning",
                            rule_id=lint_issue["code"]
                        ))
                        
            except Exception as e:
                logger.error(f"Error checking linting for {file_path}: {e}")
        
        self.issues.extend(issues)
        return issues
    
    async def _check_type_safety(self, files: List[str]) -> List[QualityIssue]:
        """Check type safety using mypy."""
        issues = []
        
        for file_path in files:
            try:
                # Run mypy on the file
                result = subprocess.run(
                    [sys.executable, "-m", "mypy", file_path, "--json"],
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    mypy_results = json.loads(result.stdout)
                    for mypy_issue in mypy_results:
                        issues.append(QualityIssue(
                            file_path=file_path,
                            line_number=mypy_issue["line"],
                            column=mypy_issue["column"],
                            issue_type=CodeIssue.TYPE_CHECKING,
                            message=mypy_issue["message"],
                            severity="error" if mypy_issue["severity"] == "error" else "warning"
                        ))
                        
            except Exception as e:
                logger.error(f"Error checking type safety for {file_path}: {e}")
        
        self.issues.extend(issues)
        return issues
    
    async def _check_complexity(self, files: List[str]) -> List[QualityIssue]:
        """Check code complexity metrics."""
        issues = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                complexity_analyzer = ComplexityAnalyzer()
                complexity_analyzer.visit(tree)
                
                # Check function complexity
                for func_name, complexity in complexity_analyzer.function_complexity.items():
                    if complexity > self.config.max_complexity:
                        issues.append(QualityIssue(
                            file_path=file_path,
                            line_number=1,  # Would need to track actual line numbers
                            column=1,
                            issue_type=CodeIssue.COMPLEXITY,
                            message=f"Function '{func_name}' has complexity {complexity}, exceeds limit of {self.config.max_complexity}",
                            severity="warning"
                        ))
                
                # Store metrics
                self.metrics[file_path] = QualityMetrics(
                    total_lines=len(content.splitlines()),
                    functions=len(complexity_analyzer.function_complexity),
                    classes=len(complexity_analyzer.classes),
                    complexity_score=complexity_analyzer.average_complexity
                )
                
            except Exception as e:
                logger.error(f"Error checking complexity for {file_path}: {e}")
        
        self.issues.extend(issues)
        return issues
    
    async def _check_documentation(self, files: List[str]) -> List[QualityIssue]:
        """Check documentation coverage."""
        issues = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc_analyzer = DocumentationAnalyzer()
                tree = ast.parse(content)
                doc_analyzer.visit(tree)
                
                coverage = doc_analyzer.calculate_coverage()
                if coverage < self.config.min_documentation_coverage:
                    issues.append(QualityIssue(
                        file_path=file_path,
                        line_number=1,
                        column=1,
                        issue_type=CodeIssue.DOCUMENTATION,
                        message=f"Documentation coverage {coverage:.1f}% is below minimum {self.config.min_documentation_coverage}%",
                        severity="warning"
                    ))
                
                # Update metrics
                if file_path in self.metrics:
                    self.metrics[file_path].documentation_coverage = coverage
                
            except Exception as e:
                logger.error(f"Error checking documentation for {file_path}: {e}")
        
        self.issues.extend(issues)
        return issues
    
    async def _check_security(self, files: List[str]) -> List[QualityIssue]:
        """Check for security issues."""
        issues = []
        security_patterns = {
            r"eval\(": "Use of eval() is dangerous",
            r"exec\(": "Use of exec() is dangerous",
            r"subprocess\.call\(": "Consider using subprocess.run() instead",
            r"pickle\.loads\(": "Unsafe deserialization with pickle",
            r"input\(": "Consider using getpass() for sensitive input",
            r"password.*=.*['\"]": "Hardcoded password detected",
            r"api_key.*=.*['\"]": "Hardcoded API key detected"
        }
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern, message in security_patterns.items():
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_number = content[:match.start()].count('\n') + 1
                        issues.append(QualityIssue(
                            file_path=file_path,
                            line_number=line_number,
                            column=match.start() - content.rfind('\n', 0, match.start()) - 1,
                            issue_type=CodeIssue.SECURITY,
                            message=message,
                            severity="error"
                        ))
                
            except Exception as e:
                logger.error(f"Error checking security for {file_path}: {e}")
        
        self.issues.extend(issues)
        return issues
    
    async def _check_performance(self, files: List[str]) -> List[QualityIssue]:
        """Check for performance issues."""
        issues = []
        performance_patterns = {
            r"for.*in.*range\(len\(": "Consider using enumerate() instead of range(len())",
            r"\.append\(.*\)\s*in\s*loop": "Consider using list comprehension for better performance",
            r"import\s+\*": "Avoid wildcard imports for better performance",
            r"time\.sleep\(": "Consider using asyncio.sleep() in async contexts"
        }
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern, message in performance_patterns.items():
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_number = content[:match.start()].count('\n') + 1
                        issues.append(QualityIssue(
                            file_path=file_path,
                            line_number=line_number,
                            column=match.start() - content.rfind('\n', 0, match.start()) - 1,
                            issue_type=CodeIssue.PERFORMANCE,
                            message=message,
                            severity="warning"
                        ))
                
            except Exception as e:
                logger.error(f"Error checking performance for {file_path}: {e}")
        
        self.issues.extend(issues)
        return issues
    
    def _find_python_files(self, root_path: str) -> List[str]:
        """Find all Python files in the codebase."""
        python_files = []
        root = Path(root_path)
        
        for file_path in root.rglob("*.py"):
            # Skip excluded directories
            if any(excluded in str(file_path) for excluded in self.config.exclude_dirs):
                continue
            
            # Skip files matching ignore patterns
            if any(re.search(pattern, str(file_path)) for pattern in self.config.ignore_patterns):
                continue
            
            python_files.append(str(file_path))
        
        return python_files
    
    def _group_issues_by_type(self) -> Dict[CodeIssue, List[QualityIssue]]:
        """Group issues by type."""
        grouped = {}
        for issue in self.issues:
            if issue.issue_type not in grouped:
                grouped[issue.issue_type] = []
            grouped[issue.issue_type].append(issue)
        return grouped
    
    def _calculate_quality_score(self) -> float:
        """Calculate overall quality score."""
        if not self.issues:
            return 100.0
        
        # Weight different issue types
        weights = {
            CodeIssue.SECURITY: 3.0,
            CodeIssue.TYPE_CHECKING: 2.0,
            CodeIssue.LINTING: 1.0,
            CodeIssue.FORMATTING: 0.5,
            CodeIssue.COMPLEXITY: 1.5,
            CodeIssue.DOCUMENTATION: 1.0,
            CodeIssue.PERFORMANCE: 1.0
        }
        
        total_weighted_issues = sum(
            weights.get(issue.issue_type, 1.0) 
            for issue in self.issues
        )
        
        # Calculate score (higher is better)
        max_possible_issues = len(self.issues) * max(weights.values())
        score = max(0, 100 - (total_weighted_issues / max_possible_issues) * 100)
        
        return round(score, 2)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        issue_counts = {}
        for issue in self.issues:
            issue_counts[issue.issue_type] = issue_counts.get(issue.issue_type, 0) + 1
        
        if issue_counts.get(CodeIssue.FORMATTING, 0) > 0:
            recommendations.append("Run 'black' to format code automatically")
        
        if issue_counts.get(CodeIssue.LINTING, 0) > 0:
            recommendations.append("Fix flake8 linting issues")
        
        if issue_counts.get(CodeIssue.TYPE_CHECKING, 0) > 0:
            recommendations.append("Add type hints and fix mypy errors")
        
        if issue_counts.get(CodeIssue.SECURITY, 0) > 0:
            recommendations.append("Address security vulnerabilities immediately")
        
        if issue_counts.get(CodeIssue.COMPLEXITY, 0) > 0:
            recommendations.append("Refactor complex functions to reduce cyclomatic complexity")
        
        if issue_counts.get(CodeIssue.DOCUMENTATION, 0) > 0:
            recommendations.append("Add comprehensive docstrings and comments")
        
        return recommendations

class ComplexityAnalyzer(ast.NodeVisitor):
    """Analyze code complexity."""
    
    def __init__(self):
        self.function_complexity = {}
        self.classes = set()
        self.current_function = None
        self.complexity = 0
    
    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.complexity = 1  # Base complexity
        
        # Visit function body
        self.generic_visit(node)
        
        self.function_complexity[node.name] = self.complexity
        self.current_function = None
    
    def visit_ClassDef(self, node):
        self.classes.add(node.name)
        self.generic_visit(node)
    
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    @property
    def average_complexity(self) -> float:
        """Calculate average complexity."""
        if not self.function_complexity:
            return 0.0
        return sum(self.function_complexity.values()) / len(self.function_complexity)

class DocumentationAnalyzer(ast.NodeVisitor):
    """Analyze documentation coverage."""
    
    def __init__(self):
        self.functions = 0
        self.classes = 0
        self.documented_functions = 0
        self.documented_classes = 0
    
    def visit_FunctionDef(self, node):
        self.functions += 1
        if ast.get_docstring(node):
            self.documented_functions += 1
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self.classes += 1
        if ast.get_docstring(node):
            self.documented_classes += 1
        self.generic_visit(node)
    
    def calculate_coverage(self) -> float:
        """Calculate documentation coverage percentage."""
        total_items = self.functions + self.classes
        if total_items == 0:
            return 100.0
        
        documented_items = self.documented_functions + self.documented_classes
        return (documented_items / total_items) * 100

# Quality manager instance
quality_manager = CodeQualityManager(QualityConfig())

def get_quality_manager() -> CodeQualityManager:
    """Get the quality manager instance."""
    return quality_manager

async def analyze_code_quality(root_path: str = ".") -> Dict[str, Any]:
    """Analyze code quality for the entire codebase."""
    return await quality_manager.analyze_codebase(root_path)

def format_code(file_path: str) -> bool:
    """Format a single file using Black."""
    try:
        black.format_file_in_place(
            Path(file_path),
            fast=False,
            mode=black.FileMode()
        )
        return True
    except Exception as e:
        logger.error(f"Error formatting {file_path}: {e}")
        return False

def sort_imports(file_path: str) -> bool:
    """Sort imports in a file using isort."""
    try:
        isort.file(file_path)
        return True
    except Exception as e:
        logger.error(f"Error sorting imports in {file_path}: {e}")
        return False 