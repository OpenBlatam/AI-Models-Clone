from __future__ import annotations

import torch
from torch.autograd.functional import vjp, jvp


def basic_backward() -> None:
    x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)
    y = (x ** 2).sum()
    y.backward()
    print("x.grad", x.grad.tolist())  # [2, 4, 6]


def grad_and_higher_order() -> None:
    w = torch.randn(5, requires_grad=True)
    f = (w.sin() * w).sum()
    g = torch.autograd.grad(f, w, create_graph=True)[0]
    # Hessian-vector product via grad of dot(grad, v)
    v = torch.randn_like(w)
    hvp = torch.autograd.grad((g * v).sum(), w)[0]
    print("grad_norm", float(g.norm()), "hvp_norm", float(hvp.norm()))


def custom_function() -> None:
    class StableLog(torch.autograd.Function):
        @staticmethod
        def forward(ctx, inp: torch.Tensor) -> torch.Tensor:
            ctx.save_for_backward(inp)
            return inp.clamp_min(1e-6).log()

        @staticmethod
        def backward(ctx, grad_output: torch.Tensor) -> tuple[torch.Tensor]:
            (inp,) = ctx.saved_tensors
            grad_inp = grad_output / inp.clamp_min(1e-6)
            return grad_inp

    x = torch.tensor([0.1, 1.0, 10.0], requires_grad=True)
    y = StableLog.apply(x).sum()
    y.backward()
    print("custom_grad", x.grad.tolist())


def vjp_jvp_demo() -> None:
    def func(z: torch.Tensor) -> torch.Tensor:
        # R^n -> R^2
        return torch.stack([z.pow(2).sum(), z.sin().sum()])

    z = torch.randn(4, requires_grad=True)
    # VJP: v^T J_f(z)
    v = torch.tensor([1.0, 0.0])
    _, vjp_val = vjp(func, z, v)
    # JVP: J_f(z) u
    u = torch.randn_like(z)
    _, jvp_val = jvp(func, (z,), (u,))
    print("vjp_norm", float(vjp_val.norm()), "jvp_norm", float(jvp_val.norm()))


def main() -> None:
    basic_backward()
    grad_and_higher_order()
    custom_function()
    vjp_jvp_demo()


if __name__ == "__main__":
    main()



