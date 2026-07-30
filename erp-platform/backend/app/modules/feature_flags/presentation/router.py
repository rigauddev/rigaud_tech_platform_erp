import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.modules.audit.application.service import AuditEventInput, AuditService
from app.modules.audit.infrastructure.repositories import SQLAlchemyAuditEventRepository
from app.modules.auth.domain.entities import AuthenticatedUser
from app.modules.auth.presentation.dependencies import get_current_user
from app.modules.feature_flags.application.use_cases import (
    ListFeatureFlags,
    ToggleFeatureFlag,
    UpsertFeatureFlag,
)
from app.modules.feature_flags.domain.exceptions import FeatureFlagError, FeatureFlagNotFoundError
from app.modules.feature_flags.infrastructure.repositories import SQLAlchemyFeatureFlagRepository
from app.modules.feature_flags.presentation.schemas import (
    FeatureFlagRequest,
    FeatureFlagResponse,
    FeatureFlagToggleRequest,
)
from app.shared.api.responses import error_response, success_response

router = APIRouter(prefix="/feature-flags", tags=["SaaS Feature Flags"])
logger = logging.getLogger("application")

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]


def _require_platform_admin(current_user: AuthenticatedUser) -> JSONResponse | None:
    if current_user.is_superuser:
        return None
    return error_response("AUTH_FORBIDDEN")


def _audit_service(session: AsyncSession) -> AuditService:
    return AuditService(SQLAlchemyAuditEventRepository(session))


@router.post("", response_model=FeatureFlagResponse)
async def upsert_feature_flag(
    payload: FeatureFlagRequest,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    if error := _require_platform_admin(current_user):
        return error
    feature_flag = await UpsertFeatureFlag(SQLAlchemyFeatureFlagRepository(session)).execute(
        payload_to_input(payload, current_user.id)
    )
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name="feature.enabled" if feature_flag.is_enabled else "feature.disabled",
            module="feature_flags",
            action="enabled" if feature_flag.is_enabled else "disabled",
            entity_type="feature_flag",
            entity_id=feature_flag.id,
            tenant_id=feature_flag.tenant_id,
            actor_user_id=current_user.id,
            after_data={
                "feature_key": feature_flag.feature_key,
                "enabled": feature_flag.is_enabled,
            },
        )
    )
    await session.commit()
    logger.info("feature.enabled" if feature_flag.is_enabled else "feature.disabled")
    return success_response(
        "FEATURE_FLAG_SAVED",
        data=FeatureFlagResponse.model_validate(feature_flag).model_dump(mode="json"),
    )


@router.get("", response_model=list[FeatureFlagResponse])
async def list_feature_flags(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    if error := _require_platform_admin(current_user):
        return error
    items = await ListFeatureFlags(SQLAlchemyFeatureFlagRepository(session)).execute(None)
    return success_response(
        "FEATURE_FLAG_LIST_RETRIEVED",
        data=[FeatureFlagResponse.model_validate(item).model_dump(mode="json") for item in items],
    )


@router.patch("/{flag_id}", response_model=FeatureFlagResponse)
async def toggle_feature_flag(
    flag_id: UUID,
    payload: FeatureFlagToggleRequest,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    if error := _require_platform_admin(current_user):
        return error
    try:
        feature_flag = await ToggleFeatureFlag(SQLAlchemyFeatureFlagRepository(session)).execute(
            flag_id, enabled=payload.is_enabled, actor_id=current_user.id
        )
        await session.commit()
        return success_response(
            "FEATURE_FLAG_SAVED",
            data=FeatureFlagResponse.model_validate(feature_flag).model_dump(mode="json"),
        )
    except FeatureFlagError as exc:
        await session.rollback()
        if isinstance(exc, FeatureFlagNotFoundError):
            return error_response("FEATURE_FLAG_NOT_FOUND")
        return error_response("VALIDATION_ERROR")


def payload_to_input(payload: FeatureFlagRequest, actor_id: UUID):
    from app.modules.feature_flags.application.use_cases import FeatureFlagInput

    return FeatureFlagInput(
        feature_key=payload.feature_key,
        name=payload.name,
        description=payload.description,
        scope=payload.scope,
        tenant_id=payload.tenant_id,
        is_enabled=payload.is_enabled,
        actor_id=actor_id,
    )
