from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from langchain_core.runnables.config import RunnableConfig

from onyx.agents.agent_search.deep_search.shared.expanded_retrieval.states import (
from onyx.agents.agent_search.deep_search.shared.expanded_retrieval.states import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
    ExpandedRetrievalState,
)
    QueryExpansionUpdate,
)


def format_queries(
    state: ExpandedRetrievalState, config: RunnableConfig
) -> QueryExpansionUpdate:
    """
    LangGraph node to format the expanded queries into a list of strings.
    """
    return QueryExpansionUpdate(
        expanded_queries=state.expanded_queries,
    )
