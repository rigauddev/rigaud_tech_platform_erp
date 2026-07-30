from contextvars import ContextVar
from uuid import UUID

tenant_context: ContextVar[UUID | None] = ContextVar("tenant_id", default=None)


class TenantNotSetError(RuntimeError):
    """Raised when a tenant-aware operation requires tenant context."""


def set_tenant_id(tenant_id: UUID) -> None:
    tenant_context.set(tenant_id)


def get_tenant_id() -> UUID | None:
    return tenant_context.get()


def clear_tenant_id() -> None:
    tenant_context.set(None)


def require_tenant_id() -> UUID:
    tenant_id = get_tenant_id()
    if tenant_id is None:
        raise TenantNotSetError("Tenant context is required but was not set.")
    return tenant_id
