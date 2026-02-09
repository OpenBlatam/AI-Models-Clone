
import sys
import os

# Add the project root to sys.path so we can import from agents.backend...
# Assuming we run this from c:\blatam-academy
sys.path.append(r"c:\blatam-academy")

try:
    print("Attempting to import WebGenPipeline...")
    from agents.backend.onyx.server.features.lovable.web_gen_system.pipeline import WebGenPipeline
    print("Import successful.")

    print("Instantiating WebGenPipeline...")
    pipeline = WebGenPipeline()
    print("WebGenPipeline instantiated successfully.")
    
    # Check if agents are loaded
    print(f"WebVoyager: {pipeline.voyager_agent}")
    print(f"MobileAgent: {pipeline.mobile_agent}")
    print(f"FerretUI: {pipeline.ferret_agent}")
    
    if pipeline.voyager_agent is None:
        print("ERROR: WebVoyager agent is None")
        sys.exit(1)
        
    print("All checks passed.")
    
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
