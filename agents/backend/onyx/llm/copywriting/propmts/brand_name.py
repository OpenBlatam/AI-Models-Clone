from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
BRAND_NAME_PROMPT = """
You are a branding expert. Suggest 5 unique and catchy brand names for the following business:

- Business Description: {description}
- Target Audience: {audience}

Your response should be a list of brand names, each on a new line.
""".strip() 