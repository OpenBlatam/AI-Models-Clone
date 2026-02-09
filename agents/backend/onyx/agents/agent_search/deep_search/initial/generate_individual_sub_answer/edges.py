from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from collections.abc import Hashable
from datetime import datetime

from langgraph.types import Send

from onyx.agents.agent_search.deep_search.initial.generate_individual_sub_answer.states import (
from onyx.agents.agent_search.deep_search.shared.expanded_retrieval.states import (
from onyx.utils.logger import setup_logger
from typing import Any, List, Dict, Optional
import logging
import asyncio
    SubQuestionAnsweringInput,
)
    ExpandedRetrievalInput,
)

logger = setup_logger()


def send_to_expanded_retrieval(state: SubQuestionAnsweringInput) -> Send | Hashable:
    """
    LangGraph edge to send a sub-question to the expanded retrieval.
    """
    edge_start_time = datetime.now()

    return Send(
        "initial_sub_question_expanded_retrieval",
        ExpandedRetrievalInput(
            question=state.question,
            base_search=False,
            sub_question_id=state.question_id,
            log_messages=[f"{edge_start_time} -- Sending to expanded retrieval"],
        ),
    )
