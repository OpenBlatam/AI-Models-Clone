from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from celery import Celery
from onyx.background.celery.apps.beat import celery_app
from onyx.utils.variable_functionality import set_is_ee_based_on_env_variable
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Factory stub for running celery worker / celery beat."""



set_is_ee_based_on_env_variable()
app: Celery = celery_app
