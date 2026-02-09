"""
Batch Face Swap Mejorado - Versión Refactorizada
=================================================
Versión refactorizada usando módulos refactorizados de face_swap_modules.

Usa los módulos refactorizados para resultados de máxima calidad.
"""

import cv2
import numpy as np
from pathlib import Path
import random
import sys
import io
import logging

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Importar módulos refactorizados
try:
    from face_swap_modules import FaceSwapPipeline
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    print("⚠ face_swap_modules no disponible. Ejecutar desde directorio scripts/")

# Intentar importar DeepSeek enhancer
try:
    from deepseek_face_swap_enhancer import DeepSeekFaceSwapEnhancer
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False
    print("⚠ DeepSeek enhancer no disponible. Instala requests: pip install requests")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ImageSourceManager:
    """Gestor de fuentes de imágenes."""
    
    @staticmethod
    def get_bunny_faces() -> list[Path]:
        """Obtiene todas las caras de bunny disponibles."""
        bunny_dirs = [
            "instagram_downloads/bunnyrose.me",
            "instagram_downloads/bunnyrose.uwu",
            "instagram_downloads/bunnyy.rose_"
        ]
        
        all_faces = []
        for dir_path in bunny_dirs:
            dir_obj = Path(dir_path)
            if dir_obj.exists():
                jpg_files = list(dir_obj.glob("*.jpg"))
                all_faces.extend(jpg_files)
        
        return all_faces
    
    @staticmethod
    def get_69caylin_images() -> list[Path]:
        """Obtiene todas las imágenes de 69caylin."""
        caylin_dir = Path("instagram_downloads/69caylin")
        if not caylin_dir.exists():
            return []
        
        return list(caylin_dir.glob("*.jpg"))


class ResultEnhancer:
    """Mejorador de resultados de face swap."""
    
    def __init__(self, deepseek_enhancer=None, use_deepseek=False):
        """
        Inicializar mejorador.
        
        Args:
            deepseek_enhancer: Instancia de DeepSeekFaceSwapEnhancer (opcional)
            use_deepseek: Si True, usa DeepSeek para mejorar
        """
        self.deepseek_enhancer = deepseek_enhancer
        self.use_deepseek = use_deepseek and DEEPSEEK_AVAILABLE and deepseek_enhancer
    
    def enhance(
        self,
        result_img: np.ndarray,
        source_img: np.ndarray,
        target_img: np.ndarray
    ) -> np.ndarray:
        """
        Mejorar resultado del face swap.
        
        Args:
            result_img: Imagen resultante
            source_img: Imagen fuente
            target_img: Imagen objetivo
        
        Returns:
            Imagen mejorada
        """
        # Aplicar DeepSeek si está disponible
        if self.use_deepseek:
            try:
                result_img, _ = self.deepseek_enhancer.enhance_face_swap(
                    result_img, source_img, target_img, use_analysis=False
                )
            except Exception as e:
                logger.warning(f"Error en mejora DeepSeek: {e}")
        
        # Mejoras estándar usando módulos refactorizados
        # (La mayoría de mejoras ya están en PostProcessor y AdvancedEnhancements)
        # Aquí solo aplicamos mejoras específicas adicionales
        
        # Reducción de ruido final
        result_img = cv2.bilateralFilter(result_img, 3, 20, 20)
        
        return result_img
    
    def apply_deepseek_advanced(
        self,
        result_img: np.ndarray,
        source_img: np.ndarray,
        target_img: np.ndarray
    ) -> np.ndarray:
        """
        Aplicar mejoras avanzadas de DeepSeek.
        
        Args:
            result_img: Imagen resultante
            source_img: Imagen fuente
            target_img: Imagen objetivo
        
        Returns:
            Imagen mejorada
        """
        if not self.use_deepseek:
            return result_img
        
        try:
            # Aplicar mejoras específicas de DeepSeek
            result_img = self.deepseek_enhancer._improve_color_matching(result_img, target_img)
            result_img = self.deepseek_enhancer._improve_lighting(result_img, target_img)
            result_img = self.deepseek_enhancer._enhance_skin_texture(result_img, target_img)
            result_img = self.deepseek_enhancer._enhance_facial_features(result_img)
            result_img = self.deepseek_enhancer._apply_auto_enhancements(
                result_img, source_img, target_img
            )
        except Exception as e:
            logger.warning(f"Error en mejoras avanzadas DeepSeek: {e}")
        
        return result_img


class BatchFaceSwapProcessor:
    """Procesador de face swap por lotes."""
    
    def __init__(
        self,
        pipeline: FaceSwapPipeline,
        enhancer: ResultEnhancer,
        output_dir: Path
    ):
        """
        Inicializar procesador.
        
        Args:
            pipeline: Pipeline de face swap
            enhancer: Mejorador de resultados
            output_dir: Directorio de salida
        """
        self.pipeline = pipeline
        self.enhancer = enhancer
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
    
    def process_batch(
        self,
        source_images: list[Path],
        target_images: list[Path]
    ) -> dict:
        """
        Procesar lote de imágenes.
        
        Args:
            source_images: Lista de imágenes fuente
            target_images: Lista de imágenes objetivo
        
        Returns:
            Diccionario con estadísticas
        """
        successful = 0
        failed = 0
        
        logger.info(f"🔄 Procesando {len(target_images)} imágenes...")
        
        for idx, target_img_path in enumerate(target_images, 1):
            try:
                # Seleccionar imagen fuente aleatoria
                source_img_path = random.choice(source_images)
                
                # Cargar imágenes
                source_img = cv2.imread(str(source_img_path))
                target_img = cv2.imread(str(target_img_path))
                
                if source_img is None or target_img is None:
                    logger.warning(f"Error cargando imágenes: {target_img_path.name}")
                    failed += 1
                    continue
                
                # Hacer face swap usando pipeline refactorizado
                result = self.pipeline.process(source_img, target_img)
                
                if result is None:
                    logger.warning(f"Face swap falló: {target_img_path.name}")
                    failed += 1
                    continue
                
                # Mejorar resultado
                result = self.enhancer.enhance(result, source_img, target_img)
                
                # Aplicar mejoras avanzadas de DeepSeek
                result = self.enhancer.apply_deepseek_advanced(
                    result, source_img, target_img
                )
                
                # Guardar resultado
                output_filename = f"bunny_face_on_{target_img_path.stem}.jpg"
                output_path = self.output_dir / output_filename
                
                cv2.imwrite(
                    str(output_path),
                    result,
                    [cv2.IMWRITE_JPEG_QUALITY, 100, cv2.IMWRITE_JPEG_OPTIMIZE, 1]
                )
                
                successful += 1
                
                if idx % 50 == 0:
                    logger.info(f"[{idx}/{len(target_images)}] Procesadas...")
                    
            except Exception as e:
                logger.error(f"Error procesando {target_img_path.name}: {e}")
                failed += 1
                continue
        
        return {
            'successful': successful,
            'failed': failed,
            'total': len(target_images)
        }


def main():
    """Función principal."""
    print("=" * 70)
    print("BATCH FACE SWAP MEJORADO REFACTORIZADO: BUNNY -> 69CAYLIN")
    print("Usando módulos refactorizados de face_swap_modules")
    print("=" * 70)
    
    if not MODULES_AVAILABLE:
        print("❌ Error: face_swap_modules no está disponible")
        print("   Asegúrate de estar en el directorio scripts/")
        return
    
    # Inicializar DeepSeek enhancer si está disponible
    deepseek_enhancer = None
    use_deepseek = DEEPSEEK_AVAILABLE
    
    if DEEPSEEK_AVAILABLE:
        try:
            print("\n🤖 Inicializando DeepSeek AI Enhancer...")
            deepseek_enhancer = DeepSeekFaceSwapEnhancer(
                api_key="sk-051c14b97c2a4526a0c3c98be47f17cb"
            )
            print("✓ DeepSeek enhancer inicializado correctamente")
        except Exception as e:
            print(f"⚠ Error inicializando DeepSeek: {e}")
            print("   Continuando sin mejoras de DeepSeek")
            use_deepseek = False
    else:
        print("\n⚠ DeepSeek no disponible. Instala: pip install requests")
    
    # Obtener imágenes
    print("\n📦 Cargando imágenes...")
    source_manager = ImageSourceManager()
    bunny_faces = source_manager.get_bunny_faces()
    caylin_images = source_manager.get_69caylin_images()
    
    if len(bunny_faces) == 0:
        print("❌ Error: No se encontraron imágenes de bunny")
        return
    
    if len(caylin_images) == 0:
        print("❌ Error: No se encontraron imágenes de 69caylin")
        return
    
    print(f"✓ Encontradas {len(bunny_faces)} caras de bunny")
    print(f"✓ Encontradas {len(caylin_images)} imágenes de 69caylin")
    
    # Crear carpeta de salida
    output_dir = Path("face_swap_results_bunny_to_69caylin")
    print(f"\n📁 Los resultados se guardarán en: {output_dir}")
    
    # Inicializar pipeline refactorizado
    print("\n🔧 Inicializando pipeline refactorizado...")
    pipeline = FaceSwapPipeline(
        use_advanced_enhancements=True,
        quality_mode='ultra'  # Máxima calidad
    )
    print("✓ Pipeline inicializado")
    
    # Inicializar mejorador
    enhancer = ResultEnhancer(
        deepseek_enhancer=deepseek_enhancer,
        use_deepseek=use_deepseek
    )
    
    # Inicializar procesador
    processor = BatchFaceSwapProcessor(
        pipeline=pipeline,
        enhancer=enhancer,
        output_dir=output_dir
    )
    
    # Procesar
    if use_deepseek:
        print("\n✨ Usando mejoras de DeepSeek AI")
    print("-" * 70)
    
    stats = processor.process_batch(bunny_faces, caylin_images)
    
    # Resumen
    print("\n" + "=" * 70)
    print("✅ PROCESO COMPLETADO")
    print("=" * 70)
    print(f"✓ Imágenes procesadas exitosamente: {stats['successful']}")
    print(f"⚠ Imágenes con errores: {stats['failed']}")
    print(f"📁 Resultados guardados en: {output_dir.absolute()}")
    
    if use_deepseek:
        print("\n✨ Mejoras aplicadas:")
        print("   - Módulos refactorizados (FaceSwapPipeline)")
        print("   - DeepSeek AI Enhancement")
        print("   - Post-procesamiento avanzado")
        print("   - Modo ultra calidad")
    else:
        print("\n💡 Los resultados usan módulos refactorizados para mejor calidad")


if __name__ == "__main__":
    main()







