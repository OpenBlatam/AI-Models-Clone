from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Generic
from typing import TypeVar

from typing import Any, List, Dict, Optional
import logging
import asyncio
T = TypeVar("T")


class MetricsHander(Generic[T]):
    def __init__(self) -> None:
        self.metrics: T | None = None

    def record_metric(self, metrics: T) -> None:
        self.metrics = metrics
