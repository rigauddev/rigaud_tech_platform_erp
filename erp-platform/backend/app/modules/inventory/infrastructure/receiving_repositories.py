from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.inventory.domain.entities import ReceivingDocumentStatus
from app.modules.inventory.domain.receiving_repositories import ReceivingDocumentRepository
from app.modules.inventory.infrastructure.models import ReceivingDocumentModel


class SQLAlchemyReceivingDocumentRepository(ReceivingDocumentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, document: ReceivingDocumentModel) -> ReceivingDocumentModel:
        self.session.add(document)
        await self.session.flush()
        await self.session.refresh(document, attribute_names=["items"])
        return document

    async def get_by_id(
        self, document_id: UUID, *, tenant_id: UUID
    ) -> ReceivingDocumentModel | None:
        result = await self.session.execute(
            select(ReceivingDocumentModel)
            .options(selectinload(ReceivingDocumentModel.items))
            .where(
                ReceivingDocumentModel.id == document_id,
                ReceivingDocumentModel.tenant_id == tenant_id,
                ReceivingDocumentModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        status: ReceivingDocumentStatus | None,
        search: str | None,
        limit: int,
        offset: int,
    ) -> list[ReceivingDocumentModel]:
        statement = self._filtered_select(
            tenant_id=tenant_id,
            branch_id=branch_id,
            warehouse_id=warehouse_id,
            status=status,
            search=search,
        )
        statement = (
            statement.options(selectinload(ReceivingDocumentModel.items))
            .order_by(ReceivingDocumentModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        status: ReceivingDocumentStatus | None,
        search: str | None,
    ) -> int:
        statement = self._filtered_select(
            tenant_id=tenant_id,
            branch_id=branch_id,
            warehouse_id=warehouse_id,
            status=status,
            search=search,
        )
        result = await self.session.execute(select(func.count()).select_from(statement.subquery()))
        return int(result.scalar_one())

    async def exists_by_document_number(
        self,
        document_number: str,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        statement = select(ReceivingDocumentModel.id).where(
            ReceivingDocumentModel.tenant_id == tenant_id,
            ReceivingDocumentModel.branch_id == branch_id,
            ReceivingDocumentModel.document_number == document_number,
            ReceivingDocumentModel.deleted_at.is_(None),
        )
        if exclude_id is not None:
            statement = statement.where(ReceivingDocumentModel.id != exclude_id)
        result = await self.session.execute(statement.limit(1))
        return result.scalar_one_or_none() is not None

    def _filtered_select(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        status: ReceivingDocumentStatus | None,
        search: str | None,
    ) -> Select[tuple[ReceivingDocumentModel]]:
        statement = select(ReceivingDocumentModel).where(
            ReceivingDocumentModel.tenant_id == tenant_id,
            ReceivingDocumentModel.deleted_at.is_(None),
        )
        if branch_id is not None:
            statement = statement.where(ReceivingDocumentModel.branch_id == branch_id)
        if warehouse_id is not None:
            statement = statement.where(ReceivingDocumentModel.warehouse_id == warehouse_id)
        if status is not None:
            statement = statement.where(ReceivingDocumentModel.status == status)
        if search:
            term = f"%{search.strip()}%"
            statement = statement.where(
                or_(
                    ReceivingDocumentModel.document_number.ilike(term),
                    ReceivingDocumentModel.document_type.ilike(term),
                    ReceivingDocumentModel.notes.ilike(term),
                )
            )
        return statement
