from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict


def analyze_with_pandas(csv_path: str) -> Dict:
    import pandas as pd  # lazy import

    df = pd.read_csv(csv_path)
    report: Dict = {
        "path": csv_path,
        "shape": [int(df.shape[0]), int(df.shape[1])],
        "memory_mb": float(df.memory_usage(deep=True).sum() / (1024 * 1024)),
        "columns": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_perc": {col: float(df[col].isna().mean()) for col in df.columns},
        "numeric_stats": {},
        "categorical_top": {},
        "head": df.head(5).to_dict(orient="records"),
    }

    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if num_cols:
        desc = df[num_cols].describe().T
        report["numeric_stats"] = {
            col: {
                "mean": float(desc.loc[col, "mean"]),
                "std": float(desc.loc[col, "std"]),
                "min": float(desc.loc[col, "min"]),
                "p25": float(df[col].quantile(0.25)),
                "p50": float(df[col].quantile(0.50)),
                "p75": float(df[col].quantile(0.75)),
                "max": float(desc.loc[col, "max"]),
            }
            for col in num_cols
        }

    cat_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    for col in cat_cols:
        vc = df[col].value_counts(dropna=False).head(10)
        report["categorical_top"][col] = {str(k): int(v) for k, v in vc.items()}

    # Basic target distribution if present
    target = os.getenv("TARGET", "")
    if target and target in df.columns:
        vc = df[target].value_counts(dropna=False)
        report["target_distribution"] = {str(k): int(v) for k, v in vc.items()}

    return report


def analyze_without_pandas(csv_path: str) -> Dict:
    import csv

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return {"path": csv_path, "shape": [0, 0]}
    header = rows[0]
    n_rows = len(rows) - 1
    n_cols = len(header)
    return {"path": csv_path, "shape": [n_rows, n_cols], "columns": header}


def main() -> None:
    data_path = os.getenv("DATA_PATH", "")
    if not data_path:
        raise SystemExit("Set DATA_PATH to a CSV file.")

    try:
        import pandas as _  # noqa: F401
        report = analyze_with_pandas(data_path)
    except Exception:
        report = analyze_without_pandas(data_path)

    out_dir = Path(os.getenv("OUT", "outputs/dataset_analysis"))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["path", "shape", "memory_mb"] if k in report}, indent=2))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import csv
import json
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np


@dataclass
class AnalysisConfig:
    path: str
    max_rows: int = 200000
    sample_rows: int = 5000
    text_columns: Optional[List[str]] = None


def detect_type(path: str) -> str:
    p = path.lower()
    if p.endswith(".csv"):
        return "csv"
    if p.endswith(".jsonl") or p.endswith(".json"):
        return "jsonl" if p.endswith(".jsonl") else "json"
    if any(p.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]):
        return "image_dir" if os.path.isdir(path) else "image_file"
    if os.path.isdir(path):
        return "directory"
    return "unknown"


def analyze_csv(path: str, cfg: AnalysisConfig) -> Dict:
    stats: Dict[str, Dict] = {}
    rows = 0
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        for h in headers:
            stats[h] = {"count": 0, "nan": 0, "min": None, "max": None, "mean": None, "unique": 0}

        values_seen: Dict[str, Counter] = {h: Counter() for h in headers}
        numeric_buffers: Dict[str, List[float]] = {h: [] for h in headers}

        for i, row in enumerate(reader, start=1):
            rows += 1
            for h in headers:
                val = row.get(h)
                if val is None or val == "":
                    stats[h]["nan"] += 1
                else:
                    stats[h]["count"] += 1
                    # collect for uniques and numerics (sampled)
                    if len(values_seen[h]) < cfg.sample_rows:
                        values_seen[h][val] += 1
                    try:
                        if len(numeric_buffers[h]) < cfg.sample_rows:
                            numeric_buffers[h].append(float(val))
                    except Exception:
                        pass
            if i >= cfg.max_rows:
                break

    for h in stats:
        # uniques
        stats[h]["unique"] = len(values_seen[h])
        # numerics
        buf = numeric_buffers[h]
        if buf:
            arr = np.asarray(buf, dtype=np.float64)
            stats[h]["min"] = float(np.min(arr))
            stats[h]["max"] = float(np.max(arr))
            stats[h]["mean"] = float(np.mean(arr))
    return {"type": "csv", "rows_scanned": rows, "columns": stats}


def analyze_jsonl(path: str, cfg: AnalysisConfig) -> Dict:
    rows = 0
    keys_counter: Counter = Counter()
    sample_text: Counter = Counter()
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            try:
                obj = json.loads(line)
            except Exception:
                continue
            rows += 1
            for k in obj.keys():
                keys_counter[k] += 1
            # crude text stats
            for k, v in obj.items():
                if isinstance(v, str) and (cfg.text_columns is None or k in cfg.text_columns):
                    if len(sample_text) < cfg.sample_rows:
                        sample_text.update({"char_len": len(v), "word_len": len(v.split())})
            if i >= cfg.max_rows:
                break
    return {
        "type": "jsonl",
        "rows_scanned": rows,
        "key_histogram": dict(keys_counter),
        "text_sample_stats": dict(sample_text),
    }


def analyze_image_dir(path: str) -> Dict:
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
    count = 0
    sizes: Counter = Counter()
    for p in Path(path).rglob("*"):
        if p.suffix.lower() in exts and p.is_file():
            count += 1
            try:
                from PIL import Image

                with Image.open(p) as im:
                    sizes[(im.width, im.height)] += 1
            except Exception:
                pass
    return {"type": "image_dir", "num_images": count, "size_histogram": {f"{k[0]}x{k[1]}": v for k, v in sizes.items()}}


def main() -> None:
    ap = argparse.ArgumentParser(description="Lightweight dataset analysis")
    ap.add_argument("--path", required=True, help="File or directory path")
    ap.add_argument("--max-rows", type=int, default=200000)
    ap.add_argument("--sample-rows", type=int, default=5000)
    ap.add_argument("--text-columns", type=str, nargs="*")
    ap.add_argument("--out", type=str, default="experiments/dataset_analysis.json")
    args = ap.parse_args()

    cfg = AnalysisConfig(
        path=args.path,
        max_rows=args.max_rows,
        sample_rows=args.sample_rows,
        text_columns=args.text_columns,
    )

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    dtype = detect_type(args.path)
    if dtype == "csv":
        report = analyze_csv(args.path, cfg)
    elif dtype == "jsonl":
        report = analyze_jsonl(args.path, cfg)
    elif dtype == "image_dir":
        report = analyze_image_dir(args.path)
    elif dtype == "directory":
        report = {"type": "directory", "entries": len(os.listdir(args.path))}
    else:
        report = {"type": "unknown", "path": args.path}

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()


