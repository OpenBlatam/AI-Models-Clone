from __future__ import annotations

import heapq
import os
from dataclasses import dataclass, field
from typing import List, Tuple

import torch
from torch import nn


@dataclass(order=True)
class _HeapItem:
    priority: float
    path: str = field(compare=False)
    original_score: float = field(compare=False)


@dataclass
class CheckpointConfig:
    directory: str
    monitor: str = "val/loss"
    mode: str = "min"  # or "max"
    save_top_k: int = 1
    save_every: int = 1


class CheckpointManager:
    def __init__(self, cfg: CheckpointConfig) -> None:
        self.cfg = cfg
        os.makedirs(self.cfg.directory, exist_ok=True)
        self._heap: List[_HeapItem] = []
        # For 'min': smaller score is better → keep K smallest; maintain heap with worst at root using priority = score (max-heap simulated via sign)
        # We unify by defining priority so that larger priority = worse (root is worst in min-heap):
        # - mode 'min': priority = score (worst is largest); but Python heap is min-heap, so we actually want root to be worst.
        #   We achieve that by storing priority = score and in replacement compare incoming_priority < current_worst? No, see unified rule below.
        # To simplify, we choose: priority = score if mode=='max' else -score. Then root (smallest) corresponds to worst.
        # Proof: mode 'min' → priority=-score. Worst (largest score) has most negative priority → smallest → at root. mode 'max' → priority=score. Worst (smallest score) is smallest → at root.
        self._is_min_mode = self.cfg.mode.lower().startswith("min")

    def _priority(self, score: float) -> float:
        return (-score) if self._is_min_mode else score

    def _maybe_insert(self, score: float, path: str) -> bool:
        item = _HeapItem(priority=self._priority(score), path=path, original_score=score)
        if self.cfg.save_top_k <= 0:
            return False
        if len(self._heap) < self.cfg.save_top_k:
            heapq.heappush(self._heap, item)
            return True
        # Root is worst. Replace if incoming is better → incoming.priority > root.priority
        if item.priority > self._heap[0].priority:
            popped = heapq.heapreplace(self._heap, item)
            try:
                os.remove(popped.path)
            except Exception:
                pass
            return True
        return False

    def maybe_save(self, epoch: int, metrics: dict, model: nn.Module, optimizer: torch.optim.Optimizer) -> str | None:
        if (epoch % self.cfg.save_every) != 0:
            return None
        key = self.cfg.monitor
        if key not in metrics:
            return None
        score = float(metrics[key])
        filename = f"epoch{epoch:04d}_{key.replace('/', '-')}_{score:.4f}.pt"
        path = os.path.join(self.cfg.directory, filename)
        obj = {"model": model.state_dict(), "optimizer": optimizer.state_dict(), "epoch": epoch, "metrics": metrics}
        torch.save(obj, path)
        kept = self._maybe_insert(score, path)
        if kept:
            return path
        # If not kept (not in top-k), remove the saved file immediately
        try:
            os.remove(path)
        except Exception:
            pass
        return None


