from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import yaml


class TaskType(str, Enum):
    classification = "classification"
    regression = "regression"
    seq2seq = "seq2seq"
    language_modeling = "language_modeling"
    diffusion = "diffusion"


@dataclass
class ProblemDefinition:
    project_name: str
    task: TaskType
    input_features: List[str]
    target_name: Optional[str]
    primary_metrics: List[str]
    constraints: Dict[str, str]
    notes: Optional[str] = None

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["task"] = self.task.value
        return data

    def save(self, out_dir: str = "project_meta", file_stem: str = "problem_definition") -> None:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        data = self.to_dict()
        (out / f"{file_stem}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / f"{file_stem}.yaml").write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def example() -> None:
    name = os.getenv("PROJECT_NAME", "my_project")
    task = TaskType(os.getenv("TASK", "classification"))
    features = [s.strip() for s in os.getenv("FEATURES", "f1,f2,f3").split(",") if s.strip()]
    target = os.getenv("TARGET", "label")
    metrics = [s.strip() for s in os.getenv("METRICS", "accuracy,f1").split(",") if s.strip()]
    constraints = {"latency_ms": os.getenv("LATENCY_MS", "<50"), "memory_mb": os.getenv("MEMORY_MB", "<1024")}
    notes = os.getenv("NOTES", "Initial problem definition.")

    pd = ProblemDefinition(
        project_name=name,
        task=task,
        input_features=features,
        target_name=target,
        primary_metrics=metrics,
        constraints=constraints,
        notes=notes,
    )
    pd.save()


if __name__ == "__main__":
    example()

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class DatasetSpec(BaseModel):
    name: str = Field(..., description="Dataset nickname, e.g., 'imdb', 'cifar10', 'custom_v1'")
    modality: str = Field(..., description="tabular|text|image|audio|multimodal")
    train_path: str = Field(..., description="Path to training data")
    val_path: Optional[str] = Field(None, description="Path to validation data (optional)")
    test_path: Optional[str] = Field(None, description="Path to test data (optional)")
    target_column: Optional[str] = Field(None, description="Supervised target column/key (if applicable)")

    @field_validator("modality")
    @classmethod
    def _modality_valid(cls, v: str) -> str:
        allowed = {"tabular", "text", "image", "audio", "multimodal"}
        v_lower = (v or "").lower()
        if v_lower not in allowed:
            raise ValueError(f"modality must be one of {sorted(allowed)}")
        return v_lower


class ProblemDefinition(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    objectives: List[str] = Field(default_factory=list)
    success_metrics: Dict[str, str] = Field(default_factory=dict, description="metric_name -> definition or target")
    stakeholders: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    dataset: DatasetSpec
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z")

    @field_validator("objectives", "stakeholders")
    @classmethod
    def _lists_not_empty(cls, v: List[str]) -> List[str]:
        return [item.strip() for item in v if isinstance(item, str) and item.strip()]

    @field_validator("success_metrics")
    @classmethod
    def _metrics_trim(cls, v: Dict[str, str]) -> Dict[str, str]:
        clean = {}
        for k, val in (v or {}).items():
            k2 = (k or "").strip()
            v2 = (val or "").strip()
            if k2 and v2:
                clean[k2] = v2
        return clean

    def save_json(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_json(path: str) -> "ProblemDefinition":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return ProblemDefinition(**data)


def make_template(name: str, data_dir: str) -> ProblemDefinition:
    return ProblemDefinition(
        name=name,
        description="Short problem statement. What are we solving and why?",
        objectives=["Define baseline", "Ship MVP", "Reach target metric"],
        success_metrics={
            "accuracy": ">= 0.90 on validation",
            "latency_ms_p50": "<= 50ms per sample",
        },
        stakeholders=["product", "ml", "infra"],
        constraints=["P99 latency <= 200ms", "Max GPU mem 12GB"],
        assumptions=["Data distribution stable for 6 months"],
        risks=["Label noise", "Domain shift"],
        dataset=DatasetSpec(
            name=f"{name}_dataset",
            modality="tabular",
            train_path=os.path.join(data_dir, "train"),
            val_path=os.path.join(data_dir, "val"),
            test_path=os.path.join(data_dir, "test"),
            target_column="label",
        ),
    )


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Problem definition init/validate")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Create a problem definition template")
    p_init.add_argument("--name", required=True)
    p_init.add_argument("--data-dir", default="datasets")
    p_init.add_argument("--out", default="config/problem_definition.json")

    p_val = sub.add_parser("validate", help="Validate an existing problem definition JSON")
    p_val.add_argument("--file", required=True)

    return p.parse_args()


def main() -> None:
    args = _parse_args()
    if args.cmd == "init":
        pd = make_template(args.name, args.data_dir)
        pd.save_json(args.out)
        print(f"wrote {args.out}")
    elif args.cmd == "validate":
        pd = ProblemDefinition.load_json(args.file)
        # round-trip to ensure validity
        print(json.dumps(pd.model_dump(), indent=2))


if __name__ == "__main__":
    main()


