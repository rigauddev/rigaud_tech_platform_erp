from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.feature_flags.domain.entities import FeatureFlagScope


class FeatureFlagRequest(BaseModel):
    feature_key: str = Field(min_length=2, max_length=80)
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    scope: FeatureFlagScope = FeatureFlagScope.TENANT
    tenant_id: UUID | None = None
    is_enabled: bool = True


class FeatureFlagToggleRequest(BaseModel):
    is_enabled: bool


class FeatureFlagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID | None
    feature_key: str
    name: str
    description: str | None
    scope: str
    status: str
    is_enabled: bool
