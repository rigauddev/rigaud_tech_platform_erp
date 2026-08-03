from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.inventory.domain.entities import ReceivingDocumentStatus
from app.modules.inventory.infrastructure.models import ReceivingDocumentModel


class ReceivingDocumentRepository(ABC):
    @abstractmethod
    async def add(self, document: ReceivingDocumentModel) -> ReceivingDocumentModel:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(
        self, document_id: UUID, *, tenant_id: UUID
    ) -> ReceivingDocumentModel | None:
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    async def count(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        status: ReceivingDocumentStatus | None,
        search: str | None,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_document_number(
        self,
        document_number: str,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        raise NotImplementedError
