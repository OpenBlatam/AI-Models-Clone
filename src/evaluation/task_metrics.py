from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch


def _to_numpy(x: torch.Tensor | np.ndarray | Sequence) -> np.ndarray:
    if isinstance(x, torch.Tensor):
        return x.detach().cpu().numpy()
    if isinstance(x, np.ndarray):
        return x
    return np.asarray(x)


def classification_metrics(
    logits_or_probs: torch.Tensor | np.ndarray,
    targets: torch.Tensor | np.ndarray,
    average: str = "macro",
) -> Dict[str, float]:
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

    probs_np = _to_numpy(logits_or_probs)
    if probs_np.ndim == 2:
        preds_np = probs_np.argmax(axis=-1)
    else:
        preds_np = (probs_np > 0.5).astype(int)
    y_true = _to_numpy(targets)
    return {
        "accuracy": float(accuracy_score(y_true, preds_np)),
        "precision": float(precision_score(y_true, preds_np, average=average, zero_division=0)),
        "recall": float(recall_score(y_true, preds_np, average=average, zero_division=0)),
        "f1": float(f1_score(y_true, preds_np, average=average, zero_division=0)),
    }


def multilabel_metrics(
    probs: torch.Tensor | np.ndarray,
    targets: torch.Tensor | np.ndarray,
    threshold: float = 0.5,
) -> Dict[str, float]:
    from sklearn.metrics import average_precision_score, roc_auc_score, f1_score

    y_score = _to_numpy(probs)
    y_true = _to_numpy(targets).astype(int)
    y_pred = (y_score >= threshold).astype(int)

    metrics: Dict[str, float] = {}
    # Handle cases where metric can be undefined
    try:
        metrics["roc_auc_micro"] = float(roc_auc_score(y_true, y_score, average="micro"))
        metrics["roc_auc_macro"] = float(roc_auc_score(y_true, y_score, average="macro"))
    except Exception:
        metrics["roc_auc_micro"] = float("nan")
        metrics["roc_auc_macro"] = float("nan")
    try:
        metrics["ap_micro"] = float(average_precision_score(y_true, y_score, average="micro"))
        metrics["ap_macro"] = float(average_precision_score(y_true, y_score, average="macro"))
    except Exception:
        metrics["ap_micro"] = float("nan")
        metrics["ap_macro"] = float("nan")
    metrics["f1_micro"] = float(f1_score(y_true, y_pred, average="micro", zero_division=0))
    metrics["f1_macro"] = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    return metrics


def regression_metrics(
    preds: torch.Tensor | np.ndarray,
    targets: torch.Tensor | np.ndarray,
) -> Dict[str, float]:
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    y_pred = _to_numpy(preds)
    y_true = _to_numpy(targets)
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mse": float(mean_squared_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
    }


def segmentation_metrics(
    pred_mask: torch.Tensor | np.ndarray,
    true_mask: torch.Tensor | np.ndarray,
    eps: float = 1e-6,
) -> Dict[str, float]:
    y_pred = _to_numpy(pred_mask).astype(bool)
    y_true = _to_numpy(true_mask).astype(bool)
    inter = np.logical_and(y_pred, y_true).sum()
    union = np.logical_or(y_pred, y_true).sum()
    dice = (2 * inter + eps) / (y_pred.sum() + y_true.sum() + eps)
    iou = (inter + eps) / (union + eps)
    return {"dice": float(dice), "iou": float(iou)}


def nlp_generation_metrics(
    references: List[List[str]],
    hypotheses: List[str],
) -> Dict[str, float]:
    metrics: Dict[str, float] = {}
    # BLEU via sacrebleu
    try:
        import sacrebleu  # type: ignore

        bleu = sacrebleu.corpus_bleu(hypotheses, list(zip(*references)))  # type: ignore[arg-type]
        metrics["bleu"] = float(bleu.score)
    except Exception:
        metrics["bleu"] = float("nan")

    # ROUGE via rouge-score
    try:
        from rouge_score import rouge_scorer  # type: ignore

        scorer = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)
        r1, rL = [], []
        for hyp, refs in zip(hypotheses, references):
            # use first reference by default for simple scoring
            scores = scorer.score(refs[0], hyp)
            r1.append(scores["rouge1"].fmeasure)
            rL.append(scores["rougeL"].fmeasure)
        metrics["rouge1_f"] = float(np.mean(r1)) if r1 else float("nan")
        metrics["rougeL_f"] = float(np.mean(rL)) if rL else float("nan")
    except Exception:
        metrics["rouge1_f"] = float("nan")
        metrics["rougeL_f"] = float("nan")
    return metrics


__all__ = [
    "classification_metrics",
    "multilabel_metrics",
    "regression_metrics",
    "segmentation_metrics",
    "nlp_generation_metrics",
]



