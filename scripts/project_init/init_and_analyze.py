from __future__ import annotations

import argparse
import json
import os
from typing import Dict

from scripts.project_init.problem_definition import make_template, ProblemDefinition
from scripts.project_init.dataset_analysis import (
    detect_type,
    analyze_csv,
    analyze_jsonl,
    analyze_image_dir,
    AnalysisConfig,
)


def main() -> None:
    ap = argparse.ArgumentParser(description="Initialize problem definition and run dataset analysis")
    ap.add_argument("--name", required=True)
    ap.add_argument("--data-dir", default="datasets")
    ap.add_argument("--analysis-path", required=True)
    ap.add_argument("--out-problem", default="config/problem_definition.json")
    ap.add_argument("--out-analysis", default="experiments/dataset_analysis.json")
    ap.add_argument("--max-rows", type=int, default=200000)
    ap.add_argument("--sample-rows", type=int, default=5000)
    args = ap.parse_args()

    # Problem definition
    pd = make_template(args.name, args.data_dir)
    os.makedirs(os.path.dirname(args.out_problem) or ".", exist_ok=True)
    with open(args.out_problem, "w", encoding="utf-8") as f:
        json.dump(pd.model_dump(), f, indent=2, ensure_ascii=False)

    # Dataset analysis
    os.makedirs(os.path.dirname(args.out_analysis) or ".", exist_ok=True)
    cfg = AnalysisConfig(path=args.analysis_path, max_rows=args.max_rows, sample_rows=args.sample_rows)
    dtype = detect_type(args.analysis_path)
    if dtype == "csv":
        report: Dict = analyze_csv(args.analysis_path, cfg)
    elif dtype == "jsonl":
        report = analyze_jsonl(args.analysis_path, cfg)
    elif dtype == "image_dir":
        report = analyze_image_dir(args.analysis_path)
    elif dtype == "directory":
        report = {"type": "directory", "entries": len(os.listdir(args.analysis_path))}
    else:
        report = {"type": "unknown", "path": args.analysis_path}
    with open(args.out_analysis, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print({
        "problem_definition": args.out_problem,
        "dataset_analysis": args.out_analysis,
    })


if __name__ == "__main__":
    main()



