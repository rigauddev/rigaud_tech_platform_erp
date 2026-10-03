from uuid import uuid4

import pyotp
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.database.session import async_session_factory
from app.main import create_app
from app.modules.auth.application.mfa_services import SecretEncryptionService
from app.modules.auth.application.passwords import PasswordService
from app.modules.auth.infrastructure.models import (
    AuthSessionModel,
    AuthUserModel,
    MfaRecoveryCodeModel,
    UserMfaMethodModel,
)
from app.modules.companies.infrastructure.models import CompanyModel


@pytest_asyncio.fixture
async def mfa_client() -> AsyncClient:
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def clean_mfa_tables() -> None:
    async with async_session_factory() as session:
        await session.execute(delete(MfaRecoveryCodeModel))
        await session.execute(delete(UserMfaMethodModel))
        await session.execute(delete(AuthSessionModel))
        await session.execute(delete(AuthUserModel))
        await session.execute(delete(CompanyModel))
        await session.commit()
    yield


def _valid_cnpj(seed: int) -> str:
    base = f"{seed:08d}0001"[-12:]

    def digit(value: str, weights: list[int]) -> str:
        total = sum(int(item) * weight for item, weight in zip(value, weights, strict=True))
        remainder = total % 11
        return str(0 if remainder < 2 else 11 - remainder)

    first = digit(base, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    second = digit(base + first, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return base + first + second


async def _create_user() -> AuthUserModel:
    async with async_session_factory() as session:
        company = CompanyModel(
            id=uuid4(),
            legal_name="MFA Demo Ltda",
            trade_name="MFA Demo",
            document=_valid_cnpj(991),
            email="contato@mfa-demo.com.br",
            phone="75982165869",
            slug="mfa-demo",
            code="MFADEMO",
            timezone="America/Sao_Paulo",
            locale="pt-BR",
            currency="BRL",
        )
        session.add(company)
        await session.flush()
        user = AuthUserModel(
            tenant_id=company.id,
            tenant_slug=company.slug,
            email="mfa@example.com",
            phone="75982165869",
            password_hash=PasswordService().hash("Senha123"),
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest.mark.integration
@pytest.mark.asyncio
async def test_totp_setup_confirm_and_login_requires_mfa(mfa_client: AsyncClient) -> None:
    user = await _create_user()
    login = await mfa_client.post(
        "/api/v1/auth/login",
        json={"email": "mfa@example.com", "password": "Senha123"},
    )
    token = login.json()["access_token"]

    setup = await mfa_client.post(
        "/api/v1/auth/mfa/totp/setup",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert setup.status_code == 200
    secret = setup.json()["secret"]
    assert "otpauth_uri" in setup.json()

    confirm = await mfa_client.post(
        "/api/v1/auth/mfa/totp/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"code": pyotp.TOTP(secret).now()},
    )
    assert confirm.status_code == 200
    assert confirm.json()["code"] == "AUTH_MFA_ENABLED"
    assert "codes" in confirm.json()

    second_login = await mfa_client.post(
        "/api/v1/auth/login",
        json={"email": "mfa@example.com", "password": "Senha123"},
    )
    assert second_login.status_code == 200
    assert second_login.json()["code"] == "AUTH_MFA_REQUIRED"
    challenge_id = second_login.json()["data"]["challenge_id"]

    async with async_session_factory() as session:
        method = (
            await session.execute(
                select(UserMfaMethodModel).where(UserMfaMethodModel.user_id == user.id)
            )
        ).scalar_one()
        secret = SecretEncryptionService().decrypt(method.encrypted_secret)

    verified = await mfa_client.post(
        "/api/v1/auth/mfa/verify",
        json={
            "challenge_id": challenge_id,
            "method": "totp",
            "code": pyotp.TOTP(secret).now(),
        },
    )
    assert verified.status_code == 200
    assert "access_token" in verified.json()
