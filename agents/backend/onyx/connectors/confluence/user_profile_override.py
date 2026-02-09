from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from onyx.connectors.confluence.models import ConfluenceUser


from typing import Any, List, Dict, Optional
import logging
import asyncio
def process_confluence_user_profiles_override(
    confluence_user_email_override: list[dict[str, str]],
) -> list[ConfluenceUser]:
    return [
        ConfluenceUser(
            user_id=override["user_id"],
            # username is not returned by the Confluence Server API anyways
            username=override["username"],
            display_name=override["display_name"],
            email=override["email"],
            type=override["type"],
        )
        for override in confluence_user_email_override
        if override is not None
    ]
