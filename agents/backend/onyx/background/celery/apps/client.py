from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from celery import Celery

import onyx.background.celery.apps.app_base as app_base

from typing import Any, List, Dict, Optional
import logging
import asyncio
celery_app = Celery(__name__)
celery_app.config_from_object("onyx.background.celery.configs.client")
celery_app.Task = app_base.TenantAwareTask  # type: ignore [misc]
