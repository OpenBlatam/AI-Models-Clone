"""
Template Manager - Gestor de Templates
=======================================

Gestiona templates personalizados para proyectos.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class TemplateManager:
    """Gestor de templates personalizados"""

    def __init__(self, templates_dir: Path = None):
        """
        Inicializa el gestor de templates.

        Args:
            templates_dir: Directorio donde se almacenan los templates
        """
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent / "templates"
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    async def save_template(
        self,
        template_name: str,
        template_config: Dict[str, Any],
        description: str = "",
    ) -> Dict[str, Any]:
        """
        Guarda un template personalizado.

        Args:
            template_name: Nombre del template
            template_config: Configuración del template
            description: Descripción del template

        Returns:
            Información del template guardado
        """
        try:
            template_file = self.templates_dir / f"{template_name}.json"
            
            from datetime import datetime
            template_data = {
                "name": template_name,
                "description": description,
                "config": template_config,
                "created_at": datetime.now().isoformat(),
            }

            template_file.write_text(
                json.dumps(template_data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

            logger.info(f"Template guardado: {template_name}")
            return {"success": True, "template_name": template_name}

        except Exception as e:
            logger.error(f"Error guardando template: {e}")
            raise

    async def load_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Carga un template.

        Args:
            template_name: Nombre del template

        Returns:
            Configuración del template o None
        """
        try:
            template_file = self.templates_dir / f"{template_name}.json"
            if not template_file.exists():
                return None

            return json.loads(template_file.read_text(encoding="utf-8"))

        except Exception as e:
            logger.error(f"Error cargando template: {e}")
            return None

    async def list_templates(self) -> List[Dict[str, Any]]:
        """
        Lista todos los templates disponibles.

        Returns:
            Lista de templates
        """
        templates = []
        for template_file in self.templates_dir.glob("*.json"):
            try:
                template_data = json.loads(template_file.read_text(encoding="utf-8"))
                templates.append({
                    "name": template_data.get("name", template_file.stem),
                    "description": template_data.get("description", ""),
                })
            except Exception:
                continue

        return templates

    async def delete_template(self, template_name: str) -> bool:
        """
        Elimina un template.

        Args:
            template_name: Nombre del template

        Returns:
            True si se eliminó exitosamente
        """
        try:
            template_file = self.templates_dir / f"{template_name}.json"
            if template_file.exists():
                template_file.unlink()
                logger.info(f"Template eliminado: {template_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error eliminando template: {e}")
            return False

