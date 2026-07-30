from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import clear_tenant_id, get_async_session
from app.modules.auth.application.passwords import PasswordService
from app.modules.auth.application.tokens import TokenService
from app.modules.auth.application.use_cases import GetCurrentUser
from app.modules.auth.domain.entities import AuthenticatedUser
from app.modules.auth.domain.exceptions import AuthenticationRequiredError
from app.modules.auth.infrastructure.repositories import SQLAlchemyUserAuthRepository
from app.modules.companies.infrastructure.repositories import (
    SQLAlchemyBranchRepository,
    SQLAlchemyMembershipRepository,
)
from app.shared.observability.context import with_actor

bearer_scheme = HTTPBearer(auto_error=False)
BearerCredentialsDependency = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(bearer_scheme),
]
AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]


def get_password_service() -> PasswordService:
    return PasswordService()


def get_token_service() -> TokenService:
    return TokenService()


TokenServiceDependency = Annotated[TokenService, Depends(get_token_service)]


async def get_current_user(
    credentials: BearerCredentialsDependency,
    session: AsyncSessionDependency,
    token_service: TokenServiceDependency,
) -> AsyncGenerator[AuthenticatedUser]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationRequiredError("Authentication required.")

    use_case = GetCurrentUser(
        users=SQLAlchemyUserAuthRepository(session),
        token_service=token_service,
        memberships=SQLAlchemyMembershipRepository(session),
        branches=SQLAlchemyBranchRepository(session),
    )
    try:
        current_user = await use_case.execute(credentials.credentials)
        with_actor(user_id=current_user.id, tenant_id=current_user.tenant_id)
        yield current_user
    finally:
        clear_tenant_id()
