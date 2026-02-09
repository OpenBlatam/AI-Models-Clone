# Descargador de Imágenes de Instagram

Script para descargar todas las imágenes de un perfil de Instagram.

## Instalación

1. Instala las dependencias:
```bash
pip install -r requirements_instagram_downloader.txt
```

O directamente:
```bash
pip install instaloader
```

## Uso

### Uso básico (usuario por defecto: mialay18)
```bash
python download_instagram_images.py
```

### Especificar un usuario diferente
```bash
python download_instagram_images.py nombre_usuario
```

### Especificar directorio de salida
```bash
python download_instagram_images.py mialay18 --output-dir ./mis_imagenes
```

### Ejemplos completos
```bash
# Descargar imágenes de mialay18
python download_instagram_images.py mialay18

# Descargar a un directorio específico
python download_instagram_images.py mialay18 -o ./descargas_instagram

# Descargar de otro usuario
python download_instagram_images.py otro_usuario
```

## Características

- ✅ Descarga todas las imágenes del perfil
- ✅ No descarga videos (solo imágenes)
- ✅ Crea directorio automáticamente
- ✅ Muestra progreso en tiempo real
- ✅ Manejo de errores robusto
- ✅ Soporte para argumentos de línea de comandos

## Notas Importantes

⚠️ **Términos de Servicio**: Asegúrate de respetar los términos de servicio de Instagram y los derechos de autor del contenido.

⚠️ **Perfiles Privados**: Los perfiles privados pueden requerir autenticación. Si encuentras este problema, puedes modificar el script para agregar inicio de sesión.

⚠️ **Límites de Rate**: Instagram puede limitar las solicitudes si descargas demasiado rápido. El script incluye manejo de errores para esto.

## Estructura de Archivos Descargados

Las imágenes se guardarán en el directorio especificado (o `instagram_username` por defecto) con la siguiente estructura:

```
instagram_mialay18/
├── 2024-01-15_12-30-45_UTC.jpg
├── 2024-01-14_10-20-30_UTC.jpg
└── ...
```

## Solución de Problemas

### Error: "instaloader no está instalado"
```bash
pip install instaloader
```

### Error: "El perfil no existe"
Verifica que el nombre de usuario sea correcto y que el perfil sea público.

### Error de conexión
- Verifica tu conexión a internet
- Intenta nuevamente más tarde (Instagram puede tener límites de rate)

### Perfil privado
Si el perfil es privado, necesitarás modificar el script para agregar autenticación:
```python
loader.login('tu_usuario', 'tu_contraseña')
```

## Licencia

Este script es para uso educativo y personal. Respeta los derechos de autor y los términos de servicio de Instagram.








