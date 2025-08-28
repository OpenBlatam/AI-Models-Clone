from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from sqlalchemy.orm import Session

from onyx.access.access import get_acl_for_user
from onyx.context.search.models import IndexFilters
from onyx.db.models import User


from typing import Any, List, Dict, Optional
import logging
import asyncio
def build_access_filters_for_user(user: User | None, session: Session) -> list[str]:
    user_acl = get_acl_for_user(user, session)
    return list(user_acl)


def build_user_only_filters(user: User | None, db_session: Session) -> IndexFilters:
    user_acl_filters = build_access_filters_for_user(user, db_session)
    return IndexFilters(
        source_type=None,
        document_set=None,
        time_cutoff=None,
        tags=None,
        access_control_list=user_acl_filters,
    )
