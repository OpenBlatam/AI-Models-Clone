import msgspec
from uuid6 import uuid7
from datetime import datetime
from typing import List
import numpy as np
try:
    import pandas as pd
except ImportError:
    pd = None

class Ad(msgspec.Struct, frozen=True, slots=True):
    __match_args__ = ("id", "title", "content", "metadata")
    id: str = msgspec.field(default_factory=lambda: str(uuid7()))
    title: str
    content: str
    metadata: dict = msgspec.field(default_factory=dict)
    created_at: str = msgspec.field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = msgspec.field(default_factory=lambda: datetime.utcnow().isoformat())
    created_by: str | None = None
    updated_by: str | None = None
    source: str | None = None
    version: int = 1
    trace_id: str | None = None
    is_deleted: bool = False

    def as_tuple(self) -> tuple:
        return (self.id, self.title, self.content, self.metadata)

    def to_training_example(self) -> dict:
        return {"input": self.title, "output": self.content, "metadata": self.metadata}

    @classmethod
    def from_training_example(cls, example: dict) -> "Ad":
        return cls(title=example["input"], content=example["output"], metadata=example.get("metadata", {}))

    @staticmethod
    def batch_encode(ads: List["Ad"]) -> bytes:
        return msgspec.json.encode(ads)

    @staticmethod
    def batch_decode(data: bytes) -> List["Ad"]:
        return msgspec.json.decode(data, type=List[Ad])

    @staticmethod
    def batch_deduplicate(ads: List["Ad"]) -> List["Ad"]:
        seen = set()
        out = []
        for ad in ads:
            if ad.id not in seen:
                seen.add(ad.id)
                out.append(ad)
        return out

    @staticmethod
    def batch_to_training_examples(ads: List["Ad"]) -> List[dict]:
        return [{"input": ad.title, "output": ad.content, "metadata": ad.metadata} for ad in ads]

    @staticmethod
    def batch_from_training_examples(examples: List[dict]) -> List["Ad"]:
        return [Ad.from_training_example(ex) for ex in examples]

    @staticmethod
    def batch_as_tuples(ads: List["Ad"]) -> List[tuple]:
        return [ad.as_tuple() for ad in ads]

    @staticmethod
    def batch_to_dicts(ads: List["Ad"]) -> List[dict]:
        return [ad.__dict__ for ad in ads]

    @staticmethod
    def batch_from_dicts(dicts: List[dict]) -> List["Ad"]:
        return [Ad(**d) for d in dicts]

    @staticmethod
    def batch_to_numpy(ads: List["Ad"]):
        arr = np.array([(d["id"], d["title"], d["content"], d["metadata"]) for d in Ad.batch_to_dicts(ads)], dtype=object)
        return arr

    @staticmethod
    def batch_to_pandas(ads: List["Ad"]):
        if pd is None:
            raise ImportError("pandas is not installed")
        return pd.DataFrame(Ad.batch_to_dicts(ads)) 