from __future__ import annotations

import math
import os
from dataclasses import dataclass

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset, random_split


@dataclass
class Config:
    input_dim: int = int(os.getenv("INPUT_DIM", "128"))
    hidden: tuple[int, int] = tuple(int(x) for x in os.getenv("HIDDEN", "256,256").split(","))  # type: ignore[assignment]
    num_classes: int = int(os.getenv("NUM_CLASSES", "10"))
    dropout: float = float(os.getenv("DROPOUT", "0.0"))

    samples: int = int(os.getenv("SAMPLES", "20000"))
    val_ratio: float = float(os.getenv("VAL_RATIO", "0.1"))
    batch_size: int = int(os.getenv("BATCH", "256"))
    num_workers: int = int(os.getenv("WORKERS", "2"))
    pin_memory: bool = bool(int(os.getenv("PIN_MEMORY", "1")))

    epochs: int = int(os.getenv("EPOCHS", "5"))
    lr: float = float(os.getenv("LR", "3e-4"))
    wd: float = float(os.getenv("WD", "1e-2"))
    amp: bool = bool(int(os.getenv("AMP", "1")))
    clip: float = float(os.getenv("CLIP", "1.0"))
    seed: int = int(os.getenv("SEED", "0"))


class SyntheticClassification(Dataset):
    def __init__(self, n: int, d: int, c: int, seed: int) -> None:
        g = torch.Generator().manual_seed(seed)
        self.features = torch.randn(n, d, generator=g)
        W = torch.randn(c, d, generator=g)
        self.labels = (self.features @ W.T).argmax(dim=1)

    def __len__(self) -> int:
        return self.features.size(0)

    def __getitem__(self, i: int):
        return self.features[i], self.labels[i]


class MLP(nn.Module):
    def __init__(self, d: int, hidden: tuple[int, ...], c: int, p: float) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        prev = d
        for h in hidden:
            layers += [nn.Linear(prev, h), nn.ReLU(inplace=True)]
            if p > 0:
                layers += [nn.Dropout(p)]
            prev = h
        layers += [nn.Linear(prev, c)]
        self.net = nn.Sequential(*layers)
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, a=math.sqrt(5))
                if m.bias is not None:
                    fan_in, _ = nn.init._calculate_fan_in_and_fan_out(m.weight)
                    bound = 1 / math.sqrt(max(1, fan_in))
                    nn.init.uniform_(m.bias, -bound, bound)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def main() -> None:
    cfg = Config()
    torch.manual_seed(cfg.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True

    dataset = SyntheticClassification(cfg.samples, cfg.input_dim, cfg.num_classes, cfg.seed)
    val_len = max(1, int(len(dataset) * cfg.val_ratio))
    train_len = len(dataset) - val_len
    train_ds, val_ds = random_split(dataset, [train_len, val_len], generator=torch.Generator().manual_seed(cfg.seed))
    train_loader = DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=True, num_workers=cfg.num_workers, pin_memory=cfg.pin_memory, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=cfg.batch_size, shuffle=False, num_workers=cfg.num_workers, pin_memory=cfg.pin_memory)

    model = MLP(cfg.input_dim, cfg.hidden, cfg.num_classes, cfg.dropout).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.wd)
    scaler = torch.cuda.amp.GradScaler(enabled=cfg.amp and device == "cuda")
    loss_fn = nn.CrossEntropyLoss()

    for epoch in range(cfg.epochs):
        # Train
        model.train()
        total_loss = 0.0
        correct = 0
        seen = 0
        for xb, yb in train_loader:
            xb = xb.to(device, non_blocking=True)
            yb = yb.to(device, non_blocking=True)
            with torch.cuda.amp.autocast(enabled=cfg.amp and device == "cuda"):
                logits = model(xb)
                loss = loss_fn(logits, yb)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            if cfg.clip > 0:
                nn.utils.clip_grad_norm_(model.parameters(), cfg.clip)
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad(set_to_none=True)

            total_loss += float(loss) * xb.size(0)
            correct += int((logits.argmax(dim=1) == yb).sum())
            seen += xb.size(0)

        train_loss = total_loss / max(1, seen)
        train_acc = correct / max(1, seen)

        # Eval
        model.eval()
        v_loss = 0.0
        v_corr = 0
        v_seen = 0
        with torch.no_grad():
            for xb, yb in val_loader:
                xb = xb.to(device, non_blocking=True)
                yb = yb.to(device, non_blocking=True)
                logits = model(xb)
                loss = loss_fn(logits, yb)
                v_loss += float(loss) * xb.size(0)
                v_corr += int((logits.argmax(dim=1) == yb).sum())
                v_seen += xb.size(0)
        val_loss = v_loss / max(1, v_seen)
        val_acc = v_corr / max(1, v_seen)

        print(f"epoch={epoch} train_loss={train_loss:.4f} train_acc={train_acc:.4f} val_loss={val_loss:.4f} val_acc={val_acc:.4f}")


if __name__ == "__main__":
    main()



