from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.domain.entities import InventoryTransferStatus
from app.modules.inventory.infrastructure.models import InventoryTransferModel


class SQLAlchemyInventoryTransferRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, transfer: InventoryTransferModel) -> InventoryTransferModel:
        self.session.add(transfer)
        await self.session.flush()
        return transfer

    async def get_by_id(
        self, transfer_id: UUID, *, tenant_id: UUID
    ) -> InventoryTransferModel | None:
        result = await self.session.execute(
            select(InventoryTransferModel).where(
                InventoryTransferModel.id == transfer_id,
                InventoryTransferModel.tenant_id == tenant_id,
                InventoryTransferModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        status: InventoryTransferStatus | None,
        limit: int,
        offset: int,
    ) -> list[InventoryTransferModel]:
        statement = (
            self._select(tenant_id=tenant_id, branch_id=branch_id, status=status)
            .order_by(InventoryTransferModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list((await self.session.execute(statement)).scalars().all())

    async def count(
        self, *, tenant_id: UUID, branch_id: UUID | None, status: InventoryTransferStatus | None
    ) -> int:
        statement = self._select(tenant_id=tenant_id, branch_id=branch_id, status=status)
        return int(
            (
                await self.session.execute(select(func.count()).select_from(statement.subquery()))
            ).scalar_one()
        )

    def _select(
        self, *, tenant_id: UUID, branch_id: UUID | None, status: InventoryTransferStatus | None
    ):
        statement = select(InventoryTransferModel).where(
            InventoryTransferModel.tenant_id == tenant_id,
            InventoryTransferModel.deleted_at.is_(None),
        )
        if branch_id is not None:
            statement = statement.where(
                (InventoryTransferModel.source_branch_id == branch_id)
                | (InventoryTransferModel.target_branch_id == branch_id)
            )
        if status is not None:
            statement = statement.where(InventoryTransferModel.status == status)
        return statement
