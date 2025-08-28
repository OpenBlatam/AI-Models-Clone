from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
QUESTION_ANSWER_PROMPT = """
You are an expert in your field. Provide a clear and concise answer to the following question:

- Question: {question}

Your response should be a direct answer, followed by a brief explanation if necessary.
""".strip() 