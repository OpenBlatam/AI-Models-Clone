from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from .model import CopywritingInput, CopywritingOutput, CopywritingModel
from .llm import CopywritingLLM, CopywritingLLMConfig
from .copywriting import Copywriting, CopywritingCreate, CopywritingRead 
from typing import Any, List, Dict, Optional
import logging
import asyncio