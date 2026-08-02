from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.inventory.domain.entities import ReceivingDocumentStatus


class ReceivingBaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ReceivingItemRequest(ReceivingBaseSchema):
    product_id: UUID
    ordered_quantity: Decimal = Field(ge=0)
    received_quantity: Decimal = Field(default=Decimal("0.000"), ge=0)
    damaged_quantity: Decimal = Field(default=Decimal("0.000"), ge=0)
    unit_cost: Decimal = Field(default=Decimal("0.00"), ge=0)


class ReceivingDocumentCreateRequest(ReceivingBaseSchema):
    warehouse_id: UUID
    supplier_id: UUID | None = None
    document_number: str = Field(min_length=2, max_length=60)
    document_type: str = Field(min_length=1, max_length=40)
    status: ReceivingDocumentStatus = ReceivingDocumentStatus.DRAFT
    expected_date: datetime | None = None
    received_date: datetime | None = None
    notes: str | None = Field(default=None, max_length=1000)
    items: list[ReceivingItemRequest] = Field(min_length=1)


class ReceivingDocumentUpdateRequest(ReceivingBaseSchema):
    document_number: str | None = Field(default=None, min_length=2, max_length=60)
    document_type: str | None = Field(default=None, min_length=1, max_length=40)
    supplier_id: UUID | None = None
    status: ReceivingDocumentStatus | None = None
    expected_date: datetime | None = None
    received_date: datetime | None = None
    notes: str | None = Field(default=None, max_length=1000)
    items: list[ReceivingItemRequest] | None = None


class ReceivingDocumentStatusRequest(ReceivingBaseSchema):
    status: ReceivingDocumentStatus
    received_date: datetime | None = None


class ReceivingItemResponse(ReceivingBaseSchema):
    id: UUID
    tenant_id: UUID
    document_id: UUID | None = None
    product_id: UUID
    ordered_quantity: Decimal
    received_quantity: Decimal
    damaged_quantity: Decimal
    pending_quantity: Decimal
    unit_cost: Decimal
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ReceivingDocumentResponse(ReceivingBaseSchema):
    id: UUID
    tenant_id: UUID
    branch_id: UUID
    warehouse_id: UUID
    supplier_id: UUID | None
    document_number: str
    document_type: str
    status: ReceivingDocumentStatus
    expected_date: datetime | None
    received_date: datetime | None
    notes: str | None
    items: list[ReceivingItemResponse]
    created_at: datetime
    updated_at: datetime
