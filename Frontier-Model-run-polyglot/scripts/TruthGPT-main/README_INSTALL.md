# TruthGPT Installation Hub

**Enterprise-Grade Setup for Frontier Model Training**

We provide automated installers that adhere to Python best practices:
1.  **Isolation**: Always creates a `.venv` (virtual environment) by default.
2.  **Hardware Awareness**: Installs the correct PyTorch version for your CUDA driver or CPU.
3.  **Developer Friendly**: Installs the core package in editable mode (`pip install -e`) so you can modify code instantly.

---

## ⚡ Quick Start

### 🍎 macOS / 🐧 Linux
```bash
# Default (CUDA 11.8 on Linux, MPS on Mac)
./install.sh

# Installation with options
./install.sh --cuda 12.1
```

### 🪟 Windows (PowerShell)
```powershell
# Default (CUDA 11.8)
.\install.ps1

# Installation with options
.\install.ps1 -CudaVersion "12.1"
```

---

## � Advanced Usage

### Windows Arguments

| Parameter | Default | Description |
| :--- | :--- | :--- |
| `-CudaVersion` | `"11.8"` | `11.8`, `12.1`, or `cpu`. Matches PyTorch index URL. |
| `-PythonVersion` | `"python"` | Python executable to use (e.g., `C:\Python311\python.exe`). |
| `-SkipVenv` | `False` | Pass this switch to install dependencies into the *current* active environment. |

**Example**:
```powershell
# Install for CPU only using specific python
.\install.ps1 -PythonVersion "py -3.10" -CudaVersion "cpu"
```

### Linux/macOS Arguments

| Flag | Default | Description |
| :--- | :--- | :--- |
| `--cuda <ver>` | `11.8` | `11.8`, `12.1`, or `cpu`. (Ignored on macOS). |
| `--python <path>` | `python3` | Python executable path. |
| `--skip-venv` | `False` | Install into current environment. |

**Example**:
```bash
# Install for CUDA 12.1 without creating a new venv
./install.sh --cuda 12.1 --skip-venv
```

---

## ❓ Troubleshooting

### "Python not found"
Ensure you have Python 3.10+ installed and added to your system PATH.
-   **Windows**: Check "Add Python to PATH" during installation.
-   **Linux**: `sudo apt install python3-venv python3-pip`

### "Execution Policy Restriction" (Windows)
If PowerShell blocks the script:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "CUDA OOM" or "Torch not found"
If PyTorch isn't detecting your GPU, verify your Nvidia drivers match the CUDA version requested.
Run `nvidia-smi` to check your driver version.
