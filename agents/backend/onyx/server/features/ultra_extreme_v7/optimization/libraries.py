import importlib
import logging

logger = logging.getLogger(__name__)

LIBRARIES = [
    'qiskit', 'pennylane', 'transformers', 'accelerate', 'bitsandbytes', 'peft',
    'optuna', 'hyperopt', 'ray', 'pytorch_lightning', 'cupy', 'numba',
    'wandb', 'mlflow', 'dask', 'cryptography'
]

def check_libraries():
    """Verifica e informa el estado de las librerías avanzadas."""
    status = {}
    for lib in LIBRARIES:
        try:
            importlib.import_module(lib)
            status[lib] = True
        except ImportError:
            status[lib] = False
    logger.info(f"Estado de librerías: {status}")
    return status 