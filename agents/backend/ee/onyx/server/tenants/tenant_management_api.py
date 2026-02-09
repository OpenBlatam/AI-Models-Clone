from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from fastapi import APIRouter
from fastapi import Depends

from ee.onyx.server.tenants.models import TenantByDomainResponse
from ee.onyx.server.tenants.provisioning import get_tenant_by_domain_from_control_plane
from onyx.auth.users import current_user
from onyx.auth.users import User
from onyx.utils.logger import setup_logger
from shared_configs.contextvars import get_current_tenant_id

from typing import Any, List, Dict, Optional
import logging
import asyncio
logger = setup_logger()

router = APIRouter(prefix="/tenants")

FORBIDDEN_COMMON_EMAIL_SUBSTRINGS = [
    "gmail",
    "outlook",
    "yahoo",
    "hotmail",
    "icloud",
    "msn",
    "hotmail",
    "hotmail.co.uk",
]


@router.get("/existing-team-by-domain")
def get_existing_tenant_by_domain(
    user: User | None = Depends(current_user),
) -> TenantByDomainResponse | None:
    if not user:
        return None
    domain = user.email.split("@")[1]
    if any(substring in domain for substring in FORBIDDEN_COMMON_EMAIL_SUBSTRINGS):
        return None

    tenant_id = get_current_tenant_id()

    return get_tenant_by_domain_from_control_plane(domain, tenant_id)
