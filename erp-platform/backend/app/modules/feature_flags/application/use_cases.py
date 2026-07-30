from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.modules.feature_flags.domain.entities import FeatureFlagScope, FeatureFlagStatus
from app.modules.feature_flags.domain.exceptions import (
    FeatureFlagAlreadyExistsError,
    FeatureFlagNotFoundError,
)
from app.modules.feature_flags.infrastructure.models import FeatureFlagModel
from app.modules.feature_flags.infrastructure.repositories import SQLAlchemyFeatureFlagRepository


@dataclass(frozen=True)
class FeatureFlagInput:
    feature_key: str
    name: str
    description: str | None
    scope: FeatureFlagScope
    tenant_id: UUID | None
    is_enabled: bool
    actor_id: UUID | None


class UpsertFeatureFlag:
    def __init__(self, feature_flags: SQLAlchemyFeatureFlagRepository) -> None:
        self.feature_flags = feature_flags

    async def execute(self, input_data: FeatureFlagInput) -> FeatureFlagModel:
        tenant_id = input_data.tenant_id if input_data.scope == FeatureFlagScope.TENANT else None
        feature_key = input_data.feature_key.strip().lower().replace("-", "_")
        feature_flag = await self.feature_flags.get_by_tenant_and_key(tenant_id, feature_key)
        if feature_flag is None:
            feature_flag = FeatureFlagModel(
                tenant_id=tenant_id,
                feature_key=feature_key,
                name=input_data.name.strip(),
                description=input_data.description.strip() if input_data.description else None,
                scope=input_data.scope.value,
                created_by=input_data.actor_id,
            )
        feature_flag.is_enabled = input_data.is_enabled
        feature_flag.status = (
            FeatureFlagStatus.ENABLED.value
            if input_data.is_enabled
            else FeatureFlagStatus.DISABLED.value
        )
        feature_flag.updated_by = input_data.actor_id
        try:
            return await self.feature_flags.add(feature_flag)
        except IntegrityError as exc:
            raise FeatureFlagAlreadyExistsError("Feature flag already exists.") from exc


class ToggleFeatureFlag:
    def __init__(self, feature_flags: SQLAlchemyFeatureFlagRepository) -> None:
        self.feature_flags = feature_flags

    async def execute(
        self, flag_id: UUID, *, enabled: bool, actor_id: UUID | None = None
    ) -> FeatureFlagModel:
        feature_flag = await self.feature_flags.get_by_id(flag_id)
        if feature_flag is None:
            raise FeatureFlagNotFoundError("Feature flag not found.")
        feature_flag.is_enabled = enabled
        feature_flag.status = (
            FeatureFlagStatus.ENABLED.value if enabled else FeatureFlagStatus.DISABLED.value
        )
        feature_flag.updated_by = actor_id
        return await self.feature_flags.add(feature_flag)


class ListFeatureFlags:
    def __init__(self, feature_flags: SQLAlchemyFeatureFlagRepository) -> None:
        self.feature_flags = feature_flags

    async def execute(self, tenant_id: UUID | None) -> list[FeatureFlagModel]:
        return await self.feature_flags.list_by_tenant(tenant_id)
