from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.products.domain.entities import ProductType, UnitOfMeasure


class ProductBaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProductCreateRequest(ProductBaseSchema):
    name: str = Field(min_length=1, max_length=160)
    internal_code: str = Field(min_length=2, max_length=40)
    description: str | None = Field(default=None, max_length=1000)
    barcode: str | None = Field(default=None, max_length=64)
    product_type: ProductType = ProductType.SIMPLE
    unit_of_measure: UnitOfMeasure = UnitOfMeasure.UNIT
    sale_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    cost_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    main_image_url: str | None = Field(default=None, max_length=500)
    is_available_for_sale: bool = True


class ProductUpdateRequest(ProductBaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    internal_code: str | None = Field(default=None, min_length=2, max_length=40)
    description: str | None = Field(default=None, max_length=1000)
    barcode: str | None = Field(default=None, max_length=64)
    product_type: ProductType | None = None
    unit_of_measure: UnitOfMeasure | None = None
    sale_price: Decimal | None = Field(default=None, ge=0)
    cost_price: Decimal | None = Field(default=None, ge=0)
    main_image_url: str | None = Field(default=None, max_length=500)
    is_available_for_sale: bool | None = None


class ProductAvailabilityRequest(ProductBaseSchema):
    is_available_for_sale: bool


class ProductResponse(ProductBaseSchema):
    id: UUID
    tenant_id: UUID
    name: str
    description: str | None
    internal_code: str
    barcode: str | None
    product_type: ProductType
    unit_of_measure: UnitOfMeasure
    sale_price: Decimal
    cost_price: Decimal
    main_image_url: str | None
    is_active: bool
    is_available_for_sale: bool
    created_at: datetime
    updated_at: datetime


class ProductListResponse(ProductBaseSchema):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
