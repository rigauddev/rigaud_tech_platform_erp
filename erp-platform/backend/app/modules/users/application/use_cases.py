from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.modules.auth.application.passwords import PasswordService
from app.modules.auth.domain.repositories import AuthSessionRepository
from app.modules.auth.infrastructure.models import AuthUserModel
from app.modules.companies.domain.entities import CompanyStatus
from app.modules.companies.domain.exceptions import CompanyNotFoundError
from app.modules.companies.domain.repositories import CompanyRepository
from app.modules.users.application.validators import (
    normalize_optional_text,
    normalize_phone,
    normalize_user_email,
)
from app.modules.users.domain.entities import UserStatus
from app.modules.users.domain.exceptions import (
    InvalidPasswordError,
    InvalidUserDataError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserPermissionError,
)
from app.modules.users.domain.repositories import UserRepository


@dataclass(frozen=True)
class UserCreateInput:
    tenant_id: UUID
    email: str
    password: str
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    phone: str | None = None
    must_change_password: bool = True
    actor_id: UUID | None = None


@dataclass(frozen=True)
class UserUpdateInput:
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    phone: str | None = None
    status: UserStatus | None = None
    must_change_password: bool | None = None
    actor_id: UUID | None = None


@dataclass(frozen=True)
class ProfileUpdateInput:
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    phone: str | None = None
    actor_id: UUID | None = None


@dataclass(frozen=True)
class UserListInput:
    page: int = 1
    page_size: int = 20
    tenant_id: UUID | None = None
    status: UserStatus | None = None
    search: str | None = None


@dataclass(frozen=True)
class UserListResult:
    items: list[AuthUserModel]
    total: int
    page: int
    page_size: int


class CreateUser:
    def __init__(
        self,
        users: UserRepository,
        companies: CompanyRepository,
        password_service: PasswordService,
    ) -> None:
        self.users = users
        self.companies = companies
        self.password_service = password_service

    async def execute(self, input_data: UserCreateInput) -> AuthUserModel:
        company = await self.companies.get_by_id(input_data.tenant_id)
        if company is None:
            raise CompanyNotFoundError("Company not found.")
        if company.status != CompanyStatus.ACTIVE or not company.is_active:
            raise InvalidUserDataError("Company must be active.")

        email = normalize_user_email(input_data.email)
        if await self.users.exists_by_email_and_tenant_id(email, company.id):
            raise UserAlreadyExistsError("Email already exists for this company.")

        user = AuthUserModel(
            tenant_id=company.id,
            tenant_slug=company.slug,
            email=email,
            password_hash=self.password_service.hash(input_data.password),
            first_name=normalize_optional_text(input_data.first_name, "first_name", max_length=80),
            last_name=normalize_optional_text(input_data.last_name, "last_name", max_length=120),
            display_name=normalize_optional_text(
                input_data.display_name,
                "display_name",
                max_length=160,
            ),
            phone=normalize_phone(input_data.phone),
            status=UserStatus.ACTIVE,
            is_active=True,
            is_superuser=False,
            must_change_password=input_data.must_change_password,
            failed_login_attempts=0,
            created_by=input_data.actor_id,
            updated_by=input_data.actor_id,
        )
        try:
            return await self.users.add(user)
        except IntegrityError as exc:
            raise UserAlreadyExistsError("Email already exists for this company.") from exc
        except ValueError as exc:
            raise InvalidUserDataError(str(exc)) from exc


class ListUsers:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    async def execute(self, input_data: UserListInput) -> UserListResult:
        page = max(input_data.page, 1)
        page_size = min(max(input_data.page_size, 1), 100)
        offset = (page - 1) * page_size
        search = input_data.search.strip() if input_data.search else None
        items = await self.users.list(
            limit=page_size,
            offset=offset,
            tenant_id=input_data.tenant_id,
            status=input_data.status,
            search=search,
        )
        total = await self.users.count(
            tenant_id=input_data.tenant_id,
            status=input_data.status,
            search=search,
        )
        return UserListResult(items=items, total=total, page=page, page_size=page_size)


class GetUser:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    async def execute(
        self,
        user_id: UUID,
        *,
        actor_id: UUID,
        actor_is_superuser: bool,
    ) -> AuthUserModel:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError("User not found.")
        if not actor_is_superuser and user.id != actor_id:
            raise UserPermissionError("Permission denied.")
        return user


class UpdateUser:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    async def execute(self, user_id: UUID, input_data: UserUpdateInput) -> AuthUserModel:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError("User not found.")

        try:
            if input_data.email is not None:
                email = normalize_user_email(input_data.email)
                if await self.users.exists_by_email_and_tenant_id(
                    email,
                    user.tenant_id,
                    exclude_id=user.id,
                ):
                    raise UserAlreadyExistsError("Email already exists for this company.")
                user.email = email
            if input_data.first_name is not None:
                user.first_name = normalize_optional_text(
                    input_data.first_name,
                    "first_name",
                    max_length=80,
                )
            if input_data.last_name is not None:
                user.last_name = normalize_optional_text(
                    input_data.last_name,
                    "last_name",
                    max_length=120,
                )
            if input_data.display_name is not None:
                user.display_name = normalize_optional_text(
                    input_data.display_name,
                    "display_name",
                    max_length=160,
                )
            if input_data.phone is not None:
                user.phone = normalize_phone(input_data.phone)
            if input_data.status is not None:
                _apply_status(user, input_data.status)
            if input_data.must_change_password is not None:
                user.must_change_password = input_data.must_change_password
            user.updated_by = input_data.actor_id
            return await self.users.add(user)
        except ValueError as exc:
            raise InvalidUserDataError(str(exc)) from exc


class UpdateOwnProfile:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    async def execute(self, user_id: UUID, input_data: ProfileUpdateInput) -> AuthUserModel:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError("User not found.")
        try:
            if input_data.first_name is not None:
                user.first_name = normalize_optional_text(
                    input_data.first_name, "first_name", max_length=80
                )
            if input_data.last_name is not None:
                user.last_name = normalize_optional_text(
                    input_data.last_name, "last_name", max_length=120
                )
            if input_data.display_name is not None:
                user.display_name = normalize_optional_text(
                    input_data.display_name, "display_name", max_length=160
                )
            if input_data.phone is not None:
                user.phone = normalize_phone(input_data.phone)
            user.updated_by = input_data.actor_id
            return await self.users.add(user)
        except ValueError as exc:
            raise InvalidUserDataError(str(exc)) from exc


class ChangeUserStatus:
    def __init__(self, users: UserRepository, sessions: AuthSessionRepository) -> None:
        self.users = users
        self.sessions = sessions

    async def execute(
        self,
        user_id: UUID,
        status: UserStatus,
        *,
        actor_id: UUID | None = None,
    ) -> AuthUserModel:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError("User not found.")
        _apply_status(user, status)
        user.updated_by = actor_id
        if status != UserStatus.ACTIVE:
            await self.sessions.revoke_all_for_user(user.id, datetime.now(UTC))
        return await self.users.add(user)


class ChangeOwnPassword:
    def __init__(
        self,
        users: UserRepository,
        sessions: AuthSessionRepository,
        password_service: PasswordService,
    ) -> None:
        self.users = users
        self.sessions = sessions
        self.password_service = password_service

    async def execute(self, user_id: UUID, current_password: str, new_password: str) -> None:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError("User not found.")
        if not self.password_service.verify(current_password, user.password_hash):
            raise InvalidPasswordError("Current password is invalid.")
        user.password_hash = self.password_service.hash(new_password)
        user.must_change_password = False
        user.failed_login_attempts = 0
        user.updated_by = user.id
        await self.users.add(user)
        await self.sessions.revoke_all_for_user(user.id, datetime.now(UTC))


class ResetUserPassword:
    def __init__(
        self,
        users: UserRepository,
        sessions: AuthSessionRepository,
        password_service: PasswordService,
    ) -> None:
        self.users = users
        self.sessions = sessions
        self.password_service = password_service

    async def execute(self, user_id: UUID, temporary_password: str, *, actor_id: UUID) -> None:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError("User not found.")
        user.password_hash = self.password_service.hash(temporary_password)
        user.must_change_password = True
        user.failed_login_attempts = 0
        user.locked_until = None
        user.updated_by = actor_id
        await self.users.add(user)
        await self.sessions.revoke_all_for_user(user.id, datetime.now(UTC))


def _apply_status(user: AuthUserModel, status: UserStatus) -> None:
    if status == UserStatus.ACTIVE:
        user.activate()
    elif status == UserStatus.INACTIVE:
        user.deactivate()
    elif status == UserStatus.BLOCKED:
        user.block()
