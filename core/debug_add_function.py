from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import sys
import os
    from example_add_function import add
from typing import Any, List, Dict, Optional
import logging
import asyncio
#!/usr/bin/env python3
"""
Debug script to identify which add function is being used
"""


# Print current working directory
print(f"Current working directory: {os.getcwd()}")

# Try to import add function
try:
    print("✅ Successfully imported add from example_add_function.py")
    
    # Test the function
    result = add(1, 2)
    print(f"add(1, 2) = {result}")
    
    if result == 3:
        print("✅ Function is working correctly (addition)")
    elif result == -1:
        print("❌ Function is doing subtraction instead of addition")
        print("   This means the file still has 'return a - b' instead of 'return a + b'")
    else:
        print(f"❓ Unexpected result: {result}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

# Check if there are any .pyc files that might be cached
print("\nChecking for cached files:")
for file in os.listdir('.'):
    if file.endswith('.pyc') and 'add' in file:
        print(f"Found cached file: {file}")
        os.remove(file)
        print(f"Removed cached file: {file}")

print("\nTo fix the issue:")
print("1. Make sure example_add_function.py has 'return a + b'")
print("2. Restart your Python interpreter")
print("3. Clear any .pyc cache files") 