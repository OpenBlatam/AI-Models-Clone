"""
Documentation Helper for ML/AI Projects

This module provides utilities to access and integrate official documentation
into the development workflow.
"""

import webbrowser
import requests
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging

@dataclass
class DocReference:
    """Reference to a specific documentation section."""
    library: str
    section: str
    url: str
    description: str
    version: str
    last_updated: str

class DocumentationHelper:
    """Helper class for accessing and managing documentation references."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.doc_cache = {}
        self.api_cache = {}
        
        # Load documentation references
        self.doc_references = self._load_doc_references()
    
    def _load_doc_references(self) -> Dict[str, List[DocReference]]:
        """Load documentation references from configuration."""
        references = {
            "pytorch": [
                DocReference(
                    library="PyTorch",
                    section="Model Creation",
                    url="https://pytorch.org/docs/stable/nn.html",
                    description="Creating neural network models",
                    version="2.0.0+",
                    last_updated="2024-01-01"
                ),
                DocReference(
                    library="PyTorch",
                    section="Training Loop",
                    url="https://pytorch.org/tutorials/beginner/basics/optimization_tutorial.html",
                    description="Basic training loop implementation",
                    version="2.0.0+",
                    last_updated="2024-01-01"
                ),
                DocReference(
                    library="PyTorch",
                    section="Data Loading",
                    url="https://pytorch.org/docs/stable/data.html",
                    description="Data loading and preprocessing",
                    version="2.0.0+",
                    last_updated="2024-01-01"
                ),
                DocReference(
                    library="PyTorch",
                    section="Distributed Training",
                    url="https://pytorch.org/tutorials/beginner/dist_overview.html",
                    description="Multi-GPU and distributed training",
                    version="2.0.0+",
                    last_updated="2024-01-01"
                ),
                DocReference(
                    library="PyTorch",
                    section="Performance Optimization",
                    url="https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html",
                    description="Performance tuning and optimization",
                    version="2.0.0+",
                    last_updated="2024-01-01"
                )
            ],
            "transformers": [
                DocReference(
                    library="Transformers",
                    section="Model Loading",
                    url="https://huggingface.co/docs/transformers/main_classes/model",
                    description="Loading pre-trained models",
                    version="4.30.0+",
                    last_updated="2024-01-01"
                ),
                DocReference(
                    library="Transformers",
                    section="Pipelines",
                    url="https://huggingface.co/docs/transformers/main_classes/pipelines",
                    description="Using pre-built pipelines",
                    version="4.30.0+",
                    last_updated="2024-01-01"
                ),
                DocReference(
                    library="Transformers",
                    section="Custom Training",
                    url="https://huggingface.co/docs/transformers/training",
                    description="Fine-tuning models",
                    version="4.30.0+",
                    last_updated="2024-01-01"
                ),
                DocReference(
                    library="Transformers",
                    section="Tokenization",
                    url="https://huggingface.co/docs/transformers/main_classes/tokenizer",
                    description="Text tokenization",
                    version="4.30.0+",
                    last_updated="2024-01-01"
                )
            ],
            "diffusers": [
                DocReference(
                    library="Diffusers",
                    section="Pipeline Usage",
                    url="https://huggingface.co/docs/diffusers/using-diffusers/pipeline_overview",
                    description="Using diffusion pipelines",
                    version="0.20.0+",
                    last_updated="2024-01-01"
                ),
                DocReference(
                    library="Diffusers",
                    section="Custom Training",
                    url="https://huggingface.co/docs/diffusers/training/overview",
                    description="Training custom diffusion models",
                    version="0.20.0+",
                    last_updated="2024-01-01"
                ),
                DocReference(
                    library="Diffusers",
                    section="Schedulers",
                    url="https://huggingface.co/docs/diffusers/api/schedulers/overview",
                    description="Noise scheduling",
                    version="0.20.0+",
                    last_updated="2024-01-01"
                )
            ],
            "gradio": [
                DocReference(
                    library="Gradio",
                    section="Interface Creation",
                    url="https://gradio.app/docs/interface",
                    description="Creating Gradio interfaces",
                    version="3.40.0+",
                    last_updated="2024-01-01"
                ),
                DocReference(
                    library="Gradio",
                    section="Blocks",
                    url="https://gradio.app/docs/blocks",
                    description="Using Gradio Blocks",
                    version="3.40.0+",
                    last_updated="2024-01-01"
                ),
                DocReference(
                    library="Gradio",
                    section="Components",
                    url="https://gradio.app/docs/components",
                    description="Available components",
                    version="3.40.0+",
                    last_updated="2024-01-01"
                ),
                DocReference(
                    library="Gradio",
                    section="Events",
                    url="https://gradio.app/docs/events",
                    description="Handling events",
                    version="3.40.0+",
                    last_updated="2024-01-01"
                )
            ]
        }
        
        return references
    
    def get_doc_reference(self, library: str, section: str) -> Optional[DocReference]:
        """Get documentation reference for a specific library and section."""
        if library.lower() in self.doc_references:
            for ref in self.doc_references[library.lower()]:
                if ref.section.lower() == section.lower():
                    return ref
        return None
    
    def open_documentation(self, library: str, section: str = None):
        """Open documentation in web browser."""
        try:
            if section:
                ref = self.get_doc_reference(library, section)
                if ref:
                    webbrowser.open(ref.url)
                    self.logger.info(f"Opened {library} {section} documentation")
                else:
                    self.logger.warning(f"No documentation reference found for {library} {section}")
            else:
                # Open main documentation page
                main_urls = {
                    "pytorch": "https://pytorch.org/docs/stable/",
                    "transformers": "https://huggingface.co/docs/transformers/",
                    "diffusers": "https://huggingface.co/docs/diffusers/",
                    "gradio": "https://gradio.app/docs/"
                }
                
                if library.lower() in main_urls:
                    webbrowser.open(main_urls[library.lower()])
                    self.logger.info(f"Opened {library} main documentation")
                else:
                    self.logger.error(f"Unknown library: {library}")
                    
        except Exception as e:
            self.logger.error(f"Error opening documentation: {e}")
    
    def search_documentation(self, query: str, library: str = None) -> List[DocReference]:
        """Search documentation references."""
        results = []
        
        libraries_to_search = [library.lower()] if library else self.doc_references.keys()
        
        for lib in libraries_to_search:
            if lib in self.doc_references:
                for ref in self.doc_references[lib]:
                    if (query.lower() in ref.section.lower() or 
                        query.lower() in ref.description.lower()):
                        results.append(ref)
        
        return results
    
    def get_api_info(self, library: str, class_name: str = None, method_name: str = None) -> Dict[str, Any]:
        """Get API information for a specific class or method."""
        cache_key = f"{library}_{class_name}_{method_name}"
        
        if cache_key in self.api_cache:
            return self.api_cache[cache_key]
        
        # This would typically fetch from the actual API documentation
        # For now, we'll return a placeholder structure
        api_info = {
            "library": library,
            "class": class_name,
            "method": method_name,
            "documentation_url": self._get_api_url(library, class_name, method_name),
            "parameters": [],
            "returns": None,
            "examples": []
        }
        
        self.api_cache[cache_key] = api_info
        return api_info
    
    def _get_api_url(self, library: str, class_name: str = None, method_name: str = None) -> str:
        """Generate API documentation URL."""
        base_urls = {
            "pytorch": "https://pytorch.org/docs/stable/",
            "transformers": "https://huggingface.co/docs/transformers/",
            "diffusers": "https://huggingface.co/docs/diffusers/",
            "gradio": "https://gradio.app/docs/"
        }
        
        if library.lower() not in base_urls:
            return ""
        
        base_url = base_urls[library.lower()]
        
        if class_name:
            if method_name:
                return f"{base_url}{class_name}.html#{class_name}.{method_name}"
            else:
                return f"{base_url}{class_name}.html"
        else:
            return base_url
    
    def generate_doc_summary(self, library: str) -> str:
        """Generate a summary of available documentation for a library."""
        if library.lower() not in self.doc_references:
            return f"No documentation references found for {library}"
        
        refs = self.doc_references[library.lower()]
        
        summary = f"📚 {library} Documentation Summary\n"
        summary += "=" * 50 + "\n\n"
        
        for ref in refs:
            summary += f"🔗 {ref.section}\n"
            summary += f"   Description: {ref.description}\n"
            summary += f"   URL: {ref.url}\n"
            summary += f"   Version: {ref.version}\n"
            summary += f"   Updated: {ref.last_updated}\n\n"
        
        return summary
    
    def check_version_compatibility(self, library: str, current_version: str) -> Dict[str, Any]:
        """Check if current version is compatible with documentation."""
        if library.lower() not in self.doc_references:
            return {"compatible": False, "message": f"Unknown library: {library}"}
        
        refs = self.doc_references[library.lower()]
        
        # Extract minimum version from references
        min_versions = []
        for ref in refs:
            version_match = re.search(r'(\d+\.\d+\.\d+)', ref.version)
            if version_match:
                min_versions.append(version_match.group(1))
        
        if not min_versions:
            return {"compatible": True, "message": "No version requirements found"}
        
        # Compare versions (simplified comparison)
        min_version = min(min_versions)
        
        # This is a simplified version comparison
        # In practice, you'd use a proper version comparison library
        try:
            current_parts = [int(x) for x in current_version.split('.')]
            min_parts = [int(x) for x in min_version.split('.')]
            
            compatible = current_parts >= min_parts
            message = f"Current: {current_version}, Minimum: {min_version}"
            
            return {
                "compatible": compatible,
                "message": message,
                "current_version": current_version,
                "min_version": min_version
            }
        except Exception as e:
            return {
                "compatible": False,
                "message": f"Error comparing versions: {e}"
            }

def main():
    """Main function to demonstrate documentation helper usage."""
    helper = DocumentationHelper()
    
    # Print documentation summary for PyTorch
    print(helper.generate_doc_summary("pytorch"))
    
    # Search for training-related documentation
    results = helper.search_documentation("training")
    print(f"\nFound {len(results)} training-related documentation references:")
    for ref in results:
        print(f"  - {ref.library}: {ref.section}")

if __name__ == "__main__":
    main()
