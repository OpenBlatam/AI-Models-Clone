from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
PRODUCT_DESCRIPTION_BULLETS_PROMPT = """
You are a product copywriter. Write a product description in bullet points for the following:

- Product: {product}
- Key Features: {features}
- Target Audience: {audience}

Your response should be a list of 4-6 bullet points highlighting the product's benefits and features.
""".strip() 