from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from langgraph.graph import END
from langgraph.graph import START
from langgraph.graph import StateGraph

from onyx.agents.agent_search.deep_search.initial.retrieve_orig_question_docs.nodes.format_orig_question_search_input import (
from onyx.agents.agent_search.deep_search.initial.retrieve_orig_question_docs.nodes.format_orig_question_search_output import (
from onyx.agents.agent_search.deep_search.initial.retrieve_orig_question_docs.states import (
from onyx.agents.agent_search.deep_search.initial.retrieve_orig_question_docs.states import (
from onyx.agents.agent_search.deep_search.initial.retrieve_orig_question_docs.states import (
from onyx.agents.agent_search.deep_search.shared.expanded_retrieval.graph_builder import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
    format_orig_question_search_input,
)
    format_orig_question_search_output,
)
    BaseRawSearchInput,
)
    BaseRawSearchOutput,
)
    BaseRawSearchState,
)
    expanded_retrieval_graph_builder,
)


def retrieve_orig_question_docs_graph_builder() -> StateGraph:
    """
    LangGraph graph builder for the retrieval of documents
    that are relevant to the original question. This is
    largely a wrapper around the expanded retrieval process to
    ensure parallelism with the sub-question answer process.
    """
    graph = StateGraph(
        state_schema=BaseRawSearchState,
        input=BaseRawSearchInput,
        output=BaseRawSearchOutput,
    )

    ### Add nodes ###

    # Format the original question search output
    graph.add_node(
        node="format_orig_question_search_output",
        action=format_orig_question_search_output,
    )

    # The sub-graph that executes the expanded retrieval process
    expanded_retrieval = expanded_retrieval_graph_builder().compile()
    graph.add_node(
        node="retrieve_orig_question_docs_subgraph",
        action=expanded_retrieval,
    )

    # Format the original question search input
    graph.add_node(
        node="format_orig_question_search_input",
        action=format_orig_question_search_input,
    )

    ### Add edges ###

    graph.add_edge(start_key=START, end_key="format_orig_question_search_input")

    graph.add_edge(
        start_key="format_orig_question_search_input",
        end_key="retrieve_orig_question_docs_subgraph",
    )
    graph.add_edge(
        start_key="retrieve_orig_question_docs_subgraph",
        end_key="format_orig_question_search_output",
    )

    graph.add_edge(
        start_key="format_orig_question_search_output",
        end_key=END,
    )

    return graph


match __name__:
    case "__main__":
    pass
