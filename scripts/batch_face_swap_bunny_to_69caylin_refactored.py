"""
Batch Face Swap: Bunny caras a 69caylin cuerpos - Versión Refactorizada
========================================================================
Versión refactorizada usando módulos separados.
"""

import cv2
import numpy as np
from pathlib import Path
import random
import sys
import io
import logging

# Importar módulos refactorizados
try:
    from simple_face_swap import SimpleFaceSwapPipeline
    SIMPLE_FACE_SWAP_AVAILABLE = True
except ImportError:
    try:
        from face_swap_simple import SimpleFaceSwapPipeline
        SIMPLE_FACE_SWAP_AVAILABLE = True
    except ImportError:
        SIMPLE_FACE_SWAP_AVAILABLE = False
        print("⚠ simple_face_swap no disponible")

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ImageSourceManager:
    """Gestiona las fuentes de imágenes para face swap."""
    
    @staticmethod
    def get_bunny_faces(base_dir: str = "instagram_downloads") -> list:
        """
        Obtiene todas las caras de bunny disponibles.
        
        Args:
            base_dir: Directorio base de descargas
        
        Returns:
            Lista de rutas a imágenes de bunny
        """
        bunny_dirs = [
            f"{base_dir}/bunnyrose.me",
            f"{base_dir}/bunnyrose.uwu",
            f"{base_dir}/bunnyy.rose_"
        ]
        
        all_faces = []
        for dir_path in bunny_dirs:
            dir_obj = Path(dir_path)
            if dir_obj.exists():
                jpg_files = list(dir_obj.glob("*.jpg"))
                all_faces.extend(jpg_files)
        
        return all_faces
    
    @staticmethod
    def get_69caylin_images(base_dir: str = "instagram_downloads") -> list:
        """
        Obtiene todas las imágenes de 69caylin.
        
        Args:
            base_dir: Directorio base de descargas
        
        Returns:
            Lista de rutas a imágenes de 69caylin
        """
        caylin_dir = Path(base_dir) / "69caylin"
        if not caylin_dir.exists():
            return []
        
        return list(caylin_dir.glob("*.jpg"))


class BatchFaceSwapProcessor:
    """Procesa batch de face swaps."""
    
    def __init__(
        self,
        pipeline: SimpleFaceSwapPipeline,
        output_dir: Path,
        random_selection: bool = True
    ):
        """
        Inicializar procesador batch.
        
        Args:
            pipeline: Pipeline de face swap
            output_dir: Directorio de salida
            random_selection: Si True, selecciona caras aleatoriamente
        """
        self.pipeline = pipeline
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        self.random_selection = random_selection
    
    def process_batch(
        self,
        source_images: list,
        target_images: list
    ) -> dict:
        """
        Procesa un batch de face swaps.
        
        Args:
            source_images: Lista de imágenes fuente (bunny)
            target_images: Lista de imágenes objetivo (69caylin)
        
        Returns:
            Diccionario con estadísticas
        """
        if not source_images:
            logger.error("No se encontraron imágenes fuente")
            return {'successful': 0, 'failed': 0, 'total': 0}
        
        if not target_images:
            logger.error("No se encontraron imágenes objetivo")
            return {'successful': 0, 'failed': 0, 'total': 0}
        
        logger.info(f"Procesando {len(target_images)} imágenes...")
        
        successful = 0
        failed = 0
        
        for idx, target_img_path in enumerate(target_images, 1):
            try:
                # Seleccionar imagen fuente
                if self.random_selection:
                    source_img_path = random.choice(source_images)
                else:
                    source_img_path = source_images[idx % len(source_images)]
                
                # Cargar imágenes
                source_img = cv2.imread(str(source_img_path))
                target_img = cv2.imread(str(target_img_path))
                
                if source_img is None or target_img is None:
                    logger.warning(f"[{idx}/{len(target_images)}] Error cargando imágenes: {target_img_path.name}")
                    failed += 1
                    continue
                
                # Realizar face swap
                result = self.pipeline.swap_faces(source_img, target_img)
                
                if result is None:
                    logger.warning(f"[{idx}/{len(target_images)}] Error en face swap: {target_img_path.name}")
                    failed += 1
                    continue
                
                # Guardar resultado
                output_path = self.output_dir / f"bunny_to_69caylin_{target_img_path.stem}.jpg"
                cv2.imwrite(str(output_path), result)
                
                successful += 1
                logger.info(f"[{idx}/{len(target_images)}] ✓ {target_img_path.name} -> {output_path.name}")
                
            except Exception as e:
                logger.error(f"[{idx}/{len(target_images)}] Error procesando {target_img_path.name}: {e}")
                failed += 1
        
        logger.info("=" * 70)
        logger.info(f"Procesamiento completado:")
        logger.info(f"  ✓ Exitosos: {successful}")
        logger.info(f"  ✗ Fallidos: {failed}")
        logger.info(f"  📁 Total: {len(target_images)}")
        
        return {
            'successful': successful,
            'failed': failed,
            'total': len(target_images)
        }


def main():
    """Función principal."""
    logger.info("=" * 70)
    logger.info("BATCH FACE SWAP: BUNNY CARAS -> 69CAYLIN CUERPOS (Refactorizado)")
    logger.info("=" * 70)
    
    if not SIMPLE_FACE_SWAP_AVAILABLE:
        logger.error("❌ Error: Módulo simple_face_swap no disponible")
        logger.error("   Asegúrate de que el módulo esté instalado")
        sys.exit(1)
    
    # Obtener imágenes
    logger.info("\n📦 Cargando imágenes...")
    bunny_faces = ImageSourceManager.get_bunny_faces()
    caylin_images = ImageSourceManager.get_69caylin_images()
    
    if len(bunny_faces) == 0:
        logger.error("❌ Error: No se encontraron imágenes de bunny")
        logger.error("   Asegúrate de haber descargado las imágenes primero")
        return
    
    if len(caylin_images) == 0:
        logger.error("❌ Error: No se encontraron imágenes de 69caylin")
        logger.error("   Asegúrate de haber descargado las imágenes primero")
        return
    
    logger.info(f"✓ Encontradas {len(bunny_faces)} caras de bunny")
    logger.info(f"✓ Encontradas {len(caylin_images)} imágenes de 69caylin")
    
    # Crear carpeta de salida
    output_dir = Path("face_swap_results_bunny_to_69caylin")
    logger.info(f"\n📁 Los resultados se guardarán en: {output_dir}")
    
    # Inicializar pipeline
    logger.info("\n🔧 Inicializando pipeline de face swap...")
    model_path = "face_swap_simple_model.pth"
    pipeline = SimpleFaceSwapPipeline(
        model_path=model_path if Path(model_path).exists() else None
    )
    
    # Crear procesador batch
    processor = BatchFaceSwapProcessor(
        pipeline=pipeline,
        output_dir=output_dir,
        random_selection=True
    )
    
    # Procesar batch
    logger.info(f"\n🔄 Procesando {len(caylin_images)} imágenes...")
    logger.info("-" * 70)
    
    stats = processor.process_batch(bunny_faces, caylin_images)
    
    logger.info("")
    logger.info(f"Estadísticas finales: {stats}")


if __name__ == "__main__":
    main()






