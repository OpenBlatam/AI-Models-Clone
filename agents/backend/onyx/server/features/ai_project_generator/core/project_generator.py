"""
Project Generator - Generador principal de proyectos
=====================================================

Genera automáticamente la estructura completa de un proyecto de IA
basándose en una descripción del usuario.
"""

import asyncio
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

from .backend_generator import BackendGenerator
from .frontend_generator import FrontendGenerator
from .keyword_extractor import KeywordExtractor
from .constants import DEFAULT_PROJECT_VERSION, DEFAULT_AUTHOR, MAX_PROJECT_NAME_LENGTH
from .shared_utils import get_logger, sanitize_filename
from .json_utils import json_dumps_pretty
from ..utils.test_generator import TestGenerator
from ..utils.cicd_generator import CICDGenerator
from ..utils.export_generator import ExportGenerator
from ..utils.validator import ProjectValidator
from ..utils.deployment_generator import DeploymentGenerator
from ..utils.cache_manager import CacheManager

logger = get_logger(__name__)


class ProjectGenerator:
    """Generador principal de proyectos de IA"""

    def __init__(
        self,
        base_output_dir: str = "generated_projects",
        backend_framework: str = "fastapi",
        frontend_framework: str = "react",
    ):
        """
        Inicializa el generador de proyectos.

        Args:
            base_output_dir: Directorio base donde se generarán los proyectos
            backend_framework: Framework de backend a usar (fastapi, flask, django)
            frontend_framework: Framework de frontend a usar (react, vue, nextjs)
        """
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        self.backend_framework = backend_framework
        self.frontend_framework = frontend_framework
        self.backend_generator = BackendGenerator()
        self.frontend_generator = FrontendGenerator()
        self.keyword_extractor = KeywordExtractor()
        self.test_generator = TestGenerator()
        self.cicd_generator = CICDGenerator()
        self.export_generator = ExportGenerator()
        self.validator = ProjectValidator()
        self.deployment_generator = DeploymentGenerator()
        self.cache_manager = CacheManager()

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """
        Sanitiza el nombre del proyecto para usarlo como nombre de carpeta (función pura).
        
        Args:
            name: Nombre a sanitizar
            
        Returns:
            Nombre sanitizado
            
        Raises:
            ValueError: Si el nombre está vacío
        """
        if not name:
            raise ValueError("name cannot be empty")
        return sanitize_filename(name, MAX_PROJECT_NAME_LENGTH)

    def _extract_keywords(self, description: str) -> Dict[str, Any]:
        """Extrae palabras clave y características del proyecto de la descripción"""
        return self.keyword_extractor.extract(description)

    async def generate_project(
        self,
        description: str,
        project_name: Optional[str] = None,
        author: str = DEFAULT_AUTHOR,
        version: str = DEFAULT_PROJECT_VERSION,
    ) -> Dict[str, Any]:
        """
        Genera un proyecto completo basándose en la descripción.

        Args:
            description: Descripción del proyecto de IA
            project_name: Nombre del proyecto (si no se proporciona, se genera)
            author: Autor del proyecto
            version: Versión del proyecto

        Returns:
            Diccionario con información del proyecto generado
            
        Raises:
            ValueError: Si los parámetros son inválidos
        """
        if not description:
            raise ValueError("description cannot be empty")
        
        if not author:
            raise ValueError("author cannot be empty")
        
        if not version:
            raise ValueError("version cannot be empty")
        
        try:
            logger.info(f"Iniciando generación de proyecto: {description[:100]}...")

            # Generar nombre del proyecto si no se proporciona
            if not project_name:
                # Intentar extraer un nombre de la descripción
                try:
                    project_name = self._sanitize_name(description.split('.')[0][:30])
                except ValueError:
                    project_name = f"ai_project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Sanitizar nombre
            project_name = self._sanitize_name(project_name)

            # Configuración para cache
            config = {
                "backend_framework": self.backend_framework,
                "frontend_framework": self.frontend_framework,
            }

            # Verificar cache
            cached_project = await self.cache_manager.get_cached_project(description, config)
            if cached_project:
                logger.info("Proyecto encontrado en cache, retornando versión cacheada")
                # Registrar cache hit (si hay metrics_collector disponible)
                return cached_project

            # Extraer keywords
            keywords = self._extract_keywords(description)

            # Crear directorio del proyecto
            project_dir = self.base_output_dir / project_name
            if project_dir.exists():
                # Agregar timestamp si ya existe
                project_dir = self.base_output_dir / f"{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            project_dir.mkdir(parents=True, exist_ok=True)

            # Generar estructura del proyecto
            project_info = {
                "name": project_name,
                "description": description,
                "author": author,
                "version": version,
                "keywords": keywords,
                "created_at": datetime.now().isoformat(),
                "project_dir": str(project_dir),
                "backend_dir": str(project_dir / "backend"),
                "frontend_dir": str(project_dir / "frontend"),
            }

            # Generar backend
            logger.info("Generando backend...")
            backend_info = await self.backend_generator.generate(
                project_dir=project_dir / "backend",
                description=description,
                keywords=keywords,
                project_info=project_info,
            )
            project_info["backend"] = backend_info

            # Generar frontend
            logger.info("Generando frontend...")
            frontend_info = await self.frontend_generator.generate(
                project_dir=project_dir / "frontend",
                description=description,
                keywords=keywords,
                project_info=project_info,
            )
            project_info["frontend"] = frontend_info

            # Generar tests
            logger.info("Generando tests...")
            await self.test_generator.generate_backend_tests(
                project_dir / "backend",
                keywords,
                project_info,
            )
            await self.test_generator.generate_frontend_tests(
                project_dir / "frontend",
                keywords,
                project_info,
            )

            # Generar CI/CD
            logger.info("Generando CI/CD pipelines...")
            await self.cicd_generator.generate_github_actions(
                project_dir,
                keywords,
                project_info,
            )

            # Generar archivos de configuración del proyecto
            await self._generate_project_files(project_dir, project_info)

            # Validar proyecto generado
            logger.info("Validando proyecto generado...")
            validation_result = await self.validator.validate_project(
                project_dir, project_info
            )
            project_info["validation"] = validation_result

            if not validation_result["valid"]:
                logger.warning(
                    f"Proyecto generado con {validation_result['error_count']} errores"
                )

            # Exportar metadata
            logger.info("Generando metadata...")
            metadata = await self.export_generator.export_metadata(
                project_dir, project_info
            )
            project_info["metadata"] = metadata

            # Guardar en cache
            await self.cache_manager.cache_project(description, config, project_info)

            logger.info(f"Proyecto generado exitosamente en: {project_dir}")

            return project_info

        except Exception as e:
            logger.error(f"Error generando proyecto: {e}", exc_info=True)
            raise

    async def _generate_project_files(
        self, project_dir: Path, project_info: Dict[str, Any]
    ):
        """Genera archivos de configuración del proyecto"""
        
        # README.md principal
        readme_content = f"""# {project_info['name'].replace('_', ' ').title()}

{project_info['description']}

## 🚀 Inicio Rápido

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port {project_info.get('backend', {}).get('port', 8000)}
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 📁 Estructura del Proyecto

```
{project_info['name']}/
├── backend/          # Backend API
├── frontend/         # Frontend Application
└── README.md         # Este archivo
```

## 🛠️ Tecnologías

- **Backend**: {project_info.get('backend', {}).get('framework', 'FastAPI')}
- **Frontend**: {project_info.get('frontend', {}).get('framework', 'React')}

## 📝 Características

{chr(10).join(f"- {feature}" for feature in project_info['keywords'].get('features', []))}

## 👤 Autor

{project_info['author']}

## 📄 Licencia

MIT
"""
        (project_dir / "README.md").write_text(readme_content, encoding="utf-8")

        # .gitignore
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local

# Build
dist/
build/
*.egg-info/

# Logs
*.log
logs/
"""
        (project_dir / ".gitignore").write_text(gitignore_content, encoding="utf-8")

        # docker-compose.yml
        docker_compose = f"""version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "{project_info.get('backend', {}).get('port', 8000)}:8000"
    environment:
      - ENV=development
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "{project_info.get('frontend', {}).get('port', 3000)}:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:{project_info.get('backend', {}).get('port', 8000)}
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm start
"""
        (project_dir / "docker-compose.yml").write_text(docker_compose, encoding="utf-8")

        # project_info.json
        (project_dir / "project_info.json").write_text(
            json_dumps_pretty(project_info, indent=2, ensure_ascii=False), encoding="utf-8"
        )

