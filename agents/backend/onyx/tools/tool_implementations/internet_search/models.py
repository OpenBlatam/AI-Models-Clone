from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from pydantic import BaseModel


from typing import Any, List, Dict, Optional
import logging
import asyncio
class InternetSearchResult(BaseModel):
    title: str
    link: str
    snippet: str


class InternetSearchResponse(BaseModel):
    revised_query: str
    internet_results: list[InternetSearchResult]
