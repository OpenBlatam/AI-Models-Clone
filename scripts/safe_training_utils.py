from __future__ import annotations

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


def is_finite_tensor(t: torch.Tensor) -> bool:
    return torch.isfinite(t).all().item() if t.numel() > 0 else True


def sanitize_gradients_(model: nn.Module, clamp_value: float | None = None) -> None:
    for param in model.parameters():
        if param.grad is None:
            continue
        torch.nan_to_num_(param.grad, nan=0.0, posinf=0.0, neginf=0.0)
        if clamp_value is not None:
            param.grad.data.clamp_(min=-clamp_value, max=clamp_value)


def safe_train_step(
    model: nn.Module,
    inputs: torch.Tensor,
    targets: torch.Tensor,
    optimizer: torch.optim.Optimizer,
    loss_fn: nn.Module,
    scaler: torch.cuda.amp.GradScaler,
    grad_clip_norm: float = 1.0,
    grad_value_clip: float | None = None,
    use_amp: bool | None = None,
) -> tuple[float, bool]:
    if use_amp is None:
        use_amp = torch.cuda.is_available()

    optimizer.zero_grad(set_to_none=True)

    with torch.cuda.amp.autocast(enabled=use_amp):
        logits = model(inputs)
        loss = loss_fn(logits, targets)

    if not is_finite_tensor(loss):
        optimizer.zero_grad(set_to_none=True)
        return float("inf"), True

    scaler.scale(loss).backward()
    scaler.unscale_(optimizer)

    sanitize_gradients_(model, clamp_value=grad_value_clip)
    nn.utils.clip_grad_norm_(model.parameters(), grad_clip_norm)

    scaler.step(optimizer)
    scaler.update()
    optimizer.zero_grad(set_to_none=True)

    return float(loss.detach().item()), False


if __name__ == "__main__":
    torch.manual_seed(0)
    device = torch.device("cuda", 0) if torch.cuda.is_available() else torch.device("cpu")

    x = torch.randn(4096, 128)
    w = torch.randn(128, 10)
    y = torch.multinomial((x @ w).softmax(-1), 1).squeeze(-1)
    dl = DataLoader(TensorDataset(x, y), batch_size=256, shuffle=True)

    model = nn.Sequential(nn.Linear(128, 256), nn.GELU(), nn.Linear(256, 10)).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.01)
    loss_fn = nn.CrossEntropyLoss()
    scaler = torch.cuda.amp.GradScaler(enabled=(device.type == "cuda"))

    for step, (xb, yb) in enumerate(dl, 1):
        xb = xb.to(device, non_blocking=True)
        yb = yb.to(device, non_blocking=True)
        loss, skipped = safe_train_step(
            model,
            xb,
            yb,
            opt,
            loss_fn,
            scaler,
            grad_clip_norm=1.0,
            grad_value_clip=1.0,
            use_amp=(device.type == "cuda"),
        )
        if step % 20 == 0:
            print({"step": step, "loss": round(loss, 4), "skipped": skipped})
        if step == 200:
            break



