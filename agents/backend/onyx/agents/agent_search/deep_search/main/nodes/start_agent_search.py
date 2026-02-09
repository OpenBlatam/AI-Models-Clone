from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from datetime import datetime
from typing import cast

from langchain_core.runnables import RunnableConfig

from onyx.agents.agent_search.deep_search.main.states import (
from onyx.agents.agent_search.deep_search.main.states import MainState
from onyx.agents.agent_search.models import GraphConfig
from onyx.agents.agent_search.shared_graph_utils.agent_prompt_ops import (
from onyx.agents.agent_search.shared_graph_utils.utils import (
from onyx.agents.agent_search.shared_graph_utils.utils import retrieve_search_docs
from onyx.configs.agent_configs import AGENT_EXPLORATORY_SEARCH_RESULTS
from onyx.context.search.models import InferenceSection
from typing import Any, List, Dict, Optional
import logging
import asyncio
    ExploratorySearchUpdate,
)
    build_history_prompt,
)
    get_langgraph_node_log_string,
)


def start_agent_search(
    state: MainState, config: RunnableConfig
) -> ExploratorySearchUpdate:
    """
    LangGraph node to start the agentic search process.
    """
    node_start_time = datetime.now()

    graph_config = cast(GraphConfig, config["metadata"]["config"])
    question = graph_config.inputs.prompt_builder.raw_user_query

    history = build_history_prompt(graph_config, question)

    # Initial search to inform decomposition. Just get top 3 fits
    search_tool = graph_config.tooling.search_tool
    assert search_tool, "search_tool must be provided for agentic search"
    retrieved_docs: list[InferenceSection] = retrieve_search_docs(search_tool, question)

    exploratory_search_results = retrieved_docs[:AGENT_EXPLORATORY_SEARCH_RESULTS]

    return ExploratorySearchUpdate(
        exploratory_search_results=exploratory_search_results,
        previous_history_summary=history,
        log_messages=[
            get_langgraph_node_log_string(
                graph_component="main",
                node_name="start agent search",
                node_start_time=node_start_time,
            )
        ],
    )
