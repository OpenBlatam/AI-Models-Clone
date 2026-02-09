"""
Face Swap Simple - Versión Refactorizada
=========================================
Versión refactorizada usando módulos separados.

Versión simplificada que solo usa OpenCV y PyTorch.
No requiere dlib ni face_recognition.
"""

import cv2
import argparse
import sys

from simple_face_swap import SimpleFaceSwapPipeline, train_simple_model


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Simple Face Swap Model")
    parser.add_argument("--mode", choices=["train", "swap"], required=True)
    parser.add_argument("--image-dir", type=str, help="Directorio con imágenes")
    parser.add_argument("--source", type=str, help="Imagen fuente")
    parser.add_argument("--target", type=str, help="Imagen destino")
    parser.add_argument("--output", type=str, default="output.jpg")
    parser.add_argument("--model", type=str, default="face_swap_simple_model.pth")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=4)
    
    args = parser.parse_args()
    
    if args.mode == "train":
        if not args.image_dir:
            print("❌ Error: --image-dir es requerido")
            sys.exit(1)
        train_simple_model(
            args.image_dir,
            args.epochs,
            args.batch_size,
            save_path=args.model
        )
    
    elif args.mode == "swap":
        if not args.source or not args.target:
            print("❌ Error: --source y --target son requeridos")
            sys.exit(1)
        
        pipeline = SimpleFaceSwapPipeline(model_path=args.model)
        source_img = cv2.imread(args.source)
        target_img = cv2.imread(args.target)
        
        if source_img is None or target_img is None:
            print("❌ Error: No se pudieron cargar las imágenes")
            sys.exit(1)
        
        result = pipeline.swap_faces(source_img, target_img)
        cv2.imwrite(args.output, result)
        print(f"✅ Resultado guardado en {args.output}")


if __name__ == "__main__":
    main()






