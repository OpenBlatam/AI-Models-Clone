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
# 1. Install (Windows - Recommended)
.\portable_setup.ps1

# 1. Install (Windows - Advanced)
.\install.ps1

# 1. Install (Linux/macOS)
./install.sh

# 2. Use the OpenClaw CLI
openclaw --help

# 3. Run a preset via CLI
openclaw train --config configs/presets/lora_fast.yaml
```

👉 **[Read the Full Quick Start Guide](docs/quickstart.md)**

## 📖 Documentation

Dive deep into the system:

-   **[Installation Guide](docs/installation.md)**: Setup for Dev, Prod, Docker, and Conda.
-   **[System Architecture](docs/architecture.md)**: Understand the registry patterns and component flow.
-   **[Optimization Techniques](docs/optimization.md)**: Learn how we achieve high GPU utilization.
-   **[Configuration Reference](docs/api/configuration.md)**: Every YAML option explained.
-   **[Trainer API](docs/api/trainer.md)**: Developer documentation for the core engine.

## 🤖 OpenClaw Agents SDK & API

TruthGPT Optimization Core now includes full **OpenClaw-compatible** autonomous agent capabilities. You can use it via Python SDK or REST API:

### Python SDK
```python
import asyncio
from optimization_core.agents import AgentClient

async def main():
    # Inicializa el cliente (funciona igual que OpenClaw)
    client = AgentClient(use_swarm=False)
    
    # Añade herramientas (ej. file_read, python_execute, web_search)
    client.add_tool("web_search")
    client.add_tool("python_execute")
    
    # Ejecuta el agente autónomo
    response = await client.run(user_id="user123", prompt="Busca en internet el precio de Bitcoin y calcula el 10% en Python.")
    print(response)

asyncio.run(main())
```

### REST API
Start the inference server (`openclaw serve`) and call the agent endpoint:

```bash
curl -X POST http://localhost:8080/v1/agent/run \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer changeme" \\
  -d '{
    "prompt": "Escribe un script en un archivo de python que imprima hola mundo",
    "user_id": "user123",
    "tools": ["file_write"]
  }'
```

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
