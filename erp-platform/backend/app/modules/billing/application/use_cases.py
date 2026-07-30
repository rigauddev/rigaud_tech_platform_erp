from dataclasses import dataclass
from uuid import UUID

from app.modules.billing.domain.entities import BillingEventStatus, BillingEventType
from app.modules.billing.infrastructure.models import BillingEventModel
from app.modules.billing.infrastructure.repositories import SQLAlchemyBillingEventRepository


@dataclass(frozen=True)
class BillingEventInput:
    tenant_id: UUID
    subscription_id: UUID | None
    event_type: BillingEventType
    provider: str = "fake"
    external_event_id: str | None = None
    payload: dict | None = None
    actor_id: UUID | None = None


class RecordBillingEvent:
    def __init__(self, billing_events: SQLAlchemyBillingEventRepository) -> None:
        self.billing_events = billing_events

    async def execute(self, input_data: BillingEventInput) -> BillingEventModel:
        event = BillingEventModel(
            tenant_id=input_data.tenant_id,
            subscription_id=input_data.subscription_id,
            provider=input_data.provider,
            event_type=input_data.event_type.value,
            status=BillingEventStatus.PROCESSED.value,
            external_event_id=input_data.external_event_id,
            payload=input_data.payload,
            created_by=input_data.actor_id,
            updated_by=input_data.actor_id,
        )
        return await self.billing_events.add(event)
