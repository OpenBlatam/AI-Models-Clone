
import sys
import os

# Add project root to path
sys.path.insert(0, "c:\\blatam-academy")

try:
    print("Attempting to import dermatology_api_modular...")
    from agents.backend.onyx.server.features.dermatology_ai.api import dermatology_api_modular
    print("Import successful!")
    
    # Check if system router is in the list (by inspecting the source code or just assuming success if import worked)
    # Since register_routers is a function called at runtime, we can't easily check the registry without running the app.
    # But successful import means no syntax errors or missing imports.
    
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
