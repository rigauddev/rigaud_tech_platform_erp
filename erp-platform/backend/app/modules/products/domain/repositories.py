from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.products.domain.entities import ProductType, UnitOfMeasure
from app.modules.products.infrastructure.models import ProductModel


class ProductRepository(ABC):
    @abstractmethod
    async def add(self, product: ProductModel) -> ProductModel:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, product_id: UUID, *, tenant_id: UUID) -> ProductModel | None:
        raise NotImplementedError

    @abstractmethod
    async def list(
        self,
        *,
        tenant_id: UUID,
        limit: int,
        offset: int,
        product_type: ProductType | None = None,
        unit_of_measure: UnitOfMeasure | None = None,
        is_active: bool | None = None,
        is_available_for_sale: bool | None = None,
        search: str | None = None,
    ) -> list[ProductModel]:
        raise NotImplementedError

    @abstractmethod
    async def count(
        self,
        *,
        tenant_id: UUID,
        product_type: ProductType | None = None,
        unit_of_measure: UnitOfMeasure | None = None,
        is_active: bool | None = None,
        is_available_for_sale: bool | None = None,
        search: str | None = None,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_internal_code(
        self,
        internal_code: str,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_barcode(
        self,
        barcode: str,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        raise NotImplementedError
