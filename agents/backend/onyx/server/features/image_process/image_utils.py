"""Robust image utilities: base64 guard, secure decode, MIME validation, resize, color."""

from typing import Optional, Dict
import math
import base64
import io
from PIL import Image, ImageOps, ImageFile
from .config import config
import numpy as np

Image.MAX_IMAGE_PIXELS = 50_000_000  # mitigate decompression bombs
ImageFile.LOAD_TRUNCATED_IMAGES = False



def b64_to_bytes(b64: str, *, max_bytes: int) -> bytes:
    """Decode base64 with size limit and validation.

    Performs a preflight size check to avoid decoding extremely large inputs.
    """
    # Preflight: worst-case decoded length is roughly 3/4 of base64 length
    # Account for padding and add a small slack (+4)
    approx_decoded = (len(b64) * 3) // 4
    if approx_decoded > max_bytes + 4:
        raise ValueError(f"image_exceeds_max_bytes_preflight:~{approx_decoded}>{max_bytes}")
    raw = base64.b64decode(b64, validate=True)
    if len(raw) > max_bytes:
        raise ValueError(f"image_exceeds_max_bytes:{len(raw)}>{max_bytes}")
    return raw


def decode_image_bytes(data: bytes) -> Image.Image:
    """Decode bytes to PIL Image safely and normalize orientation."""
    im = Image.open(io.BytesIO(data))
    im.load()
    im = ImageOps.exif_transpose(im)
    return im.convert("RGBA")


def validate_mime_declared_vs_actual(im: Image.Image, declared_mime: str) -> None:
    """Ensure declared MIME is supported and matches decoded image format."""
    actual = (Image.MIME.get(im.format) or "").lower()
    if im.format and im.format.upper() == "SVG":
        raise ValueError("unsupported_format:SVG")
    if declared_mime not in config.ALLOWED_MIME or (actual and declared_mime != actual):
        raise ValueError(f"mime_mismatch:{declared_mime}!={actual or 'unknown'}")


def resize_max_side(im: Image.Image, max_side: int) -> Image.Image:
    w, h = im.size
    s = max(w, h)
    if s <= max_side:
        return im
    r = max_side / s
    return im.resize((int(w * r), int(h * r)), Image.LANCZOS)


def dominant_color_hex(im: Image.Image) -> str:
    """Fast dominant color (hex). Uses getcolors then NumPy fallback."""
    colors = im.convert("RGB").getcolors(maxcolors=256_000)
    if colors:
        _, (r, g, b) = max(colors, key=lambda c: c[0])
        return f"#{r:02x}{g:02x}{b:02x}"
    arr = np.asarray(im.convert("RGB"))
    cols, cnt = np.unique(arr.reshape(-1, 3), axis=0, return_counts=True)
    r, g, b = cols[cnt.argmax()].tolist()
    return f"#{r:02x}{g:02x}{b:02x}"
