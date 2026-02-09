"""
Generador de Reportes - Face Swap Modules
==========================================
Genera reportes automáticos del estado del proyecto.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import importlib.util


def check_module(module_name: str) -> Dict:
    """Verifica estado de un módulo."""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return {'status': 'missing', 'path': None}
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return {
            'status': 'ok',
            'path': str(spec.origin) if spec.origin else None,
            'version': getattr(module, '__version__', 'unknown')
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}


def count_lines(file_path: Path) -> int:
    """Cuenta líneas en un archivo."""
    try:
        return len(file_path.read_text(encoding='utf-8').splitlines())
    except:
        return 0


def generate_report() -> str:
    """Genera reporte completo del proyecto."""
    base_dir = Path(__file__).parent
    
    report = []
    report.append("=" * 80)
    report.append("REPORTE DEL PROYECTO - Face Swap Modules")
    report.append("=" * 80)
    report.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Módulos principales
    report.append("📦 MÓDULOS PRINCIPALES")
    report.append("-" * 80)
    modules = [
        'face_swap_modules.base',
        'face_swap_modules.face_detector',
        'face_swap_modules.landmark_extractor',
        'face_swap_modules.face_analyzer',
        'face_swap_modules.color_corrector',
        'face_swap_modules.blending_engine',
        'face_swap_modules.quality_enhancer',
        'face_swap_modules.post_processor',
        'face_swap_modules.optimizations',
        'face_swap_modules.constants',
        'face_swap_modules.advanced_enhancements',
    ]
    
    for module in modules:
        result = check_module(module)
        status_icon = "✅" if result['status'] == 'ok' else "❌"
        report.append(f"{status_icon} {module}: {result['status']}")
        if result.get('version'):
            report.append(f"   Versión: {result['version']}")
    
    report.append("")
    
    # Documentación
    report.append("📚 DOCUMENTACIÓN")
    report.append("-" * 80)
    doc_files = list(base_dir.glob("*.md"))
    total_doc_lines = 0
    for doc_file in sorted(doc_files):
        lines = count_lines(doc_file)
        total_doc_lines += lines
        report.append(f"  {doc_file.name}: {lines} líneas")
    
    report.append(f"  Total: {len(doc_files)} documentos, {total_doc_lines} líneas")
    report.append("")
    
    # Herramientas
    report.append("🛠️ HERRAMIENTAS")
    report.append("-" * 80)
    tool_files = [
        'validate_modules.py',
        'benchmark.py',
        'demo.py',
        'setup.py',
        'check_dependencies.py',
        'generate_report.py',
        'face_swap_pipeline.py',
    ]
    
    for tool in tool_files:
        tool_path = base_dir / tool
        if tool_path.exists():
            lines = count_lines(tool_path)
            report.append(f"  ✅ {tool}: {lines} líneas")
        else:
            report.append(f"  ❌ {tool}: No encontrado")
    
    report.append("")
    
    # Tests
    report.append("🧪 TESTS")
    report.append("-" * 80)
    test_dir = base_dir / 'tests'
    if test_dir.exists():
        test_files = list(test_dir.glob("*.py"))
        total_test_lines = 0
        for test_file in test_files:
            lines = count_lines(test_file)
            total_test_lines += lines
            report.append(f"  {test_file.name}: {lines} líneas")
        report.append(f"  Total: {len(test_files)} archivos, {total_test_lines} líneas")
    else:
        report.append("  ⚠️ Directorio tests no encontrado")
    
    report.append("")
    
    # Resumen
    report.append("📊 RESUMEN")
    report.append("-" * 80)
    report.append(f"  Módulos principales: {len([m for m in modules if check_module(m)['status'] == 'ok'])}/{len(modules)}")
    report.append(f"  Documentos: {len(doc_files)}")
    report.append(f"  Herramientas: {len([t for t in tool_files if (base_dir / t).exists()])}")
    report.append(f"  Tests: {len(test_files) if test_dir.exists() else 0}")
    report.append("")
    
    report.append("=" * 80)
    report.append("✅ Reporte generado exitosamente")
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Genera reporte del proyecto')
    parser.add_argument('-o', '--output', type=str, default='project_report.txt',
                       help='Archivo de salida (default: project_report.txt)')
    
    args = parser.parse_args()
    
    print("Generando reporte del proyecto...")
    report = generate_report()
    
    # Mostrar en consola
    print()
    print(report)
    
    # Guardar en archivo
    output_path = Path(args.output)
    output_path.write_text(report, encoding='utf-8')
    print(f"\n✓ Reporte guardado en: {output_path}")


if __name__ == '__main__':
    main()








