from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
KEYWORDS_GENERATOR_PROMPT = """
You are an SEO expert. Generate a list of relevant SEO keywords for the following topic:

- Topic: {topic}
- Target Audience: {audience}

Your response should be a comma-separated list of keywords.
""".strip() 