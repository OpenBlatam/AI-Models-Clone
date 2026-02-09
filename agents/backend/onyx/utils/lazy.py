from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from collections.abc import Callable
from functools import lru_cache
from typing import TypeVar

from typing import Any, List, Dict, Optional
import logging
import asyncio
R = TypeVar("R")


def lazy_eval(func: Callable[[], R]) -> Callable[[], R]:
    @lru_cache(maxsize=1)
    def lazy_func() -> R:
        return func()

    return lazy_func
