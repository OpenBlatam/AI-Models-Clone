from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
CALL_TO_ACTION_PROMPT = """
You are a marketing copywriter. Write 3 strong call-to-action phrases for the following context:

- Context: {context}
- Goal: {goal}

Your response should be a list of call-to-action phrases, each on a new line.
""".strip() 