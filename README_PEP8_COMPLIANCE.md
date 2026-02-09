# PEP 8 Compliance Guide

This guide ensures all Python code in the project follows PEP 8 style guidelines for consistency, readability, and maintainability.

## Quick Start

### 1. Install PEP 8 Tools

```bash
# Install required tools
pip install -r requirements_pep8.txt

# Or install individually
pip install black flake8 isort mypy pre-commit
```

### 2. Apply PEP 8 Fixes

```bash
# Run the automated fixer
python apply_pep8_fixes.py

# Or run tools individually
black .
isort .
flake8 .
```

### 3. Set Up Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## Tools Overview

### Black - Code Formatter
- Automatically formats code to PEP 8 standards
- Consistent formatting across the codebase
- No configuration needed (opinionated)

```bash
# Format all Python files
black .

# Check formatting without changing files
black --check .

# Format specific file
black my_file.py
```

### isort - Import Sorter
- Sorts and organizes import statements
- Groups imports logically
- Configurable import order

```bash
# Sort imports in all files
isort .

# Check import sorting
isort --check-only .

# Sort specific file
isort my_file.py
```

### flake8 - Linter
- Checks for PEP 8 violations
- Identifies style issues
- Configurable rules

```bash
# Lint all Python files
flake8 .

# Lint specific file
flake8 my_file.py
```

### mypy - Type Checker
- Static type checking
- Catches type-related errors
- Improves code quality

```bash
# Type check all files
mypy .

# Type check specific file
mypy my_file.py
```

## Configuration Files

### pyproject.toml
```toml
[tool.black]
line-length = 79
target-version = ['py38']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 79
multi_line_output = 3

[tool.flake8]
max-line-length = 79
extend-ignore = ["E203", "W503"]
exclude = .git,__pycache__,build,dist
```

### .flake8
```ini
[flake8]
max-line-length = 79
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist,.venv,venv,env
```

### .pre-commit-config.yaml
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

## PEP 8 Rules Summary

### Code Layout
- **Indentation**: 4 spaces (no tabs)
- **Line Length**: Maximum 79 characters
- **Blank Lines**: 2 lines before classes, 1 line before methods
- **Imports**: Grouped and sorted (standard library, third-party, local)

### Naming Conventions
- **Variables/Functions**: `lowercase_with_underscores`
- **Classes**: `CapWords` (PascalCase)
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`
- **Protected**: Single underscore prefix `_protected`
- **Private**: Double underscore prefix `__private`

### Whitespace
- **Operators**: Spaces around operators
- **Commas**: No space before, space after
- **Function Calls**: No space inside parentheses
- **Indexing**: No space inside brackets

### Comments and Docstrings
- **Docstrings**: Triple quotes, Google or NumPy format
- **Comments**: Explain "why" not "what"
- **Type Hints**: Use for all function signatures

## Examples

### Before (Non-PEP 8 Compliant)
```python
import sys,os
from typing import*
import numpy as np
from fastapi import FastAPI

class agi_consciousness_engine:
    def __init__(self):
        self.consciousness_score=95.8
        self.quantum_advantage=10.7
        
    async def process_with_consciousness(self,request):
        start_time=time.perf_counter()
        #process data
        processing_time=(time.perf_counter()-start_time)*1000
        return {"processing_time_ms":processing_time}

def main():
    app=FastAPI()
    engine=agi_consciousness_engine()
    return app
```

### After (PEP 8 Compliant)
```python
import os
import sys
import time
from typing import Dict, Any

import numpy as np
from fastapi import FastAPI


class AGIConsciousnessEngine:
    """AGI consciousness processing engine."""
    
    def __init__(self) -> None:
        """Initialize the AGI consciousness engine."""
        self.consciousness_score: float = 95.8
        self.quantum_advantage: float = 10.7
    
    async def process_with_consciousness(
        self, 
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process content with AGI consciousness.
        
        Args:
            request: The consciousness processing request
            
        Returns:
            Processing results with timing information
        """
        start_time = time.perf_counter()
        
        # Process data with consciousness
        await self._consciousness_analysis(request["content"])
        
        processing_time = (time.perf_counter() - start_time) * 1000
        
        return {
            "processing_time_ms": round(processing_time, 2),
            "consciousness_score": self.consciousness_score
        }
    
    async def _consciousness_analysis(self, content: str) -> None:
        """Perform consciousness-level analysis."""
        # Implementation here
        pass


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(title="AGI Consciousness API")
    engine = AGIConsciousnessEngine()
    
    return app


if __name__ == "__main__":
    app = create_app()
```

## IDE Integration

### VS Code
Install these extensions:
- Python
- Black Formatter
- isort
- Flake8

Add to settings.json:
```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### PyCharm
1. Go to Settings → Tools → External Tools
2. Add Black, isort, and flake8 as external tools
3. Configure file watchers for automatic formatting

### Vim/NeoVim
Use plugins like:
- ale (for linting)
- black (for formatting)
- isort (for import sorting)

## CI/CD Integration

### GitHub Actions
```yaml
name: PEP 8 Compliance

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install black flake8 isort mypy
      - run: black --check .
      - run: flake8 .
      - run: isort --check-only .
      - run: mypy .
```

### GitLab CI
```yaml
pep8_check:
  stage: test
  image: python:3.9
  script:
    - pip install black flake8 isort mypy
    - black --check .
    - flake8 .
    - isort --check-only .
    - mypy .
```

## Common Issues and Solutions

### Line Length Exceeded
```python
# Bad
very_long_variable_name = some_very_long_function_call_with_many_parameters(param1, param2, param3, param4, param5)

# Good
very_long_variable_name = (
    some_very_long_function_call_with_many_parameters(
        param1, param2, param3, param4, param5
    )
)
```

### Import Organization
```python
# Bad
from fastapi import FastAPI
import os
import sys
from .models import User
import numpy as np

# Good
import os
import sys

import numpy as np
from fastapi import FastAPI

from .models import User
```

### Function Signatures
```python
# Bad
def process_data(data,config=None,timeout=30,retries=3):
    pass

# Good
def process_data(
    data: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
    retries: int = 3
) -> Dict[str, Any]:
    """Process data with configuration options.
    
    Args:
        data: Data to process
        config: Optional configuration
        timeout: Timeout in seconds
        retries: Number of retry attempts
        
    Returns:
        Processed data
    """
    pass
```

## Best Practices

### 1. Use Type Hints
```python
from typing import List, Dict, Optional, Union

def process_items(
    items: List[str],
    config: Optional[Dict[str, Any]] = None
) -> Union[List[str], None]:
    pass
```

### 2. Write Descriptive Names
```python
# Good
def calculate_user_total_score(user_data: Dict[str, Any]) -> float:
    pass

# Bad
def calc_score(data: Dict[str, Any]) -> float:
    pass
```

### 3. Use Docstrings
```python
def complex_algorithm(data: List[float]) -> float:
    """Calculate the weighted average of the dataset.
    
    This algorithm uses a sophisticated weighting scheme that
    gives more importance to recent data points while
    maintaining statistical validity.
    
    Args:
        data: List of numerical values to process
        
    Returns:
        Weighted average of the data
        
    Raises:
        ValueError: If data list is empty
    """
    if not data:
        raise ValueError("Data list cannot be empty")
    
    # Implementation here
    pass
```

### 4. Handle Exceptions Properly
```python
try:
    with open(filename, 'r') as file:
        data = file.read()
except FileNotFoundError:
    logger.error(f"File {filename} not found")
    raise
except PermissionError:
    logger.error(f"Permission denied accessing {filename}")
    raise
```

## Monitoring and Maintenance

### Regular Checks
- Run PEP 8 checks before commits
- Include in CI/CD pipeline
- Regular code reviews for style compliance

### Tools for Monitoring
- **pre-commit**: Automatic checks on commit
- **tox**: Multi-environment testing with style checks
- **coverage**: Code coverage with style integration

### Reporting
Generate style compliance reports:
```bash
# Generate flake8 report
flake8 --format=html --htmldir=flake8-report .

# Generate black diff
black --diff .

# Generate isort diff
isort --diff .
```

## Resources

- [PEP 8 Official Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [flake8 Documentation](https://flake8.pycqa.org/)
- [mypy Documentation](https://mypy.readthedocs.io/)

## Support

For questions or issues with PEP 8 compliance:
1. Check the style guide documentation
2. Run automated tools for suggestions
3. Review examples in this guide
4. Consult with the development team 