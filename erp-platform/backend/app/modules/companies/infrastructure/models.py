from uuid import UUID, uuid4

from sqlalchemy import Boolean, Enum, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.database.mixins import AuditMixin, SoftDeleteMixin, TimestampMixin
from app.database.types import UUIDType
from app.modules.companies.domain.entities import CompanyStatus


class CompanyModel(TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "companies"
    __table_args__ = (
        UniqueConstraint("document", name="uq_companies_document"),
        UniqueConstraint("slug", name="uq_companies_slug"),
        UniqueConstraint("code", name="uq_companies_code"),
    )

    id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    legal_name: Mapped[str] = mapped_column(String(180), nullable=False)
    trade_name: Mapped[str] = mapped_column(String(120), nullable=False)
    document: Mapped[str] = mapped_column(String(14), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    slug: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    status: Mapped[CompanyStatus] = mapped_column(
        Enum(
            CompanyStatus,
            name="company_status",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=CompanyStatus.ACTIVE,
        nullable=False,
    )
    timezone: Mapped[str] = mapped_column(String(64), default="America/Sao_Paulo", nullable=False)
    locale: Mapped[str] = mapped_column(String(16), default="pt-BR", nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="BRL", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def activate(self) -> None:
        self.status = CompanyStatus.ACTIVE
        self.is_active = True

    def deactivate(self) -> None:
        self.status = CompanyStatus.INACTIVE
        self.is_active = False

    def suspend(self) -> None:
        self.status = CompanyStatus.SUSPENDED
        self.is_active = False
