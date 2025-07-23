# PEP 8 Style Guide for Python Code

## Overview
This document outlines PEP 8 compliance requirements for the Python codebase, ensuring consistency, readability, and maintainability.

## Core PEP 8 Rules

### 1. Code Layout

#### Indentation
- Use 4 spaces per indentation level (not tabs)
- Continuation lines should align with opening delimiter or use 4-space hanging indent

```python
# Good
def long_function_name(
    var_one,
    var_two,
    var_three
):
    print(var_one)

# Good - hanging indent
def long_function_name(
        var_one, var_two,
        var_three):
    print(var_one)
```

#### Line Length
- Maximum 79 characters for code lines
- Maximum 72 characters for docstrings/comments
- Use parentheses for line continuation

```python
# Good
long_variable_name = (
    some_very_long_expression +
    another_expression
)

# Bad
long_variable_name = some_very_long_expression + another_expression
```

#### Imports
- Group imports in this order:
  1. Standard library imports
  2. Third-party imports
  3. Local application imports
- Separate groups with blank lines
- Use absolute imports over relative imports

```python
# Good
import os
import sys
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI

from .models import User
from .utils import helper_function
```

### 2. Whitespace

#### Around Operators
```python
# Good
x = 1 + 2
y = x * 3

# Bad
x=1+2
y=x*3
```

#### Function and Class Definitions
```python
# Good
class MyClass:
    """Class docstring."""
    
    def __init__(self):
        """Initialize the class."""
        pass
    
    def my_method(self):
        """Method docstring."""
        pass


def my_function():
    """Function docstring."""
    pass
```

#### Inside Parentheses, Brackets, Braces
```python
# Good
spam(ham[1], {eggs: 2})
foo = (0,)

# Bad
spam( ham[ 1 ], { eggs: 2 } )
foo = (0, )
```

### 3. Naming Conventions

#### Variables and Functions
- Use `lowercase_with_underscores` for variables and functions
- Use descriptive names

```python
# Good
user_name = "john_doe"
def calculate_total_price():
    pass

# Bad
userName = "john_doe"
def calc():
    pass
```

#### Classes
- Use `CapWords` (PascalCase) for class names

```python
# Good
class UserAccount:
    pass

class DatabaseConnection:
    pass

# Bad
class userAccount:
    pass

class database_connection:
    pass
```

#### Constants
- Use `UPPERCASE_WITH_UNDERSCORES` for constants

```python
# Good
MAX_CONNECTIONS = 100
DEFAULT_TIMEOUT = 30

# Bad
maxConnections = 100
default_timeout = 30
```

#### Protected and Private
- Use single underscore prefix for protected members
- Use double underscore prefix for private members

```python
class MyClass:
    def __init__(self):
        self._protected_var = 1
        self.__private_var = 2
    
    def _protected_method(self):
        pass
    
    def __private_method(self):
        pass
```

### 4. Comments and Docstrings

#### Docstrings
- Use triple quotes for docstrings
- Follow Google or NumPy docstring format
- Include type hints

```python
def calculate_area(length: float, width: float) -> float:
    """Calculate the area of a rectangle.
    
    Args:
        length: The length of the rectangle
        width: The width of the rectangle
        
    Returns:
        The area of the rectangle
        
    Raises:
        ValueError: If length or width is negative
    """
    if length < 0 or width < 0:
        raise ValueError("Length and width must be positive")
    return length * width
```

#### Comments
- Use comments sparingly, prefer self-documenting code
- Write comments that explain "why" not "what"
- Keep comments up to date

```python
# Good - explains why
# Skip weekends to avoid business logic conflicts
if day.weekday() >= 5:
    continue

# Bad - explains what is obvious
# Check if day is weekend
if day.weekday() >= 5:
    continue
```

### 5. Type Hints

#### Function Signatures
- Use type hints for all function parameters and return values
- Use `Optional[T]` for parameters that can be `None`
- Use `Union[T1, T2]` or `T1 | T2` for multiple types

```python
from typing import Optional, Union, List, Dict, Any

def process_user_data(
    user_id: int,
    data: Dict[str, Any],
    timeout: Optional[float] = None
) -> Union[Dict[str, Any], None]:
    """Process user data with optional timeout."""
    pass
```

#### Variable Annotations
```python
# Good
user_count: int = 0
user_names: List[str] = []
config: Dict[str, Any] = {}

# Bad
user_count = 0  # No type hint
```

### 6. Error Handling

#### Exception Handling
- Use specific exceptions, not bare `except:`
- Include meaningful error messages
- Use context managers when appropriate

```python
# Good
try:
    with open(filename, 'r') as file:
        data = file.read()
except FileNotFoundError:
    logger.error(f"File {filename} not found")
    raise
except PermissionError:
    logger.error(f"Permission denied accessing {filename}")
    raise

# Bad
try:
    data = open(filename).read()
except:
    pass
```

### 7. Performance and Best Practices

#### List Comprehensions
- Use list comprehensions for simple transformations
- Use generator expressions for large datasets

```python
# Good
squares = [x**2 for x in range(10)]
even_squares = [x**2 for x in range(10) if x % 2 == 0]

# For large datasets
squares_gen = (x**2 for x in range(1000000))
```

#### Context Managers
```python
# Good
with open('file.txt', 'r') as file:
    content = file.read()

# Bad
file = open('file.txt', 'r')
content = file.read()
file.close()
```

### 8. Async/Await Patterns

#### Async Function Definitions
```python
# Good
async def fetch_data(url: str) -> Dict[str, Any]:
    """Fetch data from URL asynchronously."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Bad
def fetch_data(url):  # Missing async
    pass
```

#### Async Context Managers
```python
# Good
async with aiofiles.open(filename, 'r') as file:
    content = await file.read()

# Bad
file = await aiofiles.open(filename, 'r')
content = await file.read()
await file.close()
```

## Code Examples

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

from .models import ConsciousnessRequest


class AGIConsciousnessEngine:
    """AGI consciousness processing engine."""
    
    def __init__(self) -> None:
        """Initialize the AGI consciousness engine."""
        self.consciousness_score: float = 95.8
        self.quantum_advantage: float = 10.7
    
    async def process_with_consciousness(
        self, 
        request: ConsciousnessRequest
    ) -> Dict[str, Any]:
        """Process content with AGI consciousness.
        
        Args:
            request: The consciousness processing request
            
        Returns:
            Processing results with timing information
        """
        start_time = time.perf_counter()
        
        # Process data with consciousness
        await self._consciousness_analysis(request.content)
        
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

## Tools for PEP 8 Compliance

### Automated Tools
1. **black**: Code formatter
2. **flake8**: Linter for style guide enforcement
3. **isort**: Import sorting
4. **mypy**: Type checking

### Configuration Files

#### pyproject.toml
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
```

#### .flake8
```ini
[flake8]
max-line-length = 79
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist
```

## Enforcement

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
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

### CI/CD Integration
```yaml
# .github/workflows/pep8.yml
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

## Summary

Following PEP 8 guidelines ensures:
- **Readability**: Code is easier to read and understand
- **Consistency**: Uniform style across the codebase
- **Maintainability**: Easier to maintain and modify
- **Collaboration**: Better team collaboration
- **Professionalism**: Industry-standard code quality

Remember: PEP 8 is a guide, not a law. When following PEP 8 would make code less readable, use your judgment and document the deviation. 