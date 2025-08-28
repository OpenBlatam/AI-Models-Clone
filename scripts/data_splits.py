from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, Iterator, Tuple

import numpy as np
import torch
from sklearn.model_selection import GroupKFold, StratifiedKFold, train_test_split
from torch.utils.data import DataLoader, TensorDataset


@dataclass
class SplitConfig:
    num_samples: int = int(os.getenv("SAMPLES", "10000"))
    input_dim: int = int(os.getenv("INPUT_DIM", "128"))
    num_classes: int = int(os.getenv("NUM_CLASSES", "5"))
    test_size: float = float(os.getenv("TEST_SIZE", "0.2"))
    val_size: float = float(os.getenv("VAL_SIZE", "0.1"))
    seed: int = int(os.getenv("SEED", "42"))
    batch_size: int = int(os.getenv("BATCH_SIZE", "256"))
    num_workers: int = int(os.getenv("NUM_WORKERS", "4"))
    pin_memory: bool = bool(int(os.getenv("PIN_MEMORY", "1")))
    persistent_workers: bool = bool(int(os.getenv("PERSISTENT", "1")))


def generate_synthetic_classification_data(
    num_samples: int, input_dim: int, num_classes: int, seed: int
) -> Tuple[torch.Tensor, torch.Tensor, np.ndarray]:
    g = torch.Generator().manual_seed(seed)
    features = torch.randn(num_samples, input_dim, generator=g)
    # Create class centroids and assign labels by nearest centroid
    centroids = torch.randn(num_classes, input_dim, generator=g) * 2.0
    # Compute rough logits by dot product to induce class structure
    logits = features @ centroids.T
    labels = logits.argmax(dim=1)
    # Optional groups to demonstrate GroupKFold
    groups = torch.randint(0, max(2, num_classes // 2), (num_samples,), generator=g).numpy()
    return features, labels, groups


def stratified_train_val_test_split(
    X: torch.Tensor,
    y: torch.Tensor,
    *,
    test_size: float,
    val_size: float,
    seed: int,
) -> Tuple[Tuple[torch.Tensor, torch.Tensor], Tuple[torch.Tensor, torch.Tensor], Tuple[torch.Tensor, torch.Tensor]]:
    assert 0 < test_size < 1 and 0 < val_size < 1 and test_size + val_size < 1
    X_np = X.numpy()
    y_np = y.numpy()

    # First split off temp (val+test)
    temp_size = test_size + val_size
    X_train, X_temp, y_train, y_temp = train_test_split(
        X_np, y_np, test_size=temp_size, stratify=y_np, random_state=seed
    )
    # Split temp into val and test with preserved class ratios
    val_ratio = val_size / temp_size
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=(1 - val_ratio), stratify=y_temp, random_state=seed
    )
    return (
        (torch.from_numpy(X_train), torch.from_numpy(y_train)),
        (torch.from_numpy(X_val), torch.from_numpy(y_val)),
        (torch.from_numpy(X_test), torch.from_numpy(y_test)),
    )


def build_loaders_from_splits(
    train_split: Tuple[torch.Tensor, torch.Tensor],
    val_split: Tuple[torch.Tensor, torch.Tensor],
    test_split: Tuple[torch.Tensor, torch.Tensor],
    *,
    batch_size: int,
    num_workers: int,
    pin_memory: bool,
    persistent_workers: bool,
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    train_loader = DataLoader(
        TensorDataset(train_split[0], train_split[1]),
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=persistent_workers if num_workers > 0 else False,
        drop_last=True,
    )
    val_loader = DataLoader(
        TensorDataset(val_split[0], val_split[1]),
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=persistent_workers if num_workers > 0 else False,
    )
    test_loader = DataLoader(
        TensorDataset(test_split[0], test_split[1]),
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=persistent_workers if num_workers > 0 else False,
    )
    return train_loader, val_loader, test_loader


def stratified_kfold_indices(y: torch.Tensor, n_splits: int, seed: int) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    y_np = y.numpy()
    for train_idx, val_idx in skf.split(np.zeros_like(y_np), y_np):
        yield train_idx, val_idx


def group_kfold_indices(groups: np.ndarray, n_splits: int) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
    gkf = GroupKFold(n_splits=n_splits)
    dummy = np.zeros_like(groups)
    for train_idx, val_idx in gkf.split(dummy, dummy, groups):
        yield train_idx, val_idx


def example_usage() -> None:
    cfg = SplitConfig()
    torch.manual_seed(cfg.seed)
    X, y, groups = generate_synthetic_classification_data(cfg.num_samples, cfg.input_dim, cfg.num_classes, cfg.seed)

    # Train/Val/Test stratified split
    train_split, val_split, test_split = stratified_train_val_test_split(
        X, y, test_size=cfg.test_size, val_size=cfg.val_size, seed=cfg.seed
    )
    train_loader, val_loader, test_loader = build_loaders_from_splits(
        train_split,
        val_split,
        test_split,
        batch_size=cfg.batch_size,
        num_workers=cfg.num_workers,
        pin_memory=cfg.pin_memory,
        persistent_workers=cfg.persistent_workers,
    )
    print(
        f"sizes train={len(train_loader.dataset)} val={len(val_loader.dataset)} test={len(test_loader.dataset)}"
    )

    # Stratified K-Fold demonstration
    for fold, (tr_idx, va_idx) in enumerate(stratified_kfold_indices(y, n_splits=5, seed=cfg.seed), start=1):
        print(f"StratifiedKFold fold={fold} train={len(tr_idx)} val={len(va_idx)}")

    # Group K-Fold demonstration (ensures all samples of a group stay in one split)
    for fold, (tr_idx, va_idx) in enumerate(group_kfold_indices(groups, n_splits=5), start=1):
        print(f"GroupKFold fold={fold} train={len(tr_idx)} val={len(va_idx)}")


if __name__ == "__main__":
    example_usage()

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Tuple, Iterable, List

import numpy as np
import torch
from sklearn.model_selection import StratifiedKFold, train_test_split
from torch.utils.data import DataLoader, Dataset, Subset, TensorDataset


@dataclass
class SplitConfig:
    val_size: float = 0.1
    test_size: float = 0.1
    seed: int = 42
    batch_size: int = 256
    num_workers: int = 2
    pin_memory: bool = True
    persistent_workers: bool = False
    prefetch_factor: int = 2
    k_folds: int = 5


def stratified_train_val_test_split(
    labels: np.ndarray,
    val_size: float,
    test_size: float,
    seed: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    assert 0 < val_size < 1 and 0 < test_size < 1 and (val_size + test_size) < 1
    indices = np.arange(labels.shape[0])
    idx_train, idx_test = train_test_split(
        indices, test_size=test_size, random_state=seed, stratify=labels
    )
    y_train = labels[idx_train]
    rel_val_size = val_size / (1.0 - test_size)
    idx_train, idx_val = train_test_split(
        idx_train, test_size=rel_val_size, random_state=seed, stratify=y_train
    )
    return idx_train, idx_val, idx_test


def build_loaders_from_indices(
    dataset: Dataset,
    idx_train: np.ndarray,
    idx_val: np.ndarray,
    idx_test: np.ndarray,
    batch_size: int,
    num_workers: int,
    pin_memory: bool,
    persistent_workers: bool,
    prefetch_factor: int,
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    train_ds = Subset(dataset, idx_train.tolist())
    val_ds = Subset(dataset, idx_val.tolist())
    test_ds = Subset(dataset, idx_test.tolist())
    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=persistent_workers and num_workers > 0,
        prefetch_factor=prefetch_factor if num_workers > 0 else None,
    )
    eval_kwargs = dict(
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=persistent_workers and num_workers > 0,
        prefetch_factor=prefetch_factor if num_workers > 0 else None,
    )
    return train_loader, DataLoader(val_ds, **eval_kwargs), DataLoader(test_ds, **eval_kwargs)


def stratified_kfold_indices(labels: np.ndarray, k_folds: int, seed: int) -> Iterable[Tuple[np.ndarray, np.ndarray]]:
    skf = StratifiedKFold(n_splits=k_folds, shuffle=True, random_state=seed)
    for train_idx, val_idx in skf.split(np.zeros_like(labels), labels):
        yield train_idx, val_idx


def demo_build_dataset(n: int = 50_000, d: int = 128, k: int = 10, seed: int = 7) -> TensorDataset:
    g = torch.Generator().manual_seed(seed)
    x = torch.randn(n, d, generator=g)
    w = torch.randn(d, k, generator=g)
    y = torch.multinomial((x @ w).softmax(-1), 1, generator=g).squeeze(-1)
    return TensorDataset(x, y)


def main() -> None:
    ap = argparse.ArgumentParser(description="Stratified train/val/test splits and K-Fold loaders")
    ap.add_argument("--val-size", type=float, default=0.1)
    ap.add_argument("--test-size", type=float, default=0.1)
    ap.add_argument("--k-folds", type=int, default=5)
    ap.add_argument("--batch-size", type=int, default=256)
    ap.add_argument("--num-workers", type=int, default=2)
    args = ap.parse_args()

    cfg = SplitConfig(
        val_size=args.val_size,
        test_size=args.test_size,
        k_folds=args.k_folds,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
    )

    dataset = demo_build_dataset()
    labels = dataset.tensors[1].cpu().numpy()

    idx_train, idx_val, idx_test = stratified_train_val_test_split(labels, cfg.val_size, cfg.test_size, cfg.seed)
    train_loader, val_loader, test_loader = build_loaders_from_indices(
        dataset,
        idx_train,
        idx_val,
        idx_test,
        cfg.batch_size,
        cfg.num_workers,
        pin_memory=torch.cuda.is_available(),
        persistent_workers=cfg.persistent_workers,
        prefetch_factor=cfg.prefetch_factor,
    )

    print({
        "train_batches": len(train_loader),
        "val_batches": len(val_loader),
        "test_batches": len(test_loader),
        "k_folds": cfg.k_folds,
    })

    # Demonstrate K-Fold (train/val) splits
    for fold, (tr, va) in enumerate(stratified_kfold_indices(labels, cfg.k_folds, cfg.seed), start=1):
        print({"fold": fold, "train_size": int(tr.size), "val_size": int(va.size)})


if __name__ == "__main__":
    main()


