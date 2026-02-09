"""
Entrenar Modelo de Face Swap - Versión Refactorizada
=====================================================
Versión refactorizada usando módulos existentes.
"""

import sys
import io
import shutil
import logging
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Importar módulos refactorizados
try:
    from simple_face_swap import SimpleFaceSwapTrainer
    TRAINER_AVAILABLE = True
except ImportError:
    try:
        from face_swap_simple import train_simple_model
        TRAINER_AVAILABLE = True
        SimpleFaceSwapTrainer = None
    except ImportError:
        TRAINER_AVAILABLE = False
        train_simple_model = None

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrainingDataManager:
    """Gestiona la preparación de datos de entrenamiento."""
    
    @staticmethod
    def collect_training_images(source_dirs: list, output_dir: Path) -> int:
        """
        Recolecta imágenes de múltiples directorios.
        
        Args:
            source_dirs: Lista de directorios fuente
            output_dir: Directorio de salida para imágenes temporales
        
        Returns:
            Número total de imágenes recolectadas
        """
        output_dir.mkdir(exist_ok=True)
        total_images = 0
        
        for dir_path in source_dirs:
            dir_obj = Path(dir_path)
            if dir_obj.exists():
                jpg_files = list(dir_obj.glob("*.jpg"))
                for img_file in jpg_files:
                    dest = output_dir / img_file.name
                    if not dest.exists():
                        shutil.copy2(img_file, dest)
                        total_images += 1
        
        return total_images
    
    @staticmethod
    def cleanup_temp_dir(temp_dir: Path):
        """Limpia directorio temporal."""
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            logger.info("✓ Limpieza completada")


class ModelTrainer:
    """Gestiona el entrenamiento del modelo."""
    
    def __init__(self):
        """Inicializar entrenador."""
        self.trainer = None
        if TRAINER_AVAILABLE and SimpleFaceSwapTrainer:
            try:
                self.trainer = SimpleFaceSwapTrainer()
            except Exception as e:
                logger.warning(f"Error inicializando trainer: {e}")
    
    def train(
        self,
        image_dir: str,
        epochs: int = 80,
        batch_size: int = 4,
        lr: float = 0.00015,
        save_path: str = "face_swap_simple_model.pth"
    ) -> bool:
        """
        Entrena el modelo.
        
        Args:
            image_dir: Directorio con imágenes de entrenamiento
            epochs: Número de épocas
            batch_size: Tamaño de batch
            lr: Learning rate
            save_path: Ruta para guardar el modelo
        
        Returns:
            True si el entrenamiento fue exitoso
        """
        if not TRAINER_AVAILABLE:
            logger.error("❌ Trainer no disponible")
            return False
        
        try:
            if self.trainer:
                # Usar trainer refactorizado
                self.trainer.train(
                    image_dir=image_dir,
                    epochs=epochs,
                    batch_size=batch_size,
                    lr=lr,
                    save_path=save_path
                )
            else:
                # Usar función original
                train_simple_model(
                    image_dir=image_dir,
                    epochs=epochs,
                    batch_size=batch_size,
                    lr=lr,
                    save_path=save_path
                )
            return True
        except Exception as e:
            logger.error(f"Error durante entrenamiento: {e}")
            return False


def main():
    """Función principal."""
    logger.info("=" * 70)
    logger.info("ENTRENAMIENTO DE MODELO FACE SWAP (Refactorizado)")
    logger.info("=" * 70)
    
    if not TRAINER_AVAILABLE:
        logger.error("❌ Error: Módulos de entrenamiento no disponibles")
        logger.error("   Asegúrate de que simple_face_swap esté instalado")
        return
    
    # Directorios fuente
    bunny_dirs = [
        "instagram_downloads/bunnyrose.me",
        "instagram_downloads/bunnyrose.uwu",
        "instagram_downloads/bunnyy.rose_"
    ]
    
    # Crear directorio temporal
    temp_train_dir = Path("temp_training_images")
    
    # Recolectar imágenes
    logger.info("\n📦 Preparando dataset de entrenamiento...")
    data_manager = TrainingDataManager()
    total_images = data_manager.collect_training_images(bunny_dirs, temp_train_dir)
    
    logger.info(f"✓ Total de imágenes para entrenar: {total_images}")
    
    if total_images < 10:
        logger.error("❌ Error: Se necesitan al menos 10 imágenes para entrenar")
        data_manager.cleanup_temp_dir(temp_train_dir)
        return
    
    # Entrenar modelo
    logger.info("\n🎓 Iniciando entrenamiento...")
    logger.info("   Esto puede tomar varios minutos...")
    
    trainer = ModelTrainer()
    success = trainer.train(
        image_dir=str(temp_train_dir),
        epochs=80,
        batch_size=4,
        lr=0.00015,
        save_path="face_swap_simple_model.pth"
    )
    
    if success:
        logger.info("\n✅ Entrenamiento completado!")
        logger.info("💾 Modelo guardado en: face_swap_simple_model.pth")
    else:
        logger.error("\n❌ Error durante el entrenamiento")
    
    # Limpiar directorio temporal
    logger.info("\n🧹 Limpiando archivos temporales...")
    data_manager.cleanup_temp_dir(temp_train_dir)


if __name__ == "__main__":
    main()






