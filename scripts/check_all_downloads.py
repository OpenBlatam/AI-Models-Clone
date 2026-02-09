import os
from pathlib import Path

base_dir = Path("instagram_downloads")
profiles = ["bunnyrose.uwu", "bunnyy.rose_", "bunnyrose.x"]

print("=" * 60)
print("RESUMEN DE DESCARGA DE IMAGENES")
print("=" * 60)

for profile in profiles:
    profile_dir = base_dir / profile
    if profile_dir.exists():
        jpg_files = [f for f in os.listdir(profile_dir) if f.endswith('.jpg')]
        json_files = [f for f in os.listdir(profile_dir) if f.endswith('.json')]
        total_size = sum(os.path.getsize(profile_dir / f) for f in jpg_files) / (1024*1024)
        
        print(f"\n@{profile}:")
        print(f"  - Imagenes JPG: {len(jpg_files)}")
        print(f"  - Archivos JSON: {len(json_files)}")
        print(f"  - Tamaño total: {total_size:.2f} MB")
    else:
        print(f"\n@{profile}:")
        print(f"  - ERROR: No se pudo descargar (perfil no encontrado o bloqueado)")

print("\n" + "=" * 60)








