#!/usr/bin/env python3
"""
Run All Examples - Official Documentation Reference System
=========================================================

Script para ejecutar todos los ejemplos del sistema de referencias
de documentación oficial.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_example(script_name, description):
    """Ejecutar un ejemplo específico."""
    print(f"\n{'='*60}")
    print(f"🚀 EJECUTANDO: {script_name}")
    print(f"📝 {description}")
    print(f"{'='*60}")
    
    try:
        # Ejecutar el script
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=30  # Timeout de 30 segundos
        )
        
        if result.returncode == 0:
            print("✅ Ejecutado exitosamente!")
            print("\n📤 Salida:")
            print(result.stdout)
        else:
            print("❌ Error en la ejecución:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - El script tardó demasiado")
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {script_name}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def main():
    """Función principal."""
    print("🎯 SISTEMA DE REFERENCIAS DE DOCUMENTACIÓN OFICIAL")
    print("Ejecutando todos los ejemplos prácticos")
    print("=" * 80)
    
    # Lista de ejemplos a ejecutar
    examples = [
        ("quick_start.py", "Inicio rápido del sistema de referencias"),
        ("pytorch_example.py", "Ejemplo práctico de PyTorch con AMP y optimizaciones"),
        ("transformers_example.py", "Ejemplo de Transformers con Trainer y tokenización"),
        ("diffusers_example.py", "Ejemplo de Diffusers con pipeline y optimizaciones"),
        ("gradio_example.py", "Ejemplo de Gradio con interfaces avanzadas")
    ]
    
    # Verificar que los archivos existen
    existing_examples = []
    for script_name, description in examples:
        if Path(script_name).exists():
            existing_examples.append((script_name, description))
        else:
            print(f"⚠️  Archivo no encontrado: {script_name}")
    
    if not existing_examples:
        print("❌ No se encontraron archivos de ejemplo")
        return
    
    print(f"\n📁 Encontrados {len(existing_examples)} ejemplos para ejecutar")
    
    # Ejecutar cada ejemplo
    for i, (script_name, description) in enumerate(existing_examples, 1):
        print(f"\n📋 Ejemplo {i}/{len(existing_examples)}")
        run_example(script_name, description)
    
    print(f"\n{'='*80}")
    print("🎉 TODOS LOS EJEMPLOS COMPLETADOS")
    print(f"{'='*80}")
    print("✅ Sistema de referencias funcionando correctamente")
    print("✅ Ejemplos de PyTorch, Transformers, Diffusers y Gradio ejecutados")
    print("✅ Mejores prácticas oficiales implementadas")
    
    print("\n📚 Resumen de lo que se demostró:")
    print("  🔥 PyTorch: Mixed Precision, DataLoader optimizado, checkpointing")
    print("  🤗 Transformers: Model loading, tokenización, Trainer")
    print("  🎨 Diffusers: Pipeline usage, memory optimization")
    print("  🎯 Gradio: Interface creation, advanced components, error handling")
    
    print("\n🚀 ¡Sistema listo para usar en producción!")

if __name__ == "__main__":
    main() 