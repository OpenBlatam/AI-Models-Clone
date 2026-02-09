from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import torch
from PIL import Image


@dataclass
class IOConfig:
    image_path: str = os.getenv("IMAGE", "")
    json_path: str = os.getenv("JSON", "")
    out_dir: str = os.getenv("OUT", "outputs/safe_io")


def safe_load_image(path: str) -> Image.Image:
    if not path:
        raise FileNotFoundError("Ruta de imagen vacía")
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"Imagen no encontrada: {path}")
    with Image.open(p) as img:
        return img.convert("RGB")


def safe_load_json(path: str) -> Dict[str, Any]:
    if not path:
        raise FileNotFoundError("Ruta JSON vacía")
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"JSON no encontrado: {path}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido: {e}") from e


def safe_infer_dummy(image: Image.Image, meta: Dict[str, Any]) -> Dict[str, Any]:
    # Simula una inferencia segura que valida entradas
    if image.width < 16 or image.height < 16:
        raise ValueError("Imagen demasiado pequeña")
    score = float(min(image.width, image.height)) / max(image.width, image.height)
    return {"ok": True, "score": score, "meta": meta}


def main() -> None:
    cfg = IOConfig()
    out = Path(cfg.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    try:
        img = safe_load_image(cfg.image_path)
        meta = safe_load_json(cfg.json_path) if cfg.json_path else {"info": "no meta"}
        res = safe_infer_dummy(img, meta)
        (out / "result.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        (out / "error.log").write_text(str(e), encoding="utf-8")
        raise


if __name__ == "__main__":
    main()



