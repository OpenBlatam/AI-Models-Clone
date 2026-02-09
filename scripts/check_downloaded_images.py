import os
import sys
from PIL import Image
from pathlib import Path

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

download_dir = Path("instagram_downloads/bunnyrose.me")
files = [f for f in os.listdir(download_dir) if f.endswith('.jpg')]

print(f"Total de imagenes descargadas: {len(files)}")

sizes = []
for f in files:
    try:
        img = Image.open(download_dir / f)
        sizes.append(img.size)
    except Exception as e:
        print(f"Error al leer {f}: {e}")

print(f"Resoluciones unicas encontradas: {set(sizes)}")
print(f"Resolucion maxima: {max(sizes, key=lambda x: x[0]*x[1]) if sizes else 'N/A'}")

total_size = sum(os.path.getsize(download_dir / f) for f in files)
print(f"Tamaño total: {total_size / (1024*1024):.2f} MB")








