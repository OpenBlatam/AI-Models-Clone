from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import TypedDict

from onyx.agents.agent_search.core_state import CoreState
from onyx.agents.agent_search.deep_search.main.states import (
from onyx.agents.agent_search.deep_search.main.states import (
from onyx.agents.agent_search.deep_search.main.states import (
from onyx.context.search.models import InferenceSection
from typing import Any, List, Dict, Optional
import logging
import asyncio
    InitialAnswerUpdate,
)
    InitialQuestionDecompositionUpdate,
)
    SubQuestionResultsUpdate,
)


### States ###
class SubQuestionAnsweringInput(CoreState):
    exploratory_search_results: list[InferenceSection]


## Graph State
class SubQuestionAnsweringState(
    # This includes the core state
    SubQuestionAnsweringInput,
    InitialQuestionDecompositionUpdate,
    InitialAnswerUpdate,
    SubQuestionResultsUpdate,
):
    pass


## Graph Output State
class SubQuestionAnsweringOutput(TypedDict):
    log_messages: list[str]
