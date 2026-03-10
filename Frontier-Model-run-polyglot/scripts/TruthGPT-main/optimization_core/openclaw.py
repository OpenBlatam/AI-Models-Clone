"""
OpenClaw Compatibility Layer for TruthGPT.
Allows users to 'import openclaw' and use the same high-level API.
"""

from .truthgpt import api as _api

# Alias for the main API instance
api = _api

# Re-export key methods for direct access if needed
ask = _api.ask
list_papers = _api.list_papers
get_paper_info = _api.get_paper_info
apply_paper = _api.apply_paper

__all__ = ["api", "ask", "list_papers", "get_paper_info", "apply_paper"]
