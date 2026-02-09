
import sys
import os

# Add the script path to sys.path
script_dir = r"c:\blatam-academy\agents\backend\onyx\server\features\Frontier-Model-run-polyglot\scripts\TruthGPT-main"
if script_dir not in sys.path:
    sys.path.append(script_dir)

import optimization_core
from optimization_core.utils.truthgpt_core import OptimizationLevel

def test_imports():
    print("Testing core imports...")
    try:
        from optimization_core.utils import truthgpt_core
        print("✅ optimization_core.utils.truthgpt_core imported successfully.")
    except ImportError as e:
        print(f"❌ Failed to import truthgpt_core: {e}")
        return

    print("\nTesting for purged optimization levels...")
    speculative_levels = ['TRANSCENDENT', 'DIVINE', 'OMNIPOTENT', 'INFINITE', 'ULTIMATE']
    for level in speculative_levels:
        if hasattr(OptimizationLevel, level):
            print(f"❌ OptimizationLevel still has {level}")
        else:
            print(f"✅ OptimizationLevel.{level} is gone.")

    print("\nTesting for purged lazy imports in optimization_core...")
    purged_modules = [
        'CosmicOptimizer', 
        'TranscendentOptimizer', 
        'UltraFastOptimizer', 
        'SupremeTruthGPTOptimizer',
        'AIExtremeOptimizer'
    ]
    for mod in purged_modules:
        try:
            getattr(optimization_core, mod)
            print(f"❌ {mod} is still accessible in optimization_core!")
        except AttributeError:
            print(f"✅ {mod} is correctly missing from optimization_core.")

    print("\nTesting for purged modules in optimization_core.utils.modules...")
    from optimization_core.utils import modules
    purged_utils = ['CosmicEvolutionCompiler', 'DivineWisdomCompiler']
    for mod in purged_utils:
        try:
            getattr(modules, mod)
            print(f"❌ {mod} is still accessible in optimization_core.utils.modules!")
        except AttributeError:
            print(f"✅ {mod} is correctly missing from optimization_core.utils.modules.")

    print("\nVerification Complete.")

if __name__ == "__main__":
    test_imports()
