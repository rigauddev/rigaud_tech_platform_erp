import asyncio
import os

from app.database.session import async_session_factory
from app.modules.companies.application.use_cases import CompanyCreateInput, CreateCompany
from app.modules.companies.infrastructure.repositories import SQLAlchemyCompanyRepository

REQUIRED_ENV = (
    "COMPANY_LEGAL_NAME",
    "COMPANY_TRADE_NAME",
    "COMPANY_DOCUMENT",
    "COMPANY_SLUG",
    "COMPANY_CODE",
)


def _required(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        msg = f"Missing required environment variable: {name}"
        raise RuntimeError(msg)
    return value


async def create_company() -> None:
    missing = [name for name in REQUIRED_ENV if not os.getenv(name)]
    if missing:
        msg = f"Missing required environment variables: {', '.join(missing)}"
        raise RuntimeError(msg)

    async with async_session_factory() as session:
        company = await CreateCompany(SQLAlchemyCompanyRepository(session)).execute(
            CompanyCreateInput(
                legal_name=_required("COMPANY_LEGAL_NAME"),
                trade_name=_required("COMPANY_TRADE_NAME"),
                document=_required("COMPANY_DOCUMENT"),
                email=os.getenv("COMPANY_EMAIL"),
                phone=os.getenv("COMPANY_PHONE"),
                slug=_required("COMPANY_SLUG"),
                code=_required("COMPANY_CODE"),
                timezone=os.getenv("COMPANY_TIMEZONE"),
                locale=os.getenv("COMPANY_LOCALE"),
                currency=os.getenv("COMPANY_CURRENCY"),
            )
        )
        await session.commit()
        print(f"Company created: {company.id}")


def main() -> None:
    asyncio.run(create_company())


if __name__ == "__main__":
    main()
