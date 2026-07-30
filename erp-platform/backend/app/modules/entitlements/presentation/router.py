from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.modules.auth.domain.entities import AuthenticatedUser
from app.modules.auth.presentation.dependencies import get_current_user
from app.modules.entitlements.application.use_cases import CheckEntitlement, ListTenantEntitlements
from app.modules.entitlements.infrastructure.repositories import SQLAlchemyEntitlementRepository
from app.modules.entitlements.presentation.schemas import (
    EntitlementCheckResponse,
    EntitlementResponse,
)
from app.shared.api.responses import success_response

router = APIRouter(prefix="/entitlements", tags=["SaaS Entitlements"])

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]


@router.get("", response_model=list[EntitlementResponse])
async def list_entitlements(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    items = await ListTenantEntitlements(SQLAlchemyEntitlementRepository(session)).execute(
        current_user.tenant_id
    )
    return success_response(
        "ENTITLEMENT_LIST_RETRIEVED",
        data=[EntitlementResponse.model_validate(item).model_dump(mode="json") for item in items],
    )


@router.get("/{entitlement_key}", response_model=EntitlementCheckResponse)
async def check_entitlement(
    entitlement_key: str,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    is_enabled = await CheckEntitlement(SQLAlchemyEntitlementRepository(session)).execute(
        current_user.tenant_id, entitlement_key
    )
    data = EntitlementCheckResponse(
        tenant_id=current_user.tenant_id,
        entitlement_key=entitlement_key,
        is_enabled=is_enabled,
    )
    return success_response("ENTITLEMENT_CHECKED", data=data.model_dump(mode="json"))
