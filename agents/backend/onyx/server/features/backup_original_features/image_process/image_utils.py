# Adapted from original image-processo/image-utils.py

# Aquí irían funciones utilitarias para procesamiento de imágenes
# Por ejemplo, decodificación base64, validación de formato, etc.

def is_supported_format(filename: str, allowed_formats=None) -> bool:
    if allowed_formats is None:
        allowed_formats = ["jpg", "jpeg", "png", "bmp", "gif"]
    ext = filename.lower().split('.')[-1]
    return ext in allowed_formats

def decode_base64_image(image_base64: str) -> bytes:
    import base64
    return base64.b64decode(image_base64) 