#!/usr/bin/env python3
"""
Refactor System - Sistema de análisis y refactorización de código Python
"""

from typing import Any, List, Dict, Optional, Set
import os
import ast
import json
from datetime import datetime
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RefactorResult:
    """Resultado del análisis de un archivo"""
    file_path: str
    issues_found: List[str]
    suggestions: List[str]
    complexity_score: float
    refactored: bool


class CodeAnalyzer:
    """Analizador de código para encontrar oportunidades de refactorización"""
    
    def __init__(self) -> None:
        self.issues: List[str] = []
        self.suggestions: List[str] = []
    
    def analyze_file(self, file_path: str) -> RefactorResult:
        """Analiza un archivo Python y encuentra oportunidades de refactoring"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            issues: List[str] = []
            suggestions: List[str] = []
            
            # Analizar complejidad
            complexity = self.calculate_complexity(tree)
            
            # Buscar patrones problemáticos
            issues.extend(self.find_long_functions(tree))
            issues.extend(self.find_duplicate_code(tree))
            issues.extend(self.find_global_variables(tree))
            issues.extend(self.find_magic_numbers(tree))
            
            # Generar sugerencias
            suggestions.extend(self.suggest_async_patterns(tree))
            suggestions.extend(self.suggest_type_hints(tree))
            suggestions.extend(self.suggest_error_handling(tree))
            suggestions.extend(self.suggest_optimizations(tree))
            
            return RefactorResult(
                file_path=file_path,
                issues_found=issues,
                suggestions=suggestions,
                complexity_score=complexity,
                refactored=False
            )
            
        except (IOError, OSError) as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return RefactorResult(
                file_path=file_path,
                issues_found=[f"Error reading file: {str(e)}"],
                suggestions=[],
                complexity_score=0.0,
                refactored=False
            )
        except SyntaxError as e:
            logger.error(f"Syntax error in file {file_path}: {e}")
            return RefactorResult(
                file_path=file_path,
                issues_found=[f"Syntax error: {str(e)}"],
                suggestions=[],
                complexity_score=0.0,
                refactored=False
            )
        except Exception as e:
            logger.error(f"Unexpected error parsing file {file_path}: {e}", exc_info=True)
            return RefactorResult(
                file_path=file_path,
                issues_found=[f"Error parsing file: {str(e)}"],
                suggestions=[],
                complexity_score=0.0,
                refactored=False
            )
    
    def calculate_complexity(self, tree: ast.AST) -> float:
        """Calcula la complejidad ciclomática"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def find_long_functions(self, tree: ast.AST) -> List[str]:
        """Encuentra funciones muy largas"""
        issues: List[str] = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                lines = len(node.body)
                if lines > 50:
                    issues.append(f"Función '{node.name}' muy larga ({lines} líneas)")
        
        return issues
    
    def find_duplicate_code(self, tree: ast.AST) -> List[str]:
        """Encuentra código duplicado"""
        # Implementación simplificada
        return []
    
    def find_global_variables(self, tree: ast.AST) -> List[str]:
        """Encuentra variables globales"""
        issues: List[str] = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                issues.append(f"Uso de variables globales en línea {node.lineno}")
        
        return issues
    
    def find_magic_numbers(self, tree: ast.AST) -> List[str]:
        """Encuentra números mágicos"""
        issues: List[str] = []
        
        for node in ast.walk(tree):
            # Para Python 3.8+, usar ast.Constant en lugar de ast.Num
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value > 10 or node.value < -10:
                    issues.append(f"Número mágico {node.value} en línea {node.lineno}")
            # Compatibilidad con versiones anteriores
            elif hasattr(ast, 'Num') and isinstance(node, ast.Num):
                if isinstance(node.n, (int, float)) and (node.n > 10 or node.n < -10):
                    issues.append(f"Número mágico {node.n} en línea {node.lineno}")
        
        return issues
    
    def suggest_async_patterns(self, tree: ast.AST) -> List[str]:
        """Sugiere patrones async"""
        suggestions: List[str] = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Buscar funciones que podrían ser async
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        func_name: str = ""
                        if isinstance(child.func, ast.Name):
                            func_name = child.func.id
                        elif isinstance(child.func, ast.Attribute):
                            func_name = child.func.attr
                        
                        if any(keyword in func_name.lower() for keyword in ['request', 'http', 'api', 'fetch']):
                            suggestions.append(f"Considerar hacer '{node.name}' async")
                            break
        
        return suggestions
    
    def suggest_type_hints(self, tree: ast.AST) -> List[str]:
        """Sugiere type hints"""
        suggestions: List[str] = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.returns and not node.args.annotations:
                    suggestions.append(f"Agregar type hints a función '{node.name}'")
        
        return suggestions
    
    def suggest_error_handling(self, tree: ast.AST) -> List[str]:
        """Sugiere mejor manejo de errores"""
        suggestions: List[str] = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                if not node.handlers:
                    suggestions.append("Agregar manejo de excepciones")
        
        return suggestions
    
    def suggest_optimizations(self, tree: ast.AST) -> List[str]:
        """Sugiere optimizaciones"""
        suggestions: List[str] = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ListComp):
                suggestions.append("Usar list comprehension para mejor rendimiento")
            elif isinstance(node, ast.GeneratorExp):
                suggestions.append("Usar generator expressions para memoria")
        
        return suggestions


class RefactorEngine:
    """Motor de refactorización que coordina el análisis"""
    
    def __init__(self) -> None:
        self.analyzer = CodeAnalyzer()
        self.results: List[RefactorResult] = []
    
    def scan_directory(self, directory: str) -> List[RefactorResult]:
        """Escanea un directorio en busca de archivos Python"""
        results: List[RefactorResult] = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    result = self.analyzer.analyze_file(file_path)
                    results.append(result)
        
        return results
    
    def generate_report(self, results: List[RefactorResult]) -> Dict[str, Any]:
        """Genera un reporte de refactoring"""
        total_files = len(results)
        files_with_issues = len([r for r in results if r.issues_found])
        total_issues = sum(len(r.issues_found) for r in results)
        total_suggestions = sum(len(r.suggestions) for r in results)
        
        # Archivos más complejos
        complex_files = sorted(results, key=lambda x: x.complexity_score, reverse=True)[:5]
        
        # Issues más comunes
        all_issues: List[str] = []
        for result in results:
            all_issues.extend(result.issues_found)
        
        issue_counts: Dict[str, int] = {}
        for issue in all_issues:
            issue_type = issue.split(':')[0] if ':' in issue else issue
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        return {
            "summary": {
                "total_files": total_files,
                "files_with_issues": files_with_issues,
                "total_issues": total_issues,
                "total_suggestions": total_suggestions,
                "average_complexity": sum(r.complexity_score for r in results) / total_files if total_files > 0 else 0
            },
            "complex_files": [
                {
                    "file": r.file_path,
                    "complexity": r.complexity_score,
                    "issues": len(r.issues_found)
                } for r in complex_files
            ],
            "common_issues": issue_counts,
            "detailed_results": [
                {
                    "file": r.file_path,
                    "issues": r.issues_found,
                    "suggestions": r.suggestions,
                    "complexity": r.complexity_score
                } for r in results
            ]
        }


def main() -> None:
    """Función principal"""
    logging.basicConfig(level=logging.INFO)
    
    logger.info("🔧 SISTEMA DE REFACTORING")
    logger.info("=" * 50)
    
    # Escanear directorio actual
    current_dir = os.getcwd()
    logger.info(f"📁 Escaneando: {current_dir}")
    
    engine = RefactorEngine()
    results = engine.scan_directory(current_dir)
    
    if not results:
        logger.info("❌ No se encontraron archivos Python para analizar")
        return
    
    # Generar reporte
    report = engine.generate_report(results)
    
    logger.info(f"\n📊 RESULTADOS DEL ANÁLISIS:")
    logger.info(f"  📄 Archivos analizados: {report['summary']['total_files']}")
    logger.info(f"  ⚠️  Archivos con problemas: {report['summary']['files_with_issues']}")
    logger.info(f"  🐛 Total de problemas: {report['summary']['total_issues']}")
    logger.info(f"  💡 Total de sugerencias: {report['summary']['total_suggestions']}")
    logger.info(f"  📈 Complejidad promedio: {report['summary']['average_complexity']:.1f}")
    
    # Mostrar archivos más complejos
    if report['complex_files']:
        logger.info(f"\n🔴 ARCHIVOS MÁS COMPLEJOS:")
        for i, file_info in enumerate(report['complex_files'][:3], 1):
            logger.info(f"  {i}. {file_info['file']}")
            logger.info(f"     Complejidad: {file_info['complexity']:.1f}")
            logger.info(f"     Problemas: {file_info['issues']}")
    
    # Mostrar problemas más comunes
    if report['common_issues']:
        logger.info(f"\n⚠️  PROBLEMAS MÁS COMUNES:")
        for issue, count in sorted(report['common_issues'].items(), key=lambda x: x[1], reverse=True)[:5]:
            logger.info(f"  • {issue}: {count} veces")
    
    # Guardar reporte
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"refactor_report_{timestamp}.json"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    except (IOError, OSError) as e:
        logger.error(f"Error writing report file: {e}")
        return
    
    logger.info(f"\n✅ Análisis completado!")
    logger.info(f"📄 Reporte guardado: {report_file}")
    
    # Sugerencias de acción
    if report['summary']['total_issues'] > 0:
        logger.info(f"\n🎯 PRÓXIMOS PASOS:")
        logger.info(f"  1. Revisar archivos más complejos")
        logger.info(f"  2. Implementar type hints")
        logger.info(f"  3. Agregar manejo de errores")
        logger.info(f"  4. Optimizar funciones largas")
        logger.info(f"  5. Implementar patrones async")


if __name__ == "__main__":
    main()
