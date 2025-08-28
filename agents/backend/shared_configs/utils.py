from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import TypeVar


from typing import Any, List, Dict, Optional
import logging
import asyncio
T = TypeVar("T")


def batch_list(
    lst: list[T],
    batch_size: int,
) -> list[list[T]]:
    return [lst[i : i + batch_size] for i in range(0, len(lst), batch_size)]
