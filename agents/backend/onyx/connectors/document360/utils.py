from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
def flatten_child_categories(category: dict) -> list[dict]:
    if not category["child_categories"]:
        return [category]
    else:
        flattened_categories = [category]
        for child_category in category["child_categories"]:
            flattened_categories.extend(flatten_child_categories(child_category))
        return flattened_categories
