#!/usr/bin/env python3
"""
Legacy Code Analysis and Cleanup Script

This script analyzes all the legacy files in the features directory,
categorizes them by functionality, identifies duplications, and provides
recommendations for the modular migration.
"""

import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import hashlib

class LegacyAnalyzer:
    """Analyzes legacy code files for migration planning."""
    
    def __init__(self, features_dir: str = "."):
        self.features_dir = Path(features_dir)
        self.analysis_results = {
            "files": {},
            "duplications": [],
            "categories": defaultdict(list),
            "dependencies": defaultdict(set),
            "recommendations": []
        }
        
    def analyze_all_files(self) -> Dict:
        """Analyze all Python files in the features directory."""
        print("🔍 Starting legacy code analysis...")
        
        python_files = list(self.features_dir.glob("*.py"))
        print(f"Found {len(python_files)} Python files to analyze")
        
        for file_path in python_files:
            if file_path.name.startswith("__"):
                continue
                
            try:
                analysis = self.analyze_file(file_path)
                self.analysis_results["files"][str(file_path)] = analysis
                self.categorize_file(file_path, analysis)
            except Exception as e:
                print(f"❌ Error analyzing {file_path}: {e}")
        
        self.find_duplications()
        self.analyze_dependencies()
        self.generate_recommendations()
        
        return self.analysis_results
    
    def analyze_file(self, file_path: Path) -> Dict:
        """Analyze a single Python file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Basic metrics
        lines = content.split('\n')
        size_kb = len(content) / 1024
        
        # AST analysis for imports and functions
        imports = self.extract_imports(content)
        functions = self.extract_functions(content)
        classes = self.extract_classes(content)
        
        # Content analysis
        keywords = self.extract_keywords(content)
        complexity_score = self.calculate_complexity(content)
        
        return {
            "size_kb": round(size_kb, 1),
            "lines": len(lines),
            "imports": imports,
            "functions": functions,
            "classes": classes,
            "keywords": keywords,
            "complexity": complexity_score,
            "content_hash": hashlib.md5(content.encode()).hexdigest()
        }
    
    def extract_imports(self, content: str) -> List[str]:
        """Extract import statements from code."""
        imports = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except:
            # Fallback to regex if AST parsing fails
            import_patterns = [
                r'import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import'
            ]
            for pattern in import_patterns:
                imports.extend(re.findall(pattern, content))
        
        return list(set(imports))
    
    def extract_functions(self, content: str) -> List[str]:
        """Extract function definitions from code."""
        functions = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
        except:
            # Fallback to regex
            functions = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
        
        return functions
    
    def extract_classes(self, content: str) -> List[str]:
        """Extract class definitions from code."""
        classes = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
        except:
            # Fallback to regex
            classes = re.findall(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
        
        return classes
    
    def extract_keywords(self, content: str) -> List[str]:
        """Extract relevant keywords from content."""
        keyword_patterns = {
            'production': r'\b(production|prod|deploy)\b',
            'optimization': r'\b(optim|performance|speed|fast)\b',
            'copywriting': r'\b(copy|content|text|writing)\b',
            'ai': r'\b(ai|openai|gpt|llm|model)\b',
            'cache': r'\b(cache|redis|memory)\b',
            'async': r'\b(async|await|asyncio)\b',
            'api': r'\b(api|fastapi|router|endpoint)\b',
            'database': r'\b(db|database|sql|postgres)\b',
            'monitoring': r'\b(monitor|metric|prometheus)\b',
            'benchmark': r'\b(benchmark|test|measure)\b'
        }
        
        found_keywords = []
        content_lower = content.lower()
        
        for keyword, pattern in keyword_patterns.items():
            if re.search(pattern, content_lower, re.IGNORECASE):
                found_keywords.append(keyword)
        
        return found_keywords
    
    def calculate_complexity(self, content: str) -> int:
        """Calculate a simple complexity score."""
        # Count various complexity indicators
        complexity = 0
        
        # Function and class count
        complexity += len(re.findall(r'\bdef\s+', content))
        complexity += len(re.findall(r'\bclass\s+', content)) * 2
        
        # Control flow
        complexity += len(re.findall(r'\b(if|for|while|try|except)\b', content))
        
        # Async complexity
        complexity += len(re.findall(r'\b(async|await)\b', content)) * 2
        
        return complexity
    
    def categorize_file(self, file_path: Path, analysis: Dict):
        """Categorize file based on its content and name."""
        filename = file_path.name.lower()
        keywords = analysis["keywords"]
        
        # Category mapping
        categories = {
            "production": ["production", "deploy", "main"],
            "optimization": ["optim", "performance", "ultra", "quantum"],
            "copywriting": ["copywriting", "copy", "content"],
            "benchmark": ["benchmark", "test", "demo"],
            "nexus": ["nexus"],
            "infrastructure": ["docker", "nginx", "config"],
            "cache": ["cache"],
            "api": ["api", "app"],
            "utils": ["util", "helper"],
            "legacy": []  # Default category
        }
        
        # Determine primary category
        primary_category = "legacy"
        max_matches = 0
        
        for category, terms in categories.items():
            matches = sum(1 for term in terms if term in filename)
            matches += sum(1 for kw in keywords if kw in terms)
            
            if matches > max_matches:
                max_matches = matches
                primary_category = category
        
        self.analysis_results["categories"][primary_category].append({
            "file": str(file_path),
            "analysis": analysis,
            "confidence": max_matches
        })
    
    def find_duplications(self):
        """Find potential code duplications."""
        print("🔍 Analyzing code duplications...")
        
        # Group by content hash for exact duplicates
        hash_groups = defaultdict(list)
        for file_path, analysis in self.analysis_results["files"].items():
            hash_groups[analysis["content_hash"]].append(file_path)
        
        # Find exact duplicates
        for content_hash, files in hash_groups.items():
            if len(files) > 1:
                self.analysis_results["duplications"].append({
                    "type": "exact",
                    "files": files,
                    "hash": content_hash
                })
        
        # Find similar files by function overlap
        files_list = list(self.analysis_results["files"].items())
        for i, (file1, analysis1) in enumerate(files_list):
            for file2, analysis2 in files_list[i+1:]:
                similarity = self.calculate_similarity(analysis1, analysis2)
                if similarity > 0.7:  # 70% similarity threshold
                    self.analysis_results["duplications"].append({
                        "type": "similar",
                        "files": [file1, file2],
                        "similarity": similarity
                    })
    
    def calculate_similarity(self, analysis1: Dict, analysis2: Dict) -> float:
        """Calculate similarity between two file analyses."""
        # Function name overlap
        functions1 = set(analysis1["functions"])
        functions2 = set(analysis2["functions"])
        
        if not functions1 and not functions2:
            return 0.0
        
        intersection = len(functions1.intersection(functions2))
        union = len(functions1.union(functions2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def analyze_dependencies(self):
        """Analyze dependencies between files."""
        print("🔍 Analyzing file dependencies...")
        
        # Simple dependency analysis based on imports
        for file_path, analysis in self.analysis_results["files"].items():
            file_name = Path(file_path).stem
            
            for other_file, other_analysis in self.analysis_results["files"].items():
                if file_path == other_file:
                    continue
                
                other_name = Path(other_file).stem
                
                # Check if this file imports the other
                for import_name in analysis["imports"]:
                    if other_name in import_name or import_name in other_name:
                        self.analysis_results["dependencies"][file_path].add(other_file)
    
    def generate_recommendations(self):
        """Generate migration recommendations."""
        print("🎯 Generating migration recommendations...")
        
        recommendations = []
        
        # Analyze each category
        for category, files in self.analysis_results["categories"].items():
            if not files:
                continue
            
            total_size = sum(f["analysis"]["size_kb"] for f in files)
            total_files = len(files)
            
            if category == "production":
                recommendations.append({
                    "priority": "HIGH",
                    "category": category,
                    "action": "CONSOLIDATE",
                    "description": f"Consolidate {total_files} production files ({total_size:.1f}KB) into production/ module",
                    "files": [f["file"] for f in files],
                    "target_module": "production/config/"
                })
            
            elif category == "optimization":
                recommendations.append({
                    "priority": "HIGH", 
                    "category": category,
                    "action": "MODULARIZE",
                    "description": f"Create optimization module from {total_files} files ({total_size:.1f}KB)",
                    "files": [f["file"] for f in files],
                    "target_module": "modules/optimization/"
                })
            
            elif category == "copywriting":
                recommendations.append({
                    "priority": "MEDIUM",
                    "category": category,
                    "action": "MODULARIZE",
                    "description": f"Create copywriting module from {total_files} files ({total_size:.1f}KB)",
                    "files": [f["file"] for f in files],
                    "target_module": "modules/copywriting/"
                })
            
            elif category == "benchmark":
                recommendations.append({
                    "priority": "LOW",
                    "category": category,
                    "action": "CONSOLIDATE",
                    "description": f"Consolidate {total_files} benchmark files into shared testing utilities",
                    "files": [f["file"] for f in files],
                    "target_module": "shared/testing/"
                })
        
        # Duplication recommendations
        for dup in self.analysis_results["duplications"]:
            if dup["type"] == "exact":
                recommendations.append({
                    "priority": "CRITICAL",
                    "category": "duplication",
                    "action": "REMOVE_DUPLICATES",
                    "description": f"Remove exact duplicate files: {', '.join(Path(f).name for f in dup['files'])}",
                    "files": dup["files"]
                })
        
        self.analysis_results["recommendations"] = sorted(
            recommendations, 
            key=lambda x: {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}[x["priority"]],
            reverse=True
        )
    
    def print_report(self):
        """Print a comprehensive analysis report."""
        print("\n" + "="*80)
        print("📊 LEGACY CODE ANALYSIS REPORT")
        print("="*80)
        
        # Summary
        total_files = len(self.analysis_results["files"])
        total_size = sum(f["size_kb"] for f in self.analysis_results["files"].values())
        
        print(f"\n📈 SUMMARY:")
        print(f"   Total files analyzed: {total_files}")
        print(f"   Total size: {total_size:.1f}KB")
        print(f"   Duplications found: {len(self.analysis_results['duplications'])}")
        print(f"   Recommendations: {len(self.analysis_results['recommendations'])}")
        
        # Categories
        print(f"\n📁 CATEGORIES:")
        for category, files in self.analysis_results["categories"].items():
            if files:
                size = sum(f["analysis"]["size_kb"] for f in files)
                print(f"   {category.upper()}: {len(files)} files ({size:.1f}KB)")
        
        # Top duplications
        print(f"\n🔍 TOP DUPLICATIONS:")
        for i, dup in enumerate(self.analysis_results["duplications"][:5]):
            if dup["type"] == "exact":
                print(f"   {i+1}. EXACT: {', '.join(Path(f).name for f in dup['files'])}")
            else:
                similarity = dup.get("similarity", 0) * 100
                print(f"   {i+1}. SIMILAR ({similarity:.0f}%): {', '.join(Path(f).name for f in dup['files'])}")
        
        # Top recommendations
        print(f"\n🎯 TOP RECOMMENDATIONS:")
        for i, rec in enumerate(self.analysis_results["recommendations"][:10]):
            priority_emoji = {"CRITICAL": "🚨", "HIGH": "⚡", "MEDIUM": "⚠️", "LOW": "📝"}
            emoji = priority_emoji.get(rec["priority"], "📝")
            print(f"   {emoji} {rec['priority']}: {rec['description']}")
        
        # Migration targets
        print(f"\n🏗️ MIGRATION TARGETS:")
        targets = defaultdict(list)
        for rec in self.analysis_results["recommendations"]:
            if "target_module" in rec:
                targets[rec["target_module"]].extend(rec["files"])
        
        for target, files in targets.items():
            size = sum(
                self.analysis_results["files"][f]["size_kb"] 
                for f in files 
                if f in self.analysis_results["files"]
            )
            print(f"   {target}: {len(files)} files ({size:.1f}KB)")
        
        print("\n" + "="*80)
    
    def save_report(self, output_file: str = "legacy_analysis_report.json"):
        """Save the analysis report to a JSON file."""
        import json
        
        with open(output_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        
        print(f"📄 Full report saved to {output_file}")


def main():
    """Main execution function."""
    print("🚀 Legacy Code Analyzer Starting...")
    
    # Initialize analyzer
    analyzer = LegacyAnalyzer(".")
    
    # Run analysis
    results = analyzer.analyze_all_files()
    
    # Print report
    analyzer.print_report()
    
    # Save detailed report
    analyzer.save_report()
    
    print("\n✅ Analysis complete! Check the report for migration recommendations.")
    

if __name__ == "__main__":
    main() 