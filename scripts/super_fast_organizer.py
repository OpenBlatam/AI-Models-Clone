#!/usr/bin/env python3
import os
import sys
import shutil
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class SuperFastOrganizer:
    def __init__(self):
        self.start_time = time.time()
        self.organized_files = 0
        self.total_improvements = 0
    
    def organize_codebase_fast(self) -> Dict[str, Any]:
        """Organiza el código de forma súper rápida"""
        print("🚀 SUPER FAST ORGANIZER")
        print("=" * 50)
        
        # Crear estructura de directorios optimizada
        directories = [
            'core/',
            'api/',
            'services/',
            'models/',
            'utils/',
            'config/',
            'tests/',
            'docs/',
            'scripts/',
            'assets/',
            'data/',
            'cache/',
            'logs/',
            'temp/',
            'backup/'
        ]
        
        # Crear directorios rápidamente
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        # Organizar archivos por tipo
        python_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        # Organización rápida por categorías
        organized_count = 0
        improvements = []
        
        for file_path in python_files[:100]:  # Procesar rápidamente
            try:
                # Determinar categoría del archivo
                category = self.categorize_file_fast(file_path)
                
                # Mover archivo a categoría apropiada
                if category:
                    new_path = self.move_file_to_category(file_path, category)
                    if new_path != file_path:
                        organized_count += 1
                        improvements.append(f"Moved {file_path} to {category}")
                
            except Exception as e:
                continue
        
        # Crear archivos de configuración rápidos
        self.create_fast_config_files()
        
        # Crear estructura de imports optimizada
        self.create_optimized_imports()
        
        # Calcular tiempo total
        execution_time = time.time() - self.start_time
        
        return {
            "files_processed": len(python_files),
            "files_organized": organized_count,
            "improvements_applied": len(improvements),
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }
    
    def categorize_file_fast(self, file_path: str) -> Optional[str]:
        """Categoriza archivo rápidamente"""
        filename = os.path.basename(file_path)
        content = ""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()[:1000]  # Solo leer primeros 1000 chars
        except:
            return None
        
        # Categorización rápida por contenido
        if 'class ' in content and 'def ' in content:
            return 'models'
        elif 'def ' in content and 'return' in content:
            return 'utils'
        elif 'import ' in content and 'from ' in content:
            return 'core'
        elif 'api' in filename.lower() or 'endpoint' in filename.lower():
            return 'api'
        elif 'service' in filename.lower() or 'manager' in filename.lower():
            return 'services'
        elif 'test' in filename.lower():
            return 'tests'
        elif 'config' in filename.lower() or 'settings' in filename.lower():
            return 'config'
        elif 'script' in filename.lower():
            return 'scripts'
        else:
            return 'core'
    
    def move_file_to_category(self, file_path: str, category: str) -> str:
        """Mueve archivo a categoría"""
        filename = os.path.basename(file_path)
        new_path = os.path.join(category, filename)
        
        # Solo mover si no existe
        if not os.path.exists(new_path):
            try:
                shutil.move(file_path, new_path)
                return new_path
            except:
                return file_path
        
        return file_path
    
    def create_fast_config_files(self):
        """Crea archivos de configuración rápidos"""
        configs = {
            'config/settings.py': '# Configuración rápida\nDEBUG = True\nENV = "development"',
            'config/database.py': '# Configuración de base de datos\nDB_URL = "sqlite:///app.db"',
            'config/api.py': '# Configuración de API\nAPI_VERSION = "v1"\nRATE_LIMIT = 100',
            'requirements.txt': 'fastapi\nuvicorn\nsqlalchemy\npytest\nblack\nflake8',
            'README.md': '# Proyecto Organizado\n\nCódigo optimizado y organizado.',
            '.gitignore': '*.pyc\n__pycache__\n.env\n*.log\n.DS_Store',
            'Makefile': 'install:\n\tpip install -r requirements.txt\n\nrun:\n\tpython main.py\n\ntest:\n\tpytest'
        }
        
        for file_path, content in configs.items():
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except:
                continue
    
    def create_optimized_imports(self):
        """Crea imports optimizados"""
        imports = {
            'core/__init__.py': '# Core imports\nfrom .base import *\nfrom .exceptions import *',
            'api/__init__.py': '# API imports\nfrom .routes import *\nfrom .middleware import *',
            'services/__init__.py': '# Services imports\nfrom .base_service import *',
            'models/__init__.py': '# Models imports\nfrom .base_model import *',
            'utils/__init__.py': '# Utils imports\nfrom .helpers import *\nfrom .validators import *',
            'config/__init__.py': '# Config imports\nfrom .settings import *'
        }
        
        for file_path, content in imports.items():
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except:
                continue

def main():
    print("🚀 SUPER FAST ORGANIZER")
    print("=" * 50)
    
    organizer = SuperFastOrganizer()
    results = organizer.organize_codebase_fast()
    
    print(f"\n📊 RESULTADOS SUPER FAST ORGANIZATION:")
    print(f"  📄 Archivos procesados: {results['files_processed']}")
    print(f"  📁 Archivos organizados: {results['files_organized']}")
    print(f"  🔧 Mejoras aplicadas: {results['improvements_applied']}")
    print(f"  ⏱️  Tiempo de ejecución: {results['execution_time']:.2f}s")
    
    # Guardar reporte
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"super_fast_organization_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✅ Super fast organization completado!")
    print(f"📄 Reporte: {report_file}")
    
    if results['improvements_applied'] > 0:
        print(f"🎉 ¡{results['improvements_applied']} mejoras aplicadas!")

if __name__ == "__main__":
    main() 