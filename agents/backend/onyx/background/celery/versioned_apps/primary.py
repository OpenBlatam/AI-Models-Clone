from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from celery import Celery
from onyx.utils.variable_functionality import fetch_versioned_implementation
from onyx.utils.variable_functionality import set_is_ee_based_on_env_variable
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Factory stub for running celery worker / celery beat."""



set_is_ee_based_on_env_variable()
app: Celery = fetch_versioned_implementation(
    "onyx.background.celery.apps.primary",
    "celery_app",
)
