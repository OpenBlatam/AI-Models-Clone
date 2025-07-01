"""
🚀 ULTRA VIDEO AI SYSTEM - MODULAR ARCHITECTURE
===============================================

Sistema modular ultra-optimizado para procesamiento de video AI.

Módulos disponibles:
- core: Modelos y clases principales
- api: APIs y servicios web
- optimization: Optimizaciones de rendimiento
- production: Configuración de producción
- benchmarking: Testing y benchmarking
- config: Configuración del sistema
- utils: Utilidades y helpers
- docs: Documentación
- deployment: Deployment y containerización
- monitoring: Monitoreo y métricas
"""

__version__ = "2.0.0"
__title__ = "Ultra Video AI System"
__description__ = "Sistema modular ultra-optimizado para procesamiento de video AI"

# Importaciones principales
from pathlib import Path

# Metadata
SYSTEM_PATH = Path(__file__).parent
MODULES = [
    "core",
    "api", 
    "optimization",
    "production",
    "benchmarking",
    "config",
    "utils",
    "docs",
    "deployment",
    "monitoring"
]

def get_system_info():
    """Obtener información del sistema."""
    return {
        "title": __title__,
        "version": __version__,
        "description": __description__,
        "modules": MODULES,
        "path": str(SYSTEM_PATH)
    }

def list_modules():
    """Listar módulos disponibles."""
    available_modules = []
    for module_name in MODULES:
        module_path = SYSTEM_PATH / module_name
        if module_path.exists() and module_path.is_dir():
            # Contar archivos Python en el módulo
            python_files = len([f for f in module_path.glob("*.py") if f.name != "__init__.py"])
            available_modules.append({
                "name": module_name,
                "path": str(module_path),
                "files": python_files,
                "has_init": (module_path / "__init__.py").exists()
            })
    return available_modules

def get_module_structure():
    """Obtener estructura completa del sistema."""
    structure = {}
    for module_info in list_modules():
        module_name = module_info["name"]
        module_path = Path(module_info["path"])
        
        files = []
        for py_file in module_path.glob("*.py"):
            if py_file.name != "__init__.py":
                files.append(py_file.name)
        
        structure[module_name] = {
            "description": _get_module_description(module_name),
            "files": files,
            "file_count": len(files)
        }
    
    return structure

def _get_module_description(module_name):
    """Obtener descripción de un módulo."""
    descriptions = {
        "core": "Modelos y clases principales del sistema de Video AI",
        "api": "APIs, servicios web y endpoints",
        "optimization": "Optimizaciones de rendimiento y algoritmos avanzados",
        "production": "Configuración y archivos específicos de producción",
        "benchmarking": "Sistemas de testing, benchmarking y validación",
        "config": "Archivos de configuración del sistema",
        "utils": "Utilidades, helpers y funciones auxiliares",
        "docs": "Documentación del sistema",
        "deployment": "Archivos de deployment y containerización",
        "monitoring": "Monitoreo, métricas y observabilidad"
    }
    return descriptions.get(module_name, "Módulo del sistema")

def verify_system_integrity():
    """Verificar integridad del sistema modular."""
    issues = []
    
    # Verificar que todos los módulos esperados existen
    for module_name in MODULES:
        module_path = SYSTEM_PATH / module_name
        if not module_path.exists():
            issues.append(f"Módulo faltante: {module_name}")
        elif not (module_path / "__init__.py").exists():
            issues.append(f"__init__.py faltante en: {module_name}")
    
    # Verificar backup
    backup_path = SYSTEM_PATH / "backup_original"
    if not backup_path.exists():
        issues.append("Directorio de backup no encontrado")
    
    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "modules_found": len(list_modules()),
        "expected_modules": len(MODULES)
    }

# Importaciones de módulos principales (con manejo de errores)
try:
    from . import core
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo core: {e}")

try:
    from . import api
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo api: {e}")

try:
    from . import optimization
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo optimization: {e}")

try:
    from . import production
except ImportError as e:
    import logging
    logging.warning(f"No se pudo importar módulo production: {e}")

# Configuración de logging para el sistema
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"🚀 {__title__} v{__version__} - Sistema modular inicializado")

# Verificar integridad al importar
integrity_check = verify_system_integrity()
if not integrity_check["is_valid"]:
    logger.warning(f"⚠️ Problemas de integridad encontrados: {integrity_check['issues']}")
else:
    logger.info(f"✅ Sistema modular verificado - {integrity_check['modules_found']} módulos disponibles") 