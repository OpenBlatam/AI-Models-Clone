from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from celery import Celery
from onyx.utils.variable_functionality import fetch_versioned_implementation
from onyx.utils.variable_functionality import set_is_ee_based_on_env_variable
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Factory stub for running celery worker / celery beat.
This code is different from the primary/beat stubs because there is no EE version to
fetch. Port over the code in those files if we add an EE version of this worker."""



set_is_ee_based_on_env_variable()
app: Celery = fetch_versioned_implementation(
    "onyx.background.celery.apps.light",
    "celery_app",
)
