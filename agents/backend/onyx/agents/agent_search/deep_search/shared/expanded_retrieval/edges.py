from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from collections.abc import Hashable
from typing import cast

from langchain_core.runnables.config import RunnableConfig
from langgraph.types import Send

from onyx.agents.agent_search.deep_search.shared.expanded_retrieval.states import (
from onyx.agents.agent_search.deep_search.shared.expanded_retrieval.states import (
from onyx.agents.agent_search.models import GraphConfig
from typing import Any, List, Dict, Optional
import logging
import asyncio
    ExpandedRetrievalState,
)
    RetrievalInput,
)


def parallel_retrieval_edge(
    state: ExpandedRetrievalState, config: RunnableConfig
) -> list[Send | Hashable]:
    """
    LangGraph edge to parallelize the retrieval process for each of the
    generated sub-queries and the original question.
    """
    graph_config = cast(GraphConfig, config["metadata"]["config"])
    question = (
        state.question
        if state.question
        else graph_config.inputs.prompt_builder.raw_user_query
    )

    query_expansions = state.expanded_queries + [question]

    return [
        Send(
            "retrieve_documents",
            RetrievalInput(
                query_to_retrieve=query,
                question=question,
                base_search=False,
                sub_question_id=state.sub_question_id,
                log_messages=[],
            ),
        )
        for query in query_expansions
    ]
