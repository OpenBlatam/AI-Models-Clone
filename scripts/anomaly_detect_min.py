from __future__ import annotations

import os
import torch
import torch.nn as nn


class TinyNet(nn.Module):
    def __init__(self, d: int = 16) -> None:
        super().__init__()
        self.fc = nn.Linear(d, d)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc(x)
        return x


def main() -> None:
    torch.manual_seed(int(os.getenv("SEED", "0")))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = TinyNet().to(device)
    crit = nn.MSELoss()

    x = torch.randn(32, 16, device=device, requires_grad=True)
    y = torch.zeros(32, 16, device=device)

    torch.autograd.set_detect_anomaly(True)
    try:
        out = model(x)
        # Deliberate anomaly: log of negative values -> NaNs/Infs with grad trace
        out = torch.log(out - 10.0)
        loss = crit(out, y)
        loss.backward()
    except RuntimeError as e:
        print(f"Anomaly detected: {e}")


if __name__ == "__main__":
    main()



