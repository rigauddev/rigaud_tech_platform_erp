from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.users.domain.entities import UserStatus


class UserBaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UserCreateRequest(UserBaseSchema):
    tenant_id: UUID
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)
    first_name: str | None = Field(default=None, max_length=80)
    last_name: str | None = Field(default=None, max_length=120)
    display_name: str | None = Field(default=None, max_length=160)
    phone: str | None = Field(default=None, max_length=32)
    must_change_password: bool = True


class UserUpdateRequest(UserBaseSchema):
    email: str | None = Field(default=None, min_length=3, max_length=320)
    first_name: str | None = Field(default=None, max_length=80)
    last_name: str | None = Field(default=None, max_length=120)
    display_name: str | None = Field(default=None, max_length=160)
    phone: str | None = Field(default=None, max_length=32)
    status: UserStatus | None = None
    must_change_password: bool | None = None


class UserProfileUpdateRequest(UserBaseSchema):
    first_name: str | None = Field(default=None, max_length=80)
    last_name: str | None = Field(default=None, max_length=120)
    display_name: str | None = Field(default=None, max_length=160)
    phone: str | None = Field(default=None, max_length=32)


class ChangePasswordRequest(UserBaseSchema):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class ResetPasswordRequest(UserBaseSchema):
    temporary_password: str = Field(min_length=8, max_length=128)


class UserResponse(UserBaseSchema):
    id: UUID
    tenant_id: UUID
    tenant_slug: str
    email: str
    first_name: str | None
    last_name: str | None
    display_name: str | None
    phone: str | None
    status: UserStatus
    is_active: bool
    is_superuser: bool
    must_change_password: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


class UserListResponse(UserBaseSchema):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int


class PasswordChangedResponse(UserBaseSchema):
    message: str
