from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.modules.products.application.validators import (
    normalize_barcode,
    normalize_image_url,
    normalize_internal_code,
    normalize_money,
    normalize_optional_text,
    normalize_text,
)
from app.modules.products.domain.entities import ProductType, UnitOfMeasure
from app.modules.products.domain.exceptions import (
    ProductAlreadyExistsError,
    ProductBarcodeAlreadyExistsError,
    ProductInternalCodeAlreadyExistsError,
    ProductNotAvailableError,
    ProductNotFoundError,
)
from app.modules.products.domain.repositories import ProductRepository
from app.modules.products.infrastructure.models import ProductModel


@dataclass(frozen=True)
class ProductCreateInput:
    tenant_id: UUID
    name: str
    internal_code: str
    description: str | None = None
    barcode: str | None = None
    product_type: ProductType = ProductType.SIMPLE
    unit_of_measure: UnitOfMeasure = UnitOfMeasure.UNIT
    sale_price: Decimal | str | int = Decimal("0.00")
    cost_price: Decimal | str | int = Decimal("0.00")
    main_image_url: str | None = None
    is_available_for_sale: bool = True
    actor_id: UUID | None = None


@dataclass(frozen=True)
class ProductUpdateInput:
    name: str | None = None
    description: str | None = None
    internal_code: str | None = None
    barcode: str | None = None
    product_type: ProductType | None = None
    unit_of_measure: UnitOfMeasure | None = None
    sale_price: Decimal | str | int | None = None
    cost_price: Decimal | str | int | None = None
    main_image_url: str | None = None
    is_available_for_sale: bool | None = None
    actor_id: UUID | None = None


@dataclass(frozen=True)
class ProductListInput:
    tenant_id: UUID
    page: int = 1
    page_size: int = 20
    product_type: ProductType | None = None
    unit_of_measure: UnitOfMeasure | None = None
    is_active: bool | None = None
    is_available_for_sale: bool | None = None
    search: str | None = None


@dataclass(frozen=True)
class ProductListResult:
    items: list[ProductModel]
    total: int
    page: int
    page_size: int


class CreateProduct:
    def __init__(self, products: ProductRepository) -> None:
        self.products = products

    async def execute(self, input_data: ProductCreateInput) -> ProductModel:
        internal_code = normalize_internal_code(input_data.internal_code)
        barcode = normalize_barcode(input_data.barcode)
        await self._ensure_unique(
            tenant_id=input_data.tenant_id,
            internal_code=internal_code,
            barcode=barcode,
        )

        product = ProductModel(
            tenant_id=input_data.tenant_id,
            name=normalize_text(input_data.name, "name", max_length=160),
            description=normalize_optional_text(
                input_data.description,
                "description",
                max_length=1000,
            ),
            internal_code=internal_code,
            barcode=barcode,
            product_type=input_data.product_type,
            unit_of_measure=input_data.unit_of_measure,
            sale_price=normalize_money(input_data.sale_price, "sale_price"),
            cost_price=normalize_money(input_data.cost_price, "cost_price"),
            main_image_url=normalize_image_url(input_data.main_image_url),
            is_active=True,
            is_available_for_sale=input_data.is_available_for_sale,
            created_by=input_data.actor_id,
            updated_by=input_data.actor_id,
        )
        try:
            return await self.products.add(product)
        except IntegrityError as exc:
            raise ProductAlreadyExistsError("Product already exists.") from exc

    async def _ensure_unique(
        self,
        *,
        tenant_id: UUID,
        internal_code: str,
        barcode: str | None,
    ) -> None:
        if await self.products.exists_by_internal_code(internal_code, tenant_id=tenant_id):
            raise ProductInternalCodeAlreadyExistsError("Internal code already exists.")
        if barcode and await self.products.exists_by_barcode(barcode, tenant_id=tenant_id):
            raise ProductBarcodeAlreadyExistsError("Barcode already exists.")


class GetProduct:
    def __init__(self, products: ProductRepository) -> None:
        self.products = products

    async def execute(self, product_id: UUID, *, tenant_id: UUID) -> ProductModel:
        product = await self.products.get_by_id(product_id, tenant_id=tenant_id)
        if product is None:
            raise ProductNotFoundError("Product not found.")
        return product


class ListProducts:
    def __init__(self, products: ProductRepository) -> None:
        self.products = products

    async def execute(self, input_data: ProductListInput) -> ProductListResult:
        page = max(input_data.page, 1)
        page_size = min(max(input_data.page_size, 1), 100)
        offset = (page - 1) * page_size
        search = input_data.search.strip() if input_data.search else None
        items = await self.products.list(
            tenant_id=input_data.tenant_id,
            limit=page_size,
            offset=offset,
            product_type=input_data.product_type,
            unit_of_measure=input_data.unit_of_measure,
            is_active=input_data.is_active,
            is_available_for_sale=input_data.is_available_for_sale,
            search=search,
        )
        total = await self.products.count(
            tenant_id=input_data.tenant_id,
            product_type=input_data.product_type,
            unit_of_measure=input_data.unit_of_measure,
            is_active=input_data.is_active,
            is_available_for_sale=input_data.is_available_for_sale,
            search=search,
        )
        return ProductListResult(items=items, total=total, page=page, page_size=page_size)


class UpdateProduct:
    def __init__(self, products: ProductRepository) -> None:
        self.products = products

    async def execute(
        self,
        product_id: UUID,
        *,
        tenant_id: UUID,
        input_data: ProductUpdateInput,
    ) -> ProductModel:
        product = await self.products.get_by_id(product_id, tenant_id=tenant_id)
        if product is None:
            raise ProductNotFoundError("Product not found.")
        if product.is_deleted:
            raise ProductNotFoundError("Product not found.")

        try:
            if input_data.name is not None:
                product.name = normalize_text(input_data.name, "name", max_length=160)
            if input_data.description is not None:
                product.description = normalize_optional_text(
                    input_data.description,
                    "description",
                    max_length=1000,
                )
            if input_data.internal_code is not None:
                internal_code = normalize_internal_code(input_data.internal_code)
                if await self.products.exists_by_internal_code(
                    internal_code,
                    tenant_id=tenant_id,
                    exclude_id=product.id,
                ):
                    raise ProductInternalCodeAlreadyExistsError("Internal code already exists.")
                product.internal_code = internal_code
            if input_data.barcode is not None:
                barcode = normalize_barcode(input_data.barcode)
                if barcode and await self.products.exists_by_barcode(
                    barcode,
                    tenant_id=tenant_id,
                    exclude_id=product.id,
                ):
                    raise ProductBarcodeAlreadyExistsError("Barcode already exists.")
                product.barcode = barcode
            if input_data.product_type is not None:
                product.product_type = input_data.product_type
            if input_data.unit_of_measure is not None:
                product.unit_of_measure = input_data.unit_of_measure
            if input_data.sale_price is not None:
                product.sale_price = normalize_money(input_data.sale_price, "sale_price")
            if input_data.cost_price is not None:
                product.cost_price = normalize_money(input_data.cost_price, "cost_price")
            if input_data.main_image_url is not None:
                product.main_image_url = normalize_image_url(input_data.main_image_url)
            if input_data.is_available_for_sale is not None:
                product.change_availability(input_data.is_available_for_sale)
            product.updated_by = input_data.actor_id
            return await self.products.add(product)
        except IntegrityError as exc:
            raise ProductAlreadyExistsError("Product already exists.") from exc


class ActivateProduct:
    def __init__(self, products: ProductRepository) -> None:
        self.products = products

    async def execute(
        self,
        product_id: UUID,
        *,
        tenant_id: UUID,
        actor_id: UUID | None = None,
    ) -> ProductModel:
        product = await GetProduct(self.products).execute(product_id, tenant_id=tenant_id)
        product.activate()
        product.updated_by = actor_id
        return await self.products.add(product)


class DeactivateProduct:
    def __init__(self, products: ProductRepository) -> None:
        self.products = products

    async def execute(
        self,
        product_id: UUID,
        *,
        tenant_id: UUID,
        actor_id: UUID | None = None,
    ) -> ProductModel:
        product = await GetProduct(self.products).execute(product_id, tenant_id=tenant_id)
        product.deactivate()
        product.updated_by = actor_id
        return await self.products.add(product)


class ChangeProductAvailability:
    def __init__(self, products: ProductRepository) -> None:
        self.products = products

    async def execute(
        self,
        product_id: UUID,
        *,
        tenant_id: UUID,
        available: bool,
        actor_id: UUID | None = None,
    ) -> ProductModel:
        product = await GetProduct(self.products).execute(product_id, tenant_id=tenant_id)
        if not product.is_active and available:
            raise ProductNotAvailableError("Inactive products cannot be available for sale.")
        product.change_availability(available)
        product.updated_by = actor_id
        return await self.products.add(product)


class DeleteProduct:
    def __init__(self, products: ProductRepository) -> None:
        self.products = products

    async def execute(
        self,
        product_id: UUID,
        *,
        tenant_id: UUID,
        actor_id: UUID | None = None,
    ) -> ProductModel:
        product = await GetProduct(self.products).execute(product_id, tenant_id=tenant_id)
        product.deactivate()
        product.mark_as_deleted()
        product.deleted_by = actor_id
        product.updated_by = actor_id
        return await self.products.add(product)
