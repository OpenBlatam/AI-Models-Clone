from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Iterable
from itertools import islice
from typing import TypeVar

from typing import Any, List, Dict, Optional
import logging
import asyncio
T = TypeVar("T")


def batch_generator(
    items: Iterable[T],
    batch_size: int,
    pre_batch_yield: Callable[[list[T]], None] | None = None,
) -> Generator[list[T], None, None]:
    iterable = iter(items)
    while True:
        batch = list(islice(iterable, batch_size))
        if not batch:
            return

        if pre_batch_yield:
            pre_batch_yield(batch)
        yield batch
