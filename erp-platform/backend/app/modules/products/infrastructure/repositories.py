from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products.domain.entities import ProductType, UnitOfMeasure
from app.modules.products.domain.repositories import ProductRepository
from app.modules.products.infrastructure.models import ProductModel


class SQLAlchemyProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, product: ProductModel) -> ProductModel:
        self.session.add(product)
        await self.session.flush()
        return product

    async def get_by_id(self, product_id: UUID, *, tenant_id: UUID) -> ProductModel | None:
        result = await self.session.execute(
            select(ProductModel).where(
                ProductModel.id == product_id,
                ProductModel.tenant_id == tenant_id,
                ProductModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

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
        statement = self._filtered_select(
            tenant_id=tenant_id,
            product_type=product_type,
            unit_of_measure=unit_of_measure,
            is_active=is_active,
            is_available_for_sale=is_available_for_sale,
            search=search,
        )
        statement = statement.order_by(ProductModel.name).limit(limit).offset(offset)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

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
        statement = self._filtered_select(
            tenant_id=tenant_id,
            product_type=product_type,
            unit_of_measure=unit_of_measure,
            is_active=is_active,
            is_available_for_sale=is_available_for_sale,
            search=search,
        )
        result = await self.session.execute(select(func.count()).select_from(statement.subquery()))
        return int(result.scalar_one())

    async def exists_by_internal_code(
        self,
        internal_code: str,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        return await self._exists(
            ProductModel.internal_code == internal_code,
            tenant_id=tenant_id,
            exclude_id=exclude_id,
        )

    async def exists_by_barcode(
        self,
        barcode: str,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        return await self._exists(
            ProductModel.barcode == barcode,
            tenant_id=tenant_id,
            exclude_id=exclude_id,
        )

    def _filtered_select(
        self,
        *,
        tenant_id: UUID,
        product_type: ProductType | None,
        unit_of_measure: UnitOfMeasure | None,
        is_active: bool | None,
        is_available_for_sale: bool | None,
        search: str | None,
    ) -> Select[tuple[ProductModel]]:
        statement = select(ProductModel).where(
            ProductModel.tenant_id == tenant_id,
            ProductModel.deleted_at.is_(None),
        )
        if product_type is not None:
            statement = statement.where(ProductModel.product_type == product_type)
        if unit_of_measure is not None:
            statement = statement.where(ProductModel.unit_of_measure == unit_of_measure)
        if is_active is not None:
            statement = statement.where(ProductModel.is_active == is_active)
        if is_available_for_sale is not None:
            statement = statement.where(ProductModel.is_available_for_sale == is_available_for_sale)
        if search:
            like = f"%{search.lower()}%"
            statement = statement.where(
                or_(
                    func.lower(ProductModel.name).like(like),
                    func.lower(ProductModel.internal_code).like(like),
                    func.lower(ProductModel.barcode).like(like),
                )
            )
        return statement

    async def _exists(
        self,
        condition,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        statement = select(ProductModel.id).where(
            condition,
            ProductModel.tenant_id == tenant_id,
            ProductModel.deleted_at.is_(None),
        )
        if exclude_id is not None:
            statement = statement.where(ProductModel.id != exclude_id)
        result = await self.session.execute(statement.limit(1))
        return result.scalar_one_or_none() is not None
