import io
from typing import Optional
from PIL import Image, ImageOps, ImageFile

Image.MAX_IMAGE_PIXELS = 50_000_000
ImageFile.LOAD_TRUNCATED_IMAGES = False

try:
    from turbojpeg import TurboJPEG  # type: ignore
    _JPEG = TurboJPEG()
except Exception:  # pragma: no cover
    _JPEG = None


def decode_bytes_fast(data: bytes, mime: Optional[str]) -> Image.Image:
    """Decode image bytes efficiently using TurboJPEG for JPEG and Pillow fallback.
    Always returns RGBA and applies EXIF orientation.
    """
    if _JPEG and mime == "image/jpeg":
        arr = _JPEG.decode(data)  # numpy ndarray in BGR
        im = Image.fromarray(arr[..., ::-1], "RGB")
    else:
        im = Image.open(io.BytesIO(data))
        im.load()
    return ImageOps.exif_transpose(im).convert("RGBA")


