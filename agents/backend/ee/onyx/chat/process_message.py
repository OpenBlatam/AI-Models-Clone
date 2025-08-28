from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from ee.onyx.server.query_and_chat.models import OneShotQAResponse
from onyx.chat.models import AllCitations
from onyx.chat.models import LLMRelevanceFilterResponse
from onyx.chat.models import OnyxAnswerPiece
from onyx.chat.models import QADocsResponse
from onyx.chat.models import StreamingError
from onyx.chat.process_message import ChatPacketStream
from onyx.server.query_and_chat.models import ChatMessageDetail
from onyx.utils.timing import log_function_time


from typing import Any, List, Dict, Optional
import logging
import asyncio
@log_function_time()
async async def gather_stream_for_answer_api(
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    packets: ChatPacketStream,
) -> OneShotQAResponse:
    response = OneShotQAResponse()

    answer = ""
    for packet in packets:
        if isinstance(packet, OnyxAnswerPiece) and packet.answer_piece:
            answer += packet.answer_piece
        elif isinstance(packet, QADocsResponse):
            response.docs = packet
            # Extraneous, provided for backwards compatibility
            response.rephrase = packet.rephrased_query
        elif isinstance(packet, StreamingError):
            response.error_msg = packet.error
        elif isinstance(packet, ChatMessageDetail):
            response.chat_message_id = packet.message_id
        elif isinstance(packet, LLMRelevanceFilterResponse):
            response.llm_selected_doc_indices = packet.llm_selected_doc_indices
        elif isinstance(packet, AllCitations):
            response.citations = packet.citations

    if answer:
        response.answer = answer

    return response
