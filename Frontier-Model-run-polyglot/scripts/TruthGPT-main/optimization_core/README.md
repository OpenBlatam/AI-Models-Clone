<div align="center">

# 🚀 TruthGPT Optimization Core

**The Enterprise-Grade, Modular Training System for Frontier Models**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch 2.1+](https://img.shields.io/badge/pytorch-2.1+-orange.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](docs/index.md)

[**Quick Start**](docs/quickstart.md) | [**Installation**](docs/installation.md) | [**Architecture**](docs/architecture.md) | [**API Reference**](docs/api/trainer.md)

</div>

---

## 🌟 Introduction

**TruthGPT Optimization Core** is a high-performance, modular framework designed to train Large Language Models (LLMs) with maximum efficiency. Built on PyTorch, it integrates state-of-the-art optimization techniques like **Flash Attention**, **TF32**, and **Torch.compile** into a unified, easy-to-use system.

Whether you are fine-tuning a 7B model on a single GPU or training a massive foundation model on a cluster, TruthGPT scales with you.

## ✨ Key Features

-   **⚡ Ultimate Performance**: Auto-configured for speed with TF32, mixed precision (BF16/FP16), and custom CUDA kernels.
-   **🧩 Modular Design**: Swap optimizers, attention backends, and datasets via a registry system. No code changes required.
-   **🧠 Smart Memory**: Gradient checkpointing, dynamic padding, and 8-bit optimizers allow training larger models on consumer hardware.
-   **🛡️ Production Ready**: Automatic error recovery, nan-detection, and seamless checkpoint resumption.
-   **📊 Observable**: Native integration with Weights & Biases and TensorBoard.

## 🚀 Quick Start

Train your first model in under 5 minutes:

```bash
# 1. Install
./setup_dev.sh

# 2. Run a preset
python train_llm.py --config configs/presets/lora_fast.yaml
```

👉 **[Read the Full Quick Start Guide](docs/quickstart.md)**

## 📖 Documentation

Dive deep into the system:

-   **[Installation Guide](docs/installation.md)**: Setup for Dev, Prod, Docker, and Conda.
-   **[System Architecture](docs/architecture.md)**: Understand the registry patterns and component flow.
-   **[Optimization Techniques](docs/optimization.md)**: Learn how we achieve high GPU utilization.
-   **[Configuration Reference](docs/api/configuration.md)**: Every YAML option explained.
-   **[Trainer API](docs/api/trainer.md)**: Developer documentation for the core engine.

## 🛠️ Project Structure

```text
optimization_core/
├── configs/               # YAML Configurations
├── docs/                  # 📚 Comprehensive Documentation
├── factories/             # Component Registries (Optimizers, etc.)
├── trainers/              # Core Training Logic
├── scripts/               # Utility Scripts
└── train_llm.py           # Main Entry Point
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

---

<div align="center">
    Built with ❤️ by the TruthGPT Team
</div>
