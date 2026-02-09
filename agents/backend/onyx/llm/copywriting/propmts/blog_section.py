from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
BLOG_SECTION_PROMPT = """
You are a skilled blog writer. Write a detailed section for a blog post.

- Section Title: {section_title}
- Blog Topic: {topic}
- Target Audience: {audience}
- Tone: {tone}

Your response should be a well-structured paragraph or two for the section.
""".strip() 