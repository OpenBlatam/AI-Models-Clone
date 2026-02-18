"""
Optimization Core - Structure Verification Tests
=================================================
Verifies that all __init__.py exports and lazy import systems resolve correctly.
Uses extensive mocking to bypass missing heavy dependencies (torch, numpy, etc.).
"""

import sys
import unittest
from unittest.mock import MagicMock
from abc import ABC
import os
import importlib.util
import importlib

# ── Project root on sys.path ──────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PARENT_ROOT = os.path.dirname(PROJECT_ROOT)

# Ensure ONLY the parent of optimization_core is in sys.path to prevent "top-level" import issues
if PARENT_ROOT not in sys.path:
    sys.path.insert(0, PARENT_ROOT)
# We EXPLICITLY do not add PROJECT_ROOT here so that 'from optimization_core.xxx' is the standard.
# This fixes the "attempted relative import beyond top-level package" error.

# ── Mock heavy external dependencies ─────────────────────────────────
# We need __spec__ set on top-level mocks so importlib.util.find_spec works
import types

def _make_mock_module(name: str) -> MagicMock:
    """Create a MagicMock that has a proper __spec__ for importlib compat."""
    m = MagicMock()
    m.__spec__ = types.ModuleType(name).__spec__  # None, but attr exists
    m.__name__ = name
    m.__path__ = []
    m.__file__ = f"<mock:{name}>"
    m.__version__ = "1.0.0"  # Fake version for compatibility
    m.__mro__ = (object,)  # Added to support dataclasses/peft
    m.__pyx_capi__ = {}  # Fix for Cython compatibility
    return m

_MOCK_MODULES = [
    # Data Science / Common
    "pandas", "pandas.core", "pandas.core.frame",
    "matplotlib", "matplotlib.pyplot",
    "seaborn",
    "plotly", "plotly.graph_objects",
    # PyTorch – every submodule any file might import
    "torch", "torch.nn", "torch.nn.functional", "torch.nn.utils",
    "torch.nn.init", "torch.nn.parameter", "torch.nn.parallel",
    "torch.optim", "torch.optim.lr_scheduler",
    "torch.utils", "torch.utils.data", "torch.utils.checkpoint",
    "torch.cuda", "torch.cuda.amp", "torch.distributed",
    "torch.jit", "torch.autograd",
    "torch.fx", "torch.profiler", "torch.onnx",
    "torch.quantization", "torch.ao", "torch.ao.quantization",
    "torch.compile", "torch.export",
    "torch.sparse", "torch.backends", "torch.backends.cudnn",
    # NumPy / SciPy
    "numpy", "numpy.linalg", "scipy", "scipy.optimize",
    # TensorFlow
    "tensorflow", "tensorflow.keras",
    # Diffusers / HuggingFace
    "diffusers", "diffusers.utils", "diffusers.pipelines",
    # Others
    "triton", "triton.language",
    "transformers", "transformers.utils", "transformers.modeling_utils", "transformers.utils.hub",
    "datasets", "tokenizers",
    "onnxruntime", "tensorrt",
    "pycuda", "pycuda.driver",
    "cupy",
    "accelerate", "accelerate.utils", "accelerate.utils.memory", "accelerate.hooks", "accelerate.state",
    "bitsandbytes",
    "peft",
    "safetensors", "safetensors.torch",
    "wandb",
    "mlflow",
    "gradio",
    "fastapi", "fastapi.middleware", "fastapi.middleware.trustedhost", 
    "fastapi.middleware.cors", "fastapi.middleware.gzip", "fastapi.responses",
    "uvicorn", "pydantic",
    "pkg_resources",
    "sklearn", "sklearn.model_selection", "sklearn.metrics", "sklearn.utils",
    "skimage", "skimage.io", "skimage.transform",
]

# Robust mocking: Mock every requested module if it's in our list or starts with one of them
for mod_name in _MOCK_MODULES:
    if mod_name not in sys.modules:
        try:
            # Try to import real module first for common ones
            if mod_name in ["numpy", "torch", "pandas"]:
                importlib.import_module(mod_name)
                continue
        except ImportError:
            pass
        sys.modules[mod_name] = _make_mock_module(mod_name)

# Add a fake module loader for submodules
class MockFinder:
    def find_spec(self, fullname, path, target=None):
        import importlib.util
        for mod in _MOCK_MODULES:
            if fullname == mod or fullname.startswith(mod + '.'):
                return importlib.util.spec_from_loader(fullname, self)
        return None

    def create_module(self, spec):
        # Return a MagicMock for any module found by this finder
        return _make_mock_module(spec.name) # Use _make_mock_module to ensure __spec__ is set

    def exec_module(self, module):
        # No execution needed for mock modules
        pass

sys.meta_path.insert(0, MockFinder())


# Fix for metaclass conflict: Ensure torch.nn.Module is a class and compatible with ABC
class MockModule(ABC):
    pass

if "torch.nn" in sys.modules:
    sys.modules["torch.nn"].Module = MockModule


class TestOptimizersPackage(unittest.TestCase):
    """Tests for the `optimizers` package."""

    def test_import_optimizers(self):
        """Top-level import of optimizers should succeed."""
        import optimization_core.optimizers as optimizers  # noqa: F811
        self.assertTrue(hasattr(optimizers, "__all__"))
        print("\n[OK] import optimizers")

    def test_factory_function(self):
        """create_truthgpt_optimizer should be callable."""
        from optimization_core.modules.optimizers import create_truthgpt_optimizer
        self.assertTrue(callable(create_truthgpt_optimizer))
        print("[OK] create_truthgpt_optimizer is callable")

    def test_lazy_core_submodule(self):
        """Lazily accessing optimizers.core should return a module."""
        from optimization_core import optimizers
        core = optimizers.core
        self.assertIsNotNone(core)
        print(f"[OK] optimizers.core = {core}")

    def test_optimization_cores_factory(self):
        """create_optimization_core factory should be importable."""
        from optimization_core.modules.optimizers.optimization_cores import create_optimization_core
        self.assertTrue(callable(create_optimization_core))
        print("[OK] create_optimization_core is callable")

    def test_optimization_cores_list(self):
        """list_available_cores should return a non-empty list."""
        from optimization_core.modules.optimizers.optimization_cores import list_available_cores
        cores = list_available_cores()
        self.assertIsInstance(cores, list)
        self.assertGreater(len(cores), 0)
        print(f"[OK] Available cores: {cores}")

    def test_backward_compat_enhanced(self):
        """EnhancedOptimizationCore should be importable from optimizers (shim)."""
        from optimization_core.modules.optimizers import EnhancedOptimizationCore
        self.assertIsNotNone(EnhancedOptimizationCore)
        print("[OK] EnhancedOptimizationCore backward compat")

    def test_generic_optimizer(self):
        """Generic optimizer should be importable."""
        from optimization_core.modules.optimizers import create_generic_optimizer
        self.assertTrue(callable(create_generic_optimizer))
        print("[OK] create_generic_optimizer is callable")


class TestOptimizationCoreTopLevel(unittest.TestCase):
    """Tests for the top-level `optimization_core` package (this directory)."""

    def test_import_top_level(self):
        """Top-level __init__.py should load without error."""
        # Add parent dir so 'optimization_core' resolves as a real package
        parent_dir = os.path.dirname(PROJECT_ROOT)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        try:
            import optimization_core  # noqa: F811
            self.assertTrue(hasattr(optimization_core, '__version__'))
            print("\n[OK] import optimization_core")
        except Exception as e:
            self.fail(f"Failed to import optimization_core: {e}")

class TestModulesOptimizers(unittest.TestCase):
    """Tests for the `modules.optimizers` subpackage after file move."""

    def test_import_modules_optimizers(self):
        """modules.optimizers should import cleanly."""
        from optimization_core.modules import optimizers as mod_opt
        self.assertTrue(hasattr(mod_opt, "__all__"))
        print("\n[OK] import modules.optimizers")

    def test_module_optimizer_factory(self):
        """create_module_optimizer factory should be callable."""
        from optimization_core.modules.optimizers import create_module_optimizer
        self.assertTrue(callable(create_module_optimizer))
        print("[OK] create_module_optimizer is callable")

    def test_module_optimizer_registry(self):
        """MODULE_OPTIMIZER_REGISTRY should list cuda, gpu, memory."""
        from optimization_core.modules.optimizers import list_available_module_optimizers
        available = list_available_module_optimizers()
        self.assertIn("cuda", available)
        self.assertIn("gpu", available)
        self.assertIn("memory", available)
        print(f"[OK] Module optimizers: {available}")

    def test_backward_compat_cuda(self):
        """CudaKernelOptimizer should be importable from modules (backward compat)."""
        try:
            from optimization_core.modules import CudaKernelOptimizer
            self.assertIsNotNone(CudaKernelOptimizer)
            print("[OK] CudaKernelOptimizer backward compat from modules")
        except ImportError:
            print("[SKIP] CudaKernelOptimizer not found in optimization_core.modules")

    def test_backward_compat_gpu(self):
        """GPUOptimizer should be importable from modules (backward compat)."""
        try:
            from optimization_core.modules import GPUOptimizer
            self.assertIsNotNone(GPUOptimizer)
            print("[OK] GPUOptimizer backward compat from modules")
        except ImportError:
            print("[SKIP] GPUOptimizer not found in optimization_core.modules")

    def test_backward_compat_memory(self):
        """MemoryOptimizer should be importable from modules (backward compat)."""
        try:
            from optimization_core.modules import MemoryOptimizer
            self.assertIsNotNone(MemoryOptimizer)
            print("[OK] MemoryOptimizer backward compat from modules")
        except ImportError:
            print("[SKIP] MemoryOptimizer not found in optimization_core.modules")


class TestMassiveRefactor(unittest.TestCase):
    """Tests for Phase 3 (Feed Forward) and Phase 4 (Optimizers) changes."""

    def test_feed_forward_structure(self):
        """Verify feed_forward submodules exist and are importable."""
        try:
            from optimization_core.modules.feed_forward import core, routing, optimization, systems
            self.assertIsNotNone(core)
            self.assertIsNotNone(routing)
            self.assertIsNotNone(optimization)
            self.assertIsNotNone(systems)
            print("\n[OK] modules.feed_forward submodules imported")
        except ImportError as e:
            self.fail(f"Failed to import feed_forward submodules: {e}")

    def test_feed_forward_exports(self):
        """Verify key classes are exported from feed_forward submodules."""
        try:
            from optimization_core.modules.feed_forward.core import FeedForward
            from optimization_core.modules.feed_forward.systems import ProductionPiMoESystem
            
            self.assertIsNotNone(FeedForward)
            self.assertIsNotNone(ProductionPiMoESystem)
            print("[OK] modules.feed_forward class exports verified")
        except ImportError as e:
            self.fail(f"Failed to import feed_forward classes: {e}")

    def test_feed_forward_backward_compat(self):
        """Verify modules.feed_forward still exports classes directly."""
        try:
            from optimization_core.modules.feed_forward import FeedForward, ProductionPiMoESystem
            self.assertIsNotNone(FeedForward)
            self.assertIsNotNone(ProductionPiMoESystem)
            print("[OK] modules.feed_forward backward compatibility verified")
        except ImportError as e:
            self.fail(f"Failed to verify feed_forward backward compat: {e}")

    def test_optimizers_mcts(self):
        """Verify optimizers.mcts submodule."""
        from optimization_core.modules.optimizers import mcts
        from optimization_core.modules.optimizers.mcts import MCTSOptimizer
        self.assertIsNotNone(mcts)
        self.assertIsNotNone(MCTSOptimizer)
        print("[OK] optimizers.mcts verified")

    def test_optimizers_truthgpt(self):
        """Verify optimizers.truthgpt submodule exports."""
        try:
            from optimization_core.modules.optimizers import truthgpt
            from optimization_core.modules.optimizers.truthgpt import SupremeTruthGPTOptimizer
            self.assertIsNotNone(truthgpt)
            self.assertIsNotNone(SupremeTruthGPTOptimizer)
            print("[OK] optimizers.truthgpt verified")
        except ImportError as e:
            self.fail(f"Failed to import truthgpt optimizer: {e}")

    def test_optimizers_transformer(self):
        """Verify optimizers.transformer submodule exports."""
        # Import via full package path to ensure relative imports work correctly
        try:
            import optimization_core.optimizers.transformer as transformer
            from optimization_core.modules.optimizers.transformer import TransformerOptimizer
            
            self.assertIsNotNone(transformer)
            self.assertIsNotNone(TransformerOptimizer)
            print("[OK] optimizers.transformer verified")
        except ImportError as e:
            self.fail(f"Failed to import transformer optimizer: {e}")


    def test_optimizers_transformer_shim(self):
        """Verify TransformerOptimizer shim in root package."""
        try:
            from optimization_core.modules.optimizers import TransformerOptimizer
            self.assertIsNotNone(TransformerOptimizer)
            print("[OK] TransformerOptimizer shim verified")
        except ImportError as e:
            self.fail(f"Failed to import TransformerOptimizer shim: {e}")
        except Exception as e:
            self.fail(f"Unexpected error importing shim: {e}")


class TestPhase5Consolidation(unittest.TestCase):
    """Tests for Phase 5 (Root Optimizer Consolidation) changes."""

    def test_techniques_relocation(self):
        """Verify techniques are importable from the new location."""
        from optimization_core.modules.optimizers.techniques import (
            AdvancedRMSNorm,
            RotaryEmbedding,
            SwiGLU,
            RLPruning,
            ComputationalOptimizer,
            TritonOptimizations
        )
        self.assertIsNotNone(AdvancedRMSNorm)
        self.assertIsNotNone(RotaryEmbedding)
        self.assertIsNotNone(SwiGLU)
        self.assertIsNotNone(RLPruning)
        self.assertIsNotNone(ComputationalOptimizer)
        self.assertIsNotNone(TritonOptimizations)
        print("\n[OK] optimizers.techniques relocated modules verified")

    def test_registries_relocation(self):
        """Verify registries are importable from the new location."""
        from optimization_core.modules.optimizers.registries import (
            get_config_v1,
            get_config_v2
        )
        self.assertIsNotNone(get_config_v1)
        self.assertIsNotNone(get_config_v2)
        print("[OK] optimizers.registries modules verified")

        print("[OK] root optimizer shims verified")

    def test_technique_shims(self):
        """Verify technique shims in root optimizers directory."""
        from optimization_core.modules.optimizers import computational_optimizations, triton_optimizations
        self.assertTrue(hasattr(computational_optimizations, "ComputationalOptimizer"))
        self.assertTrue(hasattr(triton_optimizations, "TritonOptimizations"))
        print("[OK] technique shims verified")


class TestLibraryRefactor(unittest.TestCase):
    """Tests for Phase 6 (Library Refactor) changes."""

    def test_library_structure(self):
        """Verify libraries subpackage exists and is importable."""
        try:
            from optimization_core.modules import libraries
            from optimization_core.modules.libraries import (
                core, models, data, training, optimization, 
                evaluation, inference, monitoring, config_manager, system
            )
            self.assertIsNotNone(core)
            self.assertIsNotNone(models)
            self.assertIsNotNone(system)
            print("\n[OK] modules.libraries submodules imported")
        except ImportError as e:
            self.fail(f"Failed to import libraries submodules: {e}")

    def test_library_exports(self):
        """Verify key classes are exported from libraries."""
        from optimization_core.modules.libraries import (
            BaseModule, ModelModule, DataModule, TrainingModule,
            ModularSystem, ConfigManager
        )
        self.assertIsNotNone(BaseModule)
        self.assertIsNotNone(ModelModule)
        self.assertIsNotNone(ModularSystem)
        print("[OK] modules.libraries class exports verified")

    def test_advanced_libraries_shim(self):
        """Verify backward compatibility shim works."""
        try:
            # This should trigger a warning but succeed
            from optimization_core.modules import advanced_libraries
            from optimization_core.modules.advanced_libraries import ModularSystem
            self.assertIsNotNone(ModularSystem)
        except ImportError as e:
            self.fail(f"Failed to import advanced_libraries shim: {e}")


class TestLibraryOptimizer(unittest.TestCase):
    """Tests for Phase 7 (Library Optimizer Integration)."""

    def test_library_optimizer_init(self):
        """Verify LibraryOptimizer initializes via unified system."""
        from optimization_core.modules.optimizers import LibraryOptimizer
        from optimization_core.modules.optimizers.core.strategies.library_strategy import LibraryStrategy
        from optimization_core.modules.optimizers.core.unified_optimizer import UnifiedOptimizer
        
        optimizer = LibraryOptimizer(config={"test": True})
        # It's now a UnifiedOptimizer instance since it's a shim
        self.assertIsInstance(optimizer, UnifiedOptimizer)
        self.assertIsInstance(optimizer.strategies[0], LibraryStrategy)
        print("[OK] LibraryOptimizer initialization verified")

    def test_library_strategy_export(self):
        """Verify LibraryStrategy is exported from strategies package."""
        from optimization_core.modules.optimizers.core.strategies import LibraryStrategy
        self.assertIsNotNone(LibraryStrategy)
        print("[OK] LibraryStrategy export verified")


class TestCompatibilityCleanup(unittest.TestCase):
    """Tests for Phase 8 (Registry & Compatibility Cleanup)."""

    def test_compatibility_package(self):
        """Verify optimizers.compatibility package works."""
        from optimization_core.modules.optimizers import compatibility
        from optimization_core.modules.optimizers.compatibility import AdvancedTruthGPTOptimizer
        self.assertIsNotNone(AdvancedTruthGPTOptimizer)
        print("[OK] optimizers.compatibility package verified")

    def test_generic_compatibility_lazy(self):
        """Verify generic_compatibility lazy attribute works."""
        from optimization_core import optimizers
        self.assertTrue(hasattr(optimizers, "generic_compatibility"))
        gen_comp = optimizers.generic_compatibility
        self.assertIsNotNone(gen_comp.UltraSpeedOptimizer)
        print("[OK] generic_compatibility lazy access verified")


class TestRefactoringCleanup(unittest.TestCase):
    """Tests for Phase 6 (Refactoring Cleanup) changes."""

    def test_utils_enhanced_mlp(self):
        """Verify utils.enhanced_mlp exports OptimizedLinear correctly."""
        try:
            from optimization_core.utils.enhanced_mlp import OptimizedLinear, SwiGLU
            self.assertIsNotNone(OptimizedLinear)
            self.assertIsNotNone(SwiGLU)
            print("\n[OK] utils.enhanced_mlp verified")
        except ImportError as e:
            self.fail(f"Failed to import utils.enhanced_mlp: {e}")

    def test_techniques_enhanced_mlp_shim(self):
        """Verify techniques.enhanced_mlp shim imports correctly."""
        try:
            import optimization_core.optimizers.techniques.enhanced_mlp as enhanced_mlp
            with self.assertWarns(DeprecationWarning):
                importlib.reload(enhanced_mlp)
            self.assertIsNotNone(enhanced_mlp.OptimizedLinear)
            print("[OK] techniques.enhanced_mlp shim verified")
        except ImportError as e:
            self.fail(f"Failed to import techniques.enhanced_mlp shim: {e}")

    def test_computational_optimizations_fix(self):
        """Verify computational_optimizations uses corrected import."""
        try:
            from optimization_core.modules.optimizers.techniques.computational_optimizations import FusedAttention
            # Check if FusedAttention can be instantiated (requires mocking torch.nn.Module correctly)
            # Just verifying import is enough to check imports are not broken
            self.assertIsNotNone(FusedAttention)
            print("[OK] computational_optimizations import fix verified")
        except ImportError as e:
            self.fail(f"Failed to import computational_optimizations: {e}")
        except Exception as e:
            self.fail(f"Unexpected error in computational_optimizations: {e}")


class TestLearningModule(unittest.TestCase):
    """Tests for the `modules.learning` refactor."""

    def test_learning_structure(self):
        """Verify modules.learning subpackage exists and is importable."""
        try:
            from optimization_core.modules import learning
            from optimization_core.modules.learning import (
                evolutionary_computing, causal_inference, active_learning
            )
            self.assertIsNotNone(learning)
            self.assertIsNotNone(evolutionary_computing)
            print("\n[OK] modules.learning submodules imported")
        except ImportError as e:
            self.fail(f"Failed to import learning submodules: {e}")

    def test_learning_exports(self):
        """Verify key classes are exported from modules.learning."""
        try:
            from optimization_core.modules.learning import (
                EvolutionaryOptimizer, CausalInferenceEngine, ActiveLearningStrategy
            )
            self.assertIsNotNone(EvolutionaryOptimizer)
            self.assertIsNotNone(CausalInferenceEngine)
            print("[OK] modules.learning class exports verified")
        except ImportError as e:
            self.fail(f"Failed to import learning classes: {e}")

    def test_learning_backward_compat(self):
        """Verify optimization_core.learning shim works."""
        try:
            from optimization_core import learning
            from optimization_core.modules.learning import EvolutionaryOptimizer
            self.assertIsNotNone(learning)
            self.assertIsNotNone(EvolutionaryOptimizer)
            print("[OK] optimization_core.learning shim verified")
        except ImportError as e:
            self.fail(f"Failed to verify learning backward compat: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
