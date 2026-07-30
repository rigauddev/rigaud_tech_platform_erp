from enum import StrEnum


class BillingProviderCode(StrEnum):
    FAKE = "fake"
    ASAAS = "asaas"
    STRIPE = "stripe"
    MERCADO_PAGO = "mercado_pago"


class BillingEventStatus(StrEnum):
    RECEIVED = "received"
    PROCESSED = "processed"
    FAILED = "failed"


class BillingEventType(StrEnum):
    PAYMENT_CONFIRMED = "payment_confirmed"
    PAYMENT_REFUSED = "payment_refused"
    TRIAL_STARTED = "trial_started"
    TRIAL_ENDED = "trial_ended"
    SUBSCRIPTION_RENEWED = "subscription_renewed"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
