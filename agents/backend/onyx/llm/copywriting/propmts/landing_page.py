from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
LANDING_PAGE_PROMPT = """
You are a conversion copywriter. Write persuasive copy for a landing page based on the following:

- Product/Service: {product}
- Target Audience: {audience}
- Main Benefit: {benefit}
- Call to Action: {cta}

Your response should include a headline, subheadline, and a short paragraph.
""".strip() 