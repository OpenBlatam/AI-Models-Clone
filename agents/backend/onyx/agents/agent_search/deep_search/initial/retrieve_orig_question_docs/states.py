from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from onyx.agents.agent_search.deep_search.main.states import (
from onyx.agents.agent_search.deep_search.shared.expanded_retrieval.states import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
    OrigQuestionRetrievalUpdate,
)
    ExpandedRetrievalInput,
)


## Graph Input State
class BaseRawSearchInput(ExpandedRetrievalInput):
    pass


## Graph Output State
class BaseRawSearchOutput(OrigQuestionRetrievalUpdate):
    """
    This is a list of results even though each call of this subgraph only returns one result.
    This is because if we parallelize the answer query subgraph, there will be multiple
      results in a list so the add operator is used to add them together.
    """

    # base_expanded_retrieval_result: QuestionRetrievalResult = QuestionRetrievalResult()


## Graph State
class BaseRawSearchState(
    BaseRawSearchInput, BaseRawSearchOutput, OrigQuestionRetrievalUpdate
):
    pass
