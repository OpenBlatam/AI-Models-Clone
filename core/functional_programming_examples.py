from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Dict, List, Tuple, Optional, Callable, Any, Union
from dataclasses import dataclass
from functools import reduce, partial
import operator
import json
import logging
from pathlib import Path
import asyncio
from datetime import datetime
    import re
    import aiohttp
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
        import string
from typing import Any, List, Dict, Optional
"""
Functional Programming Examples
Demonstrating pure functions, declarative programming, and avoiding classes where possible.
"""


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# PURE FUNCTIONS - No side effects, predictable outputs
# ============================================================================

def calculate_metrics(data: List[float]) -> Dict[str, float]:
    """Pure function to calculate statistical metrics."""
    if not data:
        return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
    
    n = len(data)
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / n
    std = variance ** 0.5
    
    return {
        "mean": mean,
        "std": std,
        "min": min(data),
        "max": max(data)
    }

def transform_text(text: str, operations: List[Callable[[str], str]]) -> str:
    """Pure function to apply a series of text transformations."""
    return reduce(lambda acc, op: op(acc), operations, text)

def filter_and_map(data: List[Any], 
                   filter_predicate: Callable[[Any], bool],
                   map_function: Callable[[Any], Any]) -> List[Any]:
    """Pure function combining filter and map operations."""
    return list(map(map_function, filter(filter_predicate, data)))

# ============================================================================
# DECLARATIVE DATA PROCESSING
# ============================================================================

def process_user_data(users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Declarative data processing pipeline."""
    
    # Define transformation functions
    def is_active_user(user: Dict[str, Any]) -> bool:
        return user.get("status") == "active" and user.get("age", 0) >= 18
    
    def enrich_user_data(user: Dict[str, Any]) -> Dict[str, Any]:
        return {
            **user,
            "age_group": "senior" if user.get("age", 0) >= 65 else "adult",
            "full_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
            "processed_at": datetime.now().isoformat()
        }
    
    def sort_by_age(user: Dict[str, Any]) -> int:
        return user.get("age", 0)
    
    # Declarative pipeline
    return (
        filter(is_active_user, users) |
        map(enrich_user_data) |
        sorted(key=sort_by_age)
    )

# ============================================================================
# FUNCTIONAL UTILITIES
# ============================================================================

def compose(*functions: Callable) -> Callable:
    """Function composition utility."""
    def inner(arg) -> Any:
        return reduce(lambda acc, f: f(acc), reversed(functions), arg)
    return inner

def curry(func: Callable, *args, **kwargs) -> Callable:
    """Partial function application."""
    return partial(func, *args, **kwargs)

def memoize(func: Callable) -> Callable:
    """Simple memoization decorator."""
    cache: Dict[str, Any] = {}
    
    def wrapper(*args) -> Any:
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    
    return wrapper

# ============================================================================
# DATA VALIDATION FUNCTIONS
# ============================================================================

def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Pure function for email validation."""
    
    if not email:
        return False, "Email cannot be empty"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, None

async async async def validate_user_input(user_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Pure function for user input validation."""
    errors: List[Any] = []
    
    # Required fields validation
    required_fields: List[Any] = ["email", "name", "age"]
    for field in required_fields:
        if field not in user_data or not user_data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Email validation
    if "email" in user_data:
        is_valid, error = validate_email(user_data["email"])
        if not is_valid:
            errors.append(error)
    
    # Age validation
    if "age" in user_data:
        try:
            age = int(user_data["age"])
            if age < 0 or age > 150:
                errors.append("Age must be between 0 and 150")
        except (ValueError, TypeError):
            errors.append("Age must be a valid number")
    
    return len(errors) == 0, errors

# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

def load_config(config_path: str) -> Dict[str, Any]:
    """Pure function to load configuration."""
    try:
        with open(config_path, 'r') as f:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file not found: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config: {e}")
        return {}

def merge_configs(base_config: Dict[str, Any], 
                  override_config: Dict[str, Any]) -> Dict[str, Any]:
    """Pure function to merge configurations."""
    def deep_merge(d1: Dict[str, Any], d2: Dict[str, Any]) -> Dict[str, Any]:
        result = d1.copy()
        for key, value in d2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    return deep_merge(base_config, override_config)

# ============================================================================
# ASYNC FUNCTIONAL PATTERNS
# ============================================================================

async def process_data_async(data_items: List[Any], 
                           processor: Callable[[Any], Any],
                           batch_size: int = 10) -> List[Any]:
    """Async functional data processing."""
    
    async def process_batch(batch: List[Any]) -> List[Any]:
        return [processor(item) for item in batch]
    
    # Split into batches
    batches: List[Any] = [data_items[i:i + batch_size] for i in range(0, len(data_items), batch_size)]
    
    # Process batches concurrently
    tasks: List[Any] = [process_batch(batch) for batch in batches]
    results = await asyncio.gather(*tasks)
    
    # Flatten results
    return [item for batch in results for item in batch]

async async async async async def fetch_data_with_retry(url: str, 
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
                               max_retries: int = 3,
                               delay: float = 1.0) -> Optional[Dict[str, Any]]:
    """Async function with retry logic."""
    
    async async async async async async def attempt_fetch(attempt: int) -> Optional[Dict[str, Any]]:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
        try:
            async with aiohttp.ClientSession() as session:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"HTTP {response.status} on attempt {attempt}")
                        return None
        except Exception as e:
            logger.error(f"Fetch attempt {attempt} failed: {e}")
            return None
    
    for attempt in range(max_retries):
        result = await attempt_fetch(attempt + 1)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
        if result is not None:
            return result
        
        if attempt < max_retries - 1:
            await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
    
    return None

# ============================================================================
# ERROR HANDLING WITH FUNCTIONAL PATTERNS
# ============================================================================

def safe_divide(numerator: float, denominator: float) -> Tuple[bool, Union[float, str]]:
    """Functional error handling with Result pattern."""
    if denominator == 0:
        return False, "Division by zero"
    return True, numerator / denominator

def safe_parse_json(json_string: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
    """Functional JSON parsing with error handling."""
    try:
        return True, json.loads(json_string)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

def handle_errors(func: Callable) -> Callable:
    """Functional error handling decorator."""
    def wrapper(*args, **kwargs) -> Any:
        try:
            return True, func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return False, str(e)
    return wrapper

# ============================================================================
# DATA TRANSFORMATION PIPELINES
# ============================================================================

def create_data_pipeline(*transformations: Callable) -> Callable:
    """Create a data transformation pipeline."""
    def pipeline(data: Any) -> Any:
        return reduce(lambda acc, transform: transform(acc), transformations, data)
    return pipeline

def text_processing_pipeline() -> Callable:
    """Example text processing pipeline."""
    def lowercase(text: str) -> str:
        return text.lower()
    
    def remove_punctuation(text: str) -> str:
        return text.translate(str.maketrans("", "", string.punctuation))
    
    def remove_extra_whitespace(text: str) -> str:
        return " ".join(text.split())
    
    return create_data_pipeline(lowercase, remove_punctuation, remove_extra_whitespace)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def chunk_list(data: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks."""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

def flatten_list(nested_list: List[List[Any]]) -> List[Any]:
    """Flatten nested list."""
    return [item for sublist in nested_list for item in sublist]

def group_by(data: List[Dict[str, Any]], key: str) -> Dict[Any, List[Dict[str, Any]]]:
    """Group data by key."""
    result: Dict[str, Any] = {}
    for item in data:
        group_key = item.get(key)
        if group_key not in result:
            result[group_key] = []
        result[group_key].append(item)
    return result

def sort_dict_by_value(data: Dict[str, Any], reverse: bool = False) -> List[Tuple[str, Any]]:
    """Sort dictionary by values."""
    return sorted(data.items(), key=operator.itemgetter(1), reverse=reverse)

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def demonstrate_functional_patterns() -> Any:
    """Demonstrate the functional programming patterns."""
    
    # Example data
    users: List[Any] = [
        {"name": "Alice", "age": 25, "status": "active", "email": "alice@example.com"},
        {"name": "Bob", "age": 17, "status": "active", "email": "bob@example.com"},
        {"name": "Charlie", "age": 30, "status": "inactive", "email": "charlie@example.com"},
        {"name": "Diana", "age": 70, "status": "active", "email": "diana@example.com"}
    ]
    
    # Process user data declaratively
    processed_users = process_user_data(users)
    print("Processed users:", processed_users)
    
    # Text processing pipeline
    text_pipeline = text_processing_pipeline()
    sample_text: str: str = "Hello, World! This is a TEST."
    processed_text = text_pipeline(sample_text)
    print("Processed text:", processed_text)
    
    # Metrics calculation
    numbers: List[Any] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    metrics = calculate_metrics(numbers)
    print("Metrics:", metrics)
    
    # Validation
    user_input: Dict[str, Any] = {"name": "John", "age": "25", "email": "john@example.com"}
    is_valid, errors = validate_user_input(user_input)
    print("Validation result:", is_valid, errors)

match __name__:
    case "__main__":
    demonstrate_functional_patterns() 