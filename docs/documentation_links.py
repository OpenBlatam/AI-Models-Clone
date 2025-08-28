# docs/documentation_links.py
"""
Official Documentation Links and Resources

This module contains links to official documentation for all major libraries
used in the Enhanced AI Model Demos System.
"""

# =============================================================================
# CORE LIBRARIES
# =============================================================================

PYTORCH_DOCS = {
    "main": "https://pytorch.org/docs/stable/",
    "tutorials": "https://pytorch.org/tutorials/",
    "examples": "https://github.com/pytorch/examples",
    "api_reference": "https://pytorch.org/docs/stable/torch.html",
    "installation": "https://pytorch.org/get-started/locally/",
    "performance": "https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html",
    "distributed": "https://pytorch.org/tutorials/beginner/dist_overview.html",
    "mobile": "https://pytorch.org/mobile/home/",
    "production": "https://pytorch.org/tutorials/recipes/recipes/production_deployment.html",
    "best_practices": "https://pytorch.org/tutorials/recipes/recipes/best_practices.html"
}

TRANSFORMERS_DOCS = {
    "main": "https://huggingface.co/docs/transformers/",
    "quicktour": "https://huggingface.co/docs/transformers/quicktour",
    "task_summary": "https://huggingface.co/docs/transformers/task_summary",
    "model_doc": "https://huggingface.co/docs/transformers/model_doc",
    "pipeline": "https://huggingface.co/docs/transformers/main_classes/pipelines",
    "training": "https://huggingface.co/docs/transformers/training",
    "custom_datasets": "https://huggingface.co/docs/transformers/custom_datasets",
    "performance": "https://huggingface.co/docs/transformers/performance",
    "model_sharing": "https://huggingface.co/docs/transformers/model_sharing",
    "examples": "https://github.com/huggingface/transformers/tree/main/examples"
}

DIFFUSERS_DOCS = {
    "main": "https://huggingface.co/docs/diffusers/",
    "quicktour": "https://huggingface.co/docs/diffusers/quicktour",
    "api": "https://huggingface.co/docs/diffusers/api",
    "training": "https://huggingface.co/docs/diffusers/training/overview",
    "custom_pipeline": "https://huggingface.co/docs/diffusers/using-diffusers/custom_pipeline",
    "schedulers": "https://huggingface.co/docs/diffusers/api/schedulers/overview",
    "models": "https://huggingface.co/docs/diffusers/api/models/overview",
    "examples": "https://github.com/huggingface/diffusers/tree/main/examples"
}

GRADIO_DOCS = {
    "main": "https://gradio.app/docs/",
    "quickstart": "https://gradio.app/quickstart/",
    "interface": "https://gradio.app/docs/interface",
    "blocks": "https://gradio.app/docs/blocks",
    "components": "https://gradio.app/docs/components",
    "events": "https://gradio.app/docs/events",
    "theming": "https://gradio.app/docs/theming",
    "deployment": "https://gradio.app/docs/deployment",
    "examples": "https://gradio.app/docs/examples",
    "troubleshooting": "https://gradio.app/docs/troubleshooting"
}

# =============================================================================
# ADDITIONAL LIBRARIES
# =============================================================================

NUMPY_DOCS = {
    "main": "https://numpy.org/doc/",
    "user_guide": "https://numpy.org/doc/stable/user/index.html",
    "reference": "https://numpy.org/doc/stable/reference/",
    "tutorials": "https://numpy.org/doc/stable/user/quickstart.html"
}

SCIKIT_LEARN_DOCS = {
    "main": "https://scikit-learn.org/stable/",
    "user_guide": "https://scikit-learn.org/stable/user_guide.html",
    "api": "https://scikit-learn.org/stable/modules/classes.html",
    "tutorials": "https://scikit-learn.org/stable/tutorial/index.html"
}

PLOTLY_DOCS = {
    "main": "https://plotly.com/python/",
    "graph_objects": "https://plotly.com/python/graph-objects/",
    "express": "https://plotly.com/python/plotly-express/",
    "subplots": "https://plotly.com/python/subplots/"
}

# =============================================================================
# VERSION TRACKING
# =============================================================================

def get_latest_versions():
    """Get latest versions of core libraries."""
    import requests
    import json
    
    versions = {}
    
    try:
        # PyPI API for version info
        pypi_url = "https://pypi.org/pypi/{}/json"
        
        libraries = [
            "torch", "transformers", "diffusers", "gradio",
            "numpy", "scikit-learn", "plotly"
        ]
        
        for lib in libraries:
            try:
                response = requests.get(pypi_url.format(lib))
                if response.status_code == 200:
                    data = response.json()
                    versions[lib] = data['info']['version']
            except Exception as e:
                print(f"Error getting version for {lib}: {e}")
                
    except Exception as e:
        print(f"Error fetching versions: {e}")
    
    return versions

def print_documentation_links():
    """Print all documentation links."""
    print("📚 Official Documentation Links")
    print("=" * 50)
    
    for lib_name, docs in [
        ("PyTorch", PYTORCH_DOCS),
        ("Transformers", TRANSFORMERS_DOCS),
        ("Diffusers", DIFFUSERS_DOCS),
        ("Gradio", GRADIO_DOCS)
    ]:
        print(f"\n🔗 {lib_name}")
        print("-" * 30)
        for doc_type, url in docs.items():
            print(f"  {doc_type:15}: {url}")
    
    print(f"\n📦 Latest Versions")
    print("-" * 30)
    versions = get_latest_versions()
    for lib, version in versions.items():
        print(f"  {lib:15}: {version}")

if __name__ == "__main__":
    print_documentation_links()
