from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from datetime import datetime
from typing import cast

from langchain_core.runnables import RunnableConfig

from onyx.agents.agent_search.deep_search.main.states import MainState
from onyx.agents.agent_search.deep_search.main.states import (
from onyx.agents.agent_search.models import GraphConfig
from onyx.agents.agent_search.shared_graph_utils.utils import (
from onyx.utils.timing import log_function_time
from typing import Any, List, Dict, Optional
import logging
import asyncio
    RequireRefinemenEvalUpdate,
)
    get_langgraph_node_log_string,
)


@log_function_time(print_only=True)
def decide_refinement_need(
    state: MainState, config: RunnableConfig
) -> RequireRefinemenEvalUpdate:
    """
    LangGraph node to decide if refinement is needed based on the initial answer and the question.
    At present, we always refine.
    """
    node_start_time = datetime.now()

    graph_config = cast(GraphConfig, config["metadata"]["config"])

    decision = graph_config.behavior.allow_refinement

    if state.answer_error:
        return RequireRefinemenEvalUpdate(
            require_refined_answer_eval=False,
            log_messages=[
                get_langgraph_node_log_string(
                    graph_component="main",
                    node_name="decide refinement need",
                    node_start_time=node_start_time,
                    result="Timeout Error",
                )
            ],
        )

    log_messages = [
        get_langgraph_node_log_string(
            graph_component="main",
            node_name="decide refinement need",
            node_start_time=node_start_time,
            result=f"Refinement decision: {decision}",
        )
    ]

    return RequireRefinemenEvalUpdate(
        require_refined_answer_eval=graph_config.behavior.allow_refinement and decision,
        log_messages=log_messages,
    )
