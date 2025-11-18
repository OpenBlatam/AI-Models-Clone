"""
Import Export - Sistema de Importación y Exportación Avanzado
==============================================================

Sistema avanzado para importar y exportar proyectos.
"""

import logging
import json
import shutil
import tarfile
import zipfile
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class AdvancedImportExport:
    """Sistema avanzado de importación y exportación"""

    def __init__(self):
        """Inicializa el sistema"""
        pass

    def export_project_advanced(
        self,
        project_path: Path,
        output_path: Path,
        format: str = "zip",
        include_dependencies: bool = True,
        include_tests: bool = True,
        include_docs: bool = True,
        compress: bool = True,
    ) -> Dict[str, Any]:
        """
        Exporta un proyecto de forma avanzada.

        Args:
            project_path: Ruta del proyecto
            output_path: Ruta de salida
            format: Formato (zip, tar, tar.gz, tar.bz2)
            include_dependencies: Incluir dependencias
            include_tests: Incluir tests
            include_docs: Incluir documentación
            compress: Comprimir

        Returns:
            Información de la exportación
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "zip":
            return self._export_zip(
                project_path, output_path,
                include_dependencies, include_tests, include_docs
            )
        elif format.startswith("tar"):
            return self._export_tar(
                project_path, output_path, format,
                include_dependencies, include_tests, include_docs, compress
            )
        else:
            raise ValueError(f"Formato no soportado: {format}")

    def _export_zip(
        self,
        project_path: Path,
        output_path: Path,
        include_dependencies: bool,
        include_tests: bool,
        include_docs: bool,
    ) -> Dict[str, Any]:
        """Exporta a ZIP"""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in project_path.rglob("*"):
                if file_path.is_file():
                    # Filtrar según opciones
                    if not include_tests and "test" in str(file_path):
                        continue
                    if not include_docs and file_path.suffix in [".md", ".txt"]:
                        continue

                    arcname = file_path.relative_to(project_path)
                    zipf.write(file_path, arcname)

        return {
            "format": "zip",
            "output_path": str(output_path),
            "size_bytes": output_path.stat().st_size,
            "created_at": datetime.now().isoformat(),
        }

    def _export_tar(
        self,
        project_path: Path,
        output_path: Path,
        format: str,
        include_dependencies: bool,
        include_tests: bool,
        include_docs: bool,
        compress: bool,
    ) -> Dict[str, Any]:
        """Exporta a TAR"""
        mode = "w"
        if format == "tar.gz" or (format == "tar" and compress):
            mode = "w:gz"
        elif format == "tar.bz2":
            mode = "w:bz2"
        elif format == "tar.xz":
            mode = "w:xz"

        with tarfile.open(output_path, mode) as tar:
            for file_path in project_path.rglob("*"):
                if file_path.is_file():
                    # Filtrar según opciones
                    if not include_tests and "test" in str(file_path):
                        continue
                    if not include_docs and file_path.suffix in [".md", ".txt"]:
                        continue

                    arcname = file_path.relative_to(project_path)
                    tar.add(file_path, arcname=arcname)

        return {
            "format": format,
            "output_path": str(output_path),
            "size_bytes": output_path.stat().st_size,
            "created_at": datetime.now().isoformat(),
        }

    def import_project(
        self,
        archive_path: Path,
        extract_to: Path,
        validate: bool = True,
    ) -> Dict[str, Any]:
        """
        Importa un proyecto desde un archivo.

        Args:
            archive_path: Ruta del archivo
            extract_to: Directorio donde extraer
            validate: Validar después de importar

        Returns:
            Información de la importación
        """
        extract_to = Path(extract_to)
        extract_to.mkdir(parents=True, exist_ok=True)

        archive_path = Path(archive_path)

        if archive_path.suffix == ".zip":
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                zipf.extractall(extract_to)
        elif archive_path.suffix in [".tar", ".gz", ".bz2", ".xz"]:
            mode = "r"
            if archive_path.suffix in [".gz", ".tar.gz"]:
                mode = "r:gz"
            elif archive_path.suffix == ".bz2":
                mode = "r:bz2"
            elif archive_path.suffix == ".xz":
                mode = "r:xz"

            with tarfile.open(archive_path, mode) as tar:
                tar.extractall(extract_to)
        else:
            raise ValueError(f"Formato de archivo no soportado: {archive_path.suffix}")

        result = {
            "imported_at": datetime.now().isoformat(),
            "extracted_to": str(extract_to),
            "files_count": len(list(extract_to.rglob("*"))),
        }

        if validate:
            # Validación básica
            has_backend = (extract_to / "backend").exists()
            has_frontend = (extract_to / "frontend").exists()
            result["validation"] = {
                "valid": has_backend or has_frontend,
                "has_backend": has_backend,
                "has_frontend": has_frontend,
            }

        logger.info(f"Proyecto importado desde {archive_path} a {extract_to}")
        return result


