import time
import base64
from io import BytesIO
from PIL import Image

from agents.backend.onyx.server.features.image_process.models import ImageSummaryRequest
from agents.backend.onyx.server.features.image_process.service import ImageProcessService


def bench_summary(size: int = 1024, max_side: int = 512) -> None:
    im = Image.new("RGB", (size, size), (64, 128, 32))
    buf = BytesIO()
    im.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    req = ImageSummaryRequest(image_url=None, image_base64=b64, summary_type="simple")

    svc = ImageProcessService()
    t0 = time.perf_counter()
    resp = svc.summarize(req)
    dt = (time.perf_counter() - t0) * 1000
    print({"summary_ms": round(dt, 2), "success": resp.success})


if __name__ == "__main__":
    bench_summary()


