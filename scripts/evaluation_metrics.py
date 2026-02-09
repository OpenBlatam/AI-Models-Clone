from __future__ import annotations

import math
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import torch
from rouge_score import rouge_scorer
from sacrebleu.metrics import BLEU
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    recall_score,
    r2_score,
    roc_auc_score,
)


# ------------- Classification Metrics -------------
def classification_metrics(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    y_prob: np.ndarray | None = None,
    average: str = "macro",
) -> Dict[str, float]:
    y_true_np = np.asarray(y_true)
    y_pred_np = np.asarray(y_pred)
    metrics: Dict[str, float] = {
        "accuracy": float(accuracy_score(y_true_np, y_pred_np)),
        "precision": float(precision_score(y_true_np, y_pred_np, average=average, zero_division=0)),
        "recall": float(recall_score(y_true_np, y_pred_np, average=average, zero_division=0)),
        "f1": float(f1_score(y_true_np, y_pred_np, average=average, zero_division=0)),
    }
    # ROC-AUC for multi-class requires probability estimates
    if y_prob is not None:
        try:
            metrics["roc_auc_ovr"] = float(roc_auc_score(y_true_np, y_prob, multi_class="ovr"))
        except Exception:
            pass
    return metrics


# ------------- Regression Metrics -------------
def regression_metrics(y_true: Sequence[float], y_pred: Sequence[float]) -> Dict[str, float]:
    y_true_np = np.asarray(y_true, dtype=np.float64)
    y_pred_np = np.asarray(y_pred, dtype=np.float64)
    mse = float(mean_squared_error(y_true_np, y_pred_np))
    rmse = float(math.sqrt(max(mse, 0.0)))
    return {
        "mae": float(mean_absolute_error(y_true_np, y_pred_np)),
        "mse": mse,
        "rmse": rmse,
        "r2": float(r2_score(y_true_np, y_pred_np)),
    }


# ------------- Language Modeling Metrics -------------
def language_modeling_perplexity_from_logits(
    logits: torch.Tensor, labels: torch.Tensor
) -> Dict[str, float]:
    # logits: [batch, seq, vocab], labels: [batch, seq] with -100 ignored
    vocab_dim = logits.size(-1)
    loss_fn = torch.nn.CrossEntropyLoss(ignore_index=-100, reduction="mean")
    loss = loss_fn(logits.view(-1, vocab_dim), labels.view(-1))
    ppl = float(torch.exp(loss).item())
    return {"cross_entropy": float(loss.item()), "perplexity": ppl}


# ------------- Seq2Seq Text Metrics (BLEU, ROUGE) -------------
def seq2seq_text_metrics(preds: List[str], refs: List[str]) -> Dict[str, float]:
    assert len(preds) == len(refs)
    bleu = BLEU(effective_order=True)
    bleu_score = float(bleu.corpus_score(preds, [refs]).score)

    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    r1_f = r2_f = rl_f = 0.0
    for p, r in zip(preds, refs):
        res = scorer.score(r, p)
        r1_f += res["rouge1"].fmeasure
        r2_f += res["rouge2"].fmeasure
        rl_f += res["rougeL"].fmeasure
    n = max(len(preds), 1)
    return {"bleu": bleu_score, "rouge1_f": r1_f / n, "rouge2_f": r2_f / n, "rougeL_f": rl_f / n}


# ------------- Ranking Metrics (MAP@K, MRR, NDCG@K) -------------
def mean_reciprocal_rank(rank_lists: List[List[int]]) -> float:
    # rank_lists: lists of ranks where 1 means first relevant, higher is worse; 0 means no relevant found
    mrr = 0.0
    for ranks in rank_lists:
        rr = 0.0
        for r in ranks:
            if r > 0:
                rr = 1.0 / r
                break
        mrr += rr
    return mrr / max(len(rank_lists), 1)


def average_precision_at_k(relevances: List[int], k: int) -> float:
    # relevances: 1 for relevant, 0 for non-relevant, ordered by predicted rank
    assert k >= 1
    rel = relevances[:k]
    if sum(rel) == 0:
        return 0.0
    precisions = [sum(rel[:i]) / i for i in range(1, k + 1) if rel[i - 1] == 1]
    return float(sum(precisions) / max(sum(rel), 1))


def mean_average_precision_at_k(relevances_list: List[List[int]], k: int) -> float:
    return float(np.mean([average_precision_at_k(rel, k) for rel in relevances_list]))


def ndcg_at_k(relevances: List[float], k: int) -> float:
    rel = np.array(relevances[:k], dtype=np.float64)
    gains = (2.0**rel - 1.0)
    discounts = 1.0 / np.log2(np.arange(2, k + 2))
    dcg = float(np.sum(gains * discounts))
    ideal = np.sort(rel)[::-1]
    idcg = float(np.sum((2.0**ideal - 1.0) * discounts))
    return 0.0 if idcg == 0.0 else dcg / idcg


def mean_ndcg_at_k(relevances_list: List[List[float]], k: int) -> float:
    return float(np.mean([ndcg_at_k(rel, k) for rel in relevances_list]))


# ------------- Minimal Demonstration -------------
def demo() -> None:
    # Classification demo
    rng = np.random.default_rng(42)
    y_true = rng.integers(0, 3, size=200)
    y_pred = y_true.copy()
    flip_idx = rng.choice(len(y_true), size=40, replace=False)
    y_pred[flip_idx] = rng.integers(0, 3, size=len(flip_idx))
    y_prob = np.clip(rng.random((200, 3)), 1e-6, 1.0)
    y_prob = y_prob / y_prob.sum(axis=1, keepdims=True)
    print("classification:", classification_metrics(y_true, y_pred, y_prob=y_prob))

    # Regression demo
    y = rng.standard_normal(200)
    y_hat = y + rng.normal(0, 0.5, size=y.shape)
    print("regression:", regression_metrics(y, y_hat))

    # Language modeling demo (fake logits)
    vocab = 100
    batch, seq = 8, 16
    logits = torch.randn(batch, seq, vocab)
    labels = torch.randint(0, vocab, (batch, seq))
    labels[labels % 7 == 0] = -100
    print("lm:", language_modeling_perplexity_from_logits(logits, labels))

    # Seq2Seq metrics
    preds = ["the cat sat on the mat", "transformers improve nlp"]
    refs = ["a cat is sitting on the mat", "transformers improve natural language processing"]
    print("seq2seq:", seq2seq_text_metrics(preds, refs))

    # Ranking metrics
    rel_lists = [[1, 0, 1, 0, 0], [0, 1, 0, 0, 1]]
    ranks = [[1], [2]]
    print("map@5:", mean_average_precision_at_k(rel_lists, k=5))
    print("mrr:", mean_reciprocal_rank(ranks))
    graded_lists = [[3, 2, 0, 1, 0], [0, 3, 2, 0, 1]]
    print("ndcg@5:", mean_ndcg_at_k(graded_lists, k=5))


if __name__ == "__main__":
    demo()



