"""
Documentation Integration for Code

This module provides decorators and utilities to integrate official
documentation references directly into code.
"""

import functools
import inspect
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path

def doc_reference(library: str, section: str, url: str = None):
    """
    Decorator to add documentation reference to functions and classes.
    
    Args:
        library: The library name (e.g., 'pytorch', 'transformers')
        section: The documentation section
        url: Optional specific URL
    """
    def decorator(func_or_class):
        # Add documentation reference to the object
        func_or_class.__doc_reference__ = {
            'library': library,
            'section': section,
            'url': url
        }
        
        # Add to docstring if it exists
        if hasattr(func_or_class, '__doc__') and func_or_class.__doc__:
            doc_ref = f"\n\n📚 Documentation: {library} - {section}"
            if url:
                doc_ref += f" ({url})"
            func_or_class.__doc__ += doc_ref
        
        return func_or_class
    return decorator

def best_practice(rule_id: str, description: str, suggestion: str = None):
    """
    Decorator to mark functions/classes as following best practices.
    
    Args:
        rule_id: The best practice rule ID
        description: Description of the best practice
        suggestion: Optional suggestion for improvement
    """
    def decorator(func_or_class):
        # Add best practice reference
        if not hasattr(func_or_class, '__best_practices__'):
            func_or_class.__best_practices__ = []
        
        func_or_class.__best_practices__.append({
            'rule_id': rule_id,
            'description': description,
            'suggestion': suggestion
        })
        
        return func_or_class
    return decorator

class DocumentationMixin:
    """Mixin class to add documentation capabilities to classes."""
    
    def get_documentation_reference(self) -> Optional[Dict[str, str]]:
        """Get documentation reference for this class."""
        if hasattr(self.__class__, '__doc_reference__'):
            return self.__class__.__doc_reference__
        return None
    
    def get_best_practices(self) -> List[Dict[str, str]]:
        """Get best practices applied to this class."""
        if hasattr(self.__class__, '__best_practices__'):
            return self.__class__.__best_practices__
        return []
    
    def print_documentation_info(self):
        """Print documentation information for this class."""
        doc_ref = self.get_documentation_reference()
        best_practices = self.get_best_practices()
        
        print(f"📚 Documentation for {self.__class__.__name__}")
        print("=" * 50)
        
        if doc_ref:
            print(f"Library: {doc_ref['library']}")
            print(f"Section: {doc_ref['section']}")
            if doc_ref.get('url'):
                print(f"URL: {doc_ref['url']}")
        
        if best_practices:
            print(f"\n✅ Best Practices Applied:")
            for practice in best_practices:
                print(f"  - {practice['description']}")
                if practice.get('suggestion'):
                    print(f"    Suggestion: {practice['suggestion']}")

# Example usage in actual code
@doc_reference("pytorch", "Model Creation", "https://pytorch.org/docs/stable/nn.html")
@best_practice("PY001", "Proper model initialization", "Use __init__ method for model setup")
class PyTorchModel:
    """Example PyTorch model following best practices."""
    
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super().__init__()
        self.linear1 = torch.nn.Linear(input_size, hidden_size)
        self.linear2 = torch.nn.Linear(hidden_size, output_size)
        self.relu = torch.nn.ReLU()
    
    def forward(self, x):
        x = self.relu(self.linear1(x))
        x = self.linear2(x)
        return x

@doc_reference("transformers", "Model Loading", "https://huggingface.co/docs/transformers/main_classes/model")
@best_practice("TF004", "Proper model loading", "Use AutoModel.from_pretrained() with error handling")
def load_transformer_model(model_name: str):
    """Load a transformer model following best practices."""
    try:
        from transformers import AutoModel, AutoTokenizer
        
        model = AutoModel.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        return model, tokenizer
    except Exception as e:
        raise RuntimeError(f"Failed to load model {model_name}: {e}")

@doc_reference("gradio", "Interface Creation", "https://gradio.app/docs/interface")
@best_practice("GR001", "Input validation", "Add proper validation to input components")
def create_gradio_interface():
    """Create a Gradio interface following best practices."""
    import gradio as gr
    
    def process_input(text: str) -> str:
        if not text.strip():
            return "Please provide some input text."
        return f"Processed: {text}"
    
    interface = gr.Interface(
        fn=process_input,
        inputs=gr.Textbox(label="Input Text", placeholder="Enter text here..."),
        outputs=gr.Textbox(label="Output"),
        title="Text Processing Interface",
        description="Enter text to process it following best practices."
    )
    
    return interface

# Documentation integration utilities
def get_function_documentation(func: Callable) -> Dict[str, Any]:
    """Get documentation information for a function."""
    doc_info = {
        'name': func.__name__,
        'docstring': func.__doc__,
        'doc_reference': getattr(func, '__doc_reference__', None),
        'best_practices': getattr(func, '__best_practices__', [])
    }
    return doc_info

def get_class_documentation(cls: type) -> Dict[str, Any]:
    """Get documentation information for a class."""
    doc_info = {
        'name': cls.__name__,
        'docstring': cls.__doc__,
        'doc_reference': getattr(cls, '__doc_reference__', None),
        'best_practices': getattr(cls, '__best_practices__', [])
    }
    return doc_info

def print_documentation_summary(module_path: str):
    """Print documentation summary for all documented items in a module."""
    import importlib
    import inspect
    
    try:
        module = importlib.import_module(module_path)
        
        print(f"📚 Documentation Summary for {module_path}")
        print("=" * 60)
        
        # Check functions
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if hasattr(obj, '__doc_reference__') or hasattr(obj, '__best_practices__'):
                doc_info = get_function_documentation(obj)
                print(f"\n🔧 Function: {doc_info['name']}")
                if doc_info['doc_reference']:
                    print(f"   📖 Doc: {doc_info['doc_reference']['library']} - {doc_info['doc_reference']['section']}")
                if doc_info['best_practices']:
                    print(f"   ✅ Best Practices: {len(doc_info['best_practices'])} applied")
        
        # Check classes
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if hasattr(obj, '__doc_reference__') or hasattr(obj, '__best_practices__'):
                doc_info = get_class_documentation(obj)
                print(f"\n🏗️  Class: {doc_info['name']}")
                if doc_info['doc_reference']:
                    print(f"   📖 Doc: {doc_info['doc_reference']['library']} - {doc_info['doc_reference']['section']}")
                if doc_info['best_practices']:
                    print(f"   ✅ Best Practices: {len(doc_info['best_practices'])} applied")
                    
    except ImportError as e:
        print(f"❌ Could not import module {module_path}: {e}")

def main():
    """Main function to demonstrate documentation integration."""
    print("📚 Documentation Integration Examples")
    print("=" * 50)
    
    # Example 1: PyTorch Model
    print("\n1️⃣ PyTorch Model Example:")
    model = PyTorchModel(10, 20, 5)
    model.print_documentation_info()
    
    # Example 2: Transformer Loading
    print("\n2️⃣ Transformer Loading Example:")
    doc_info = get_function_documentation(load_transformer_model)
    print(f"Function: {doc_info['name']}")
    if doc_info['doc_reference']:
        print(f"Documentation: {doc_info['doc_reference']['library']} - {doc_info['doc_reference']['section']}")
    if doc_info['best_practices']:
        print(f"Best Practices: {len(doc_info['best_practices'])} applied")
    
    # Example 3: Gradio Interface
    print("\n3️⃣ Gradio Interface Example:")
    doc_info = get_function_documentation(create_gradio_interface)
    print(f"Function: {doc_info['name']}")
    if doc_info['doc_reference']:
        print(f"Documentation: {doc_info['doc_reference']['library']} - {doc_info['doc_reference']['section']}")
    if doc_info['best_practices']:
        print(f"Best Practices: {len(doc_info['best_practices'])} applied")

if __name__ == "__main__":
    main()
