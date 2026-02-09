import sys
import os

# Add the project root to the python path
sys.path.append(os.getcwd())

try:
    print("Attempting to import bs4...")
    import bs4
    print(f"Successfully imported bs4: {bs4.__version__}")
except ImportError as e:
    print(f"Failed to import bs4: {e}")

try:
    print("Attempting to import jinja2...")
    import jinja2
    print(f"Successfully imported jinja2: {jinja2.__version__}")
except ImportError as e:
    print(f"Failed to import jinja2: {e}")

try:
    print("Attempting to import WebAccessibilityEnhancer...")
    from agents.backend.onyx.server.features.lovable.web_gen_system.accessibility import WebAccessibilityEnhancer
    print("Successfully imported WebAccessibilityEnhancer")
except ImportError as e:
    print(f"Failed to import WebAccessibilityEnhancer: {e}")
except Exception as e:
    print(f"Error importing WebAccessibilityEnhancer: {e}")
