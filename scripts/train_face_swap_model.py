"""
Entrenar Modelo de Face Swap de Alta Calidad
=============================================
Entrena el modelo con todas las imágenes disponibles para mejores resultados
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from face_swap_simple import train_simple_model
from pathlib import Path

def main():
    print("=" * 70)
    print("ENTRENAMIENTO DE MODELO FACE SWAP DE ALTA CALIDAD")
    print("=" * 70)
    
    # Combinar todas las imágenes de bunny para entrenar
    bunny_dirs = [
        "instagram_downloads/bunnyrose.me",
        "instagram_downloads/bunnyrose.uwu",
        "instagram_downloads/bunnyy.rose_"
    ]
    
    # Crear directorio temporal con todas las imágenes
    import shutil
    temp_train_dir = Path("temp_training_images")
    temp_train_dir.mkdir(exist_ok=True)
    
    print("\n📦 Preparando dataset de entrenamiento...")
    total_images = 0
    
    for dir_path in bunny_dirs:
        dir_obj = Path(dir_path)
        if dir_obj.exists():
            jpg_files = list(dir_obj.glob("*.jpg"))
            for img_file in jpg_files:
                # Copiar imagen al directorio temporal
                dest = temp_train_dir / img_file.name
                if not dest.exists():
                    shutil.copy2(img_file, dest)
                    total_images += 1
    
    print(f"✓ Total de imágenes para entrenar: {total_images}")
    
    if total_images < 10:
        print("❌ Error: Se necesitan al menos 10 imágenes para entrenar")
        return
    
    # Entrenar modelo
    print("\n🎓 Iniciando entrenamiento...")
    print("   Esto puede tomar varios minutos...")
    
    train_simple_model(
        image_dir=str(temp_train_dir),
        epochs=80,  # Más épocas para mejor calidad
        batch_size=4,
        lr=0.00015,  # Learning rate optimizado
        save_path="face_swap_simple_model.pth"
    )
    
    print("\n✅ Entrenamiento completado!")
    print("💾 Modelo guardado en: face_swap_simple_model.pth")
    
    # Limpiar directorio temporal
    print("\n🧹 Limpiando archivos temporales...")
    shutil.rmtree(temp_train_dir)
    print("✓ Limpieza completada")

if __name__ == "__main__":
    main()








