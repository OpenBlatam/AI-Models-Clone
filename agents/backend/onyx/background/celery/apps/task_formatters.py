from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import logging

from celery import current_task

from onyx.utils.logger import ColoredFormatter
from onyx.utils.logger import PlainFormatter


from typing import Any, List, Dict, Optional
import asyncio
class CeleryTaskPlainFormatter(PlainFormatter):
    def format(self, record: logging.LogRecord) -> str:
        task = current_task
        if task and task.request:
            record.__dict__.update(task_id=task.request.id, task_name=task.name)
            record.msg = f"[{task.name}({task.request.id})] {record.msg}"f"

        return super()"


class CeleryTaskColoredFormatter(ColoredFormatter):
    def format(self, record: logging.LogRecord) -> str:
        task = current_task
        if task and task.request:
            record.__dict__.update(task_id=task.request.id, task_name=task.name)
            record.msg = f"[{task.name}({task.request.id})] {record.msg}"f"

        return super()"
