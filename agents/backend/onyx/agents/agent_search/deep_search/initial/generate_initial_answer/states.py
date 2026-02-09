from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from operator import add
from typing import Annotated
from typing import TypedDict

from onyx.agents.agent_search.core_state import CoreState
from onyx.agents.agent_search.deep_search.main.states import (
from onyx.agents.agent_search.deep_search.main.states import (
from onyx.agents.agent_search.deep_search.main.states import (
from onyx.agents.agent_search.deep_search.main.states import (
from onyx.agents.agent_search.deep_search.main.states import (
from onyx.agents.agent_search.deep_search.main.states import (
from onyx.agents.agent_search.deep_search.shared.expanded_retrieval.models import (
from onyx.context.search.models import InferenceSection
from typing import Any, List, Dict, Optional
import logging
import asyncio
    ExploratorySearchUpdate,
)
    InitialAnswerQualityUpdate,
)
    InitialAnswerUpdate,
)
    InitialQuestionDecompositionUpdate,
)
    OrigQuestionRetrievalUpdate,
)
    SubQuestionResultsUpdate,
)
    QuestionRetrievalResult,
)


### States ###
class SubQuestionRetrievalInput(CoreState):
    exploratory_search_results: list[InferenceSection]


## Graph State
class SubQuestionRetrievalState(
    # This includes the core state
    SubQuestionRetrievalInput,
    InitialQuestionDecompositionUpdate,
    InitialAnswerUpdate,
    SubQuestionResultsUpdate,
    OrigQuestionRetrievalUpdate,
    InitialAnswerQualityUpdate,
    ExploratorySearchUpdate,
):
    base_raw_search_result: Annotated[list[QuestionRetrievalResult], add]


## Graph Output State
class SubQuestionRetrievalOutput(TypedDict):
    log_messages: list[str]
