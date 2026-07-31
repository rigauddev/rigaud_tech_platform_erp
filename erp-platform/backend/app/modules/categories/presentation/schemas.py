from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.categories.domain.entities import CategoryStatus


class CategoryBaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CategoryCreateRequest(CategoryBaseSchema):
    name: str = Field(min_length=1, max_length=120)
    internal_code: str = Field(min_length=2, max_length=40)
    parent_id: UUID | None = None
    slug: str | None = Field(default=None, min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=500)
    icon: str | None = Field(default=None, max_length=80)
    color: str | None = Field(default=None, max_length=7)
    display_order: int = Field(default=0, ge=0)


class CategoryUpdateRequest(CategoryBaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    internal_code: str | None = Field(default=None, min_length=2, max_length=40)
    parent_id: UUID | None = None
    slug: str | None = Field(default=None, min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=500)
    icon: str | None = Field(default=None, max_length=80)
    color: str | None = Field(default=None, max_length=7)
    display_order: int | None = Field(default=None, ge=0)


class CategoryReorderRequest(CategoryBaseSchema):
    display_order: int = Field(ge=0)


class CategoryResponse(CategoryBaseSchema):
    id: UUID
    tenant_id: UUID
    parent_id: UUID | None
    internal_code: str
    name: str
    slug: str
    description: str | None
    icon: str | None
    color: str | None
    display_order: int
    status: CategoryStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CategoryTreeResponse(CategoryResponse):
    children: list["CategoryTreeResponse"] = Field(default_factory=list)


CategoryTreeResponse.model_rebuild()
