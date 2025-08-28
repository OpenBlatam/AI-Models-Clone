from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from onyx.background.celery.apps.monitoring import celery_app

from typing import Any, List, Dict, Optional
import logging
import asyncio
celery_app.autodiscover_tasks(
    [
        "ee.onyx.background.celery.tasks.tenant_provisioning",
    ]
)
