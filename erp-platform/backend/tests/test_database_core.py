from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import (
    Base,
    CoreEntityMixin,
    TenantNotSetError,
    clear_tenant_id,
    get_tenant_id,
    require_tenant_id,
    set_tenant_id,
)
from app.database.base import naming_convention


class TechnicalTestEntity(CoreEntityMixin, Base):
    __tablename__ = "technical_test_entities"

    name: Mapped[str] = mapped_column(String(120), nullable=False)


@pytest.mark.unit
def test_base_uses_naming_convention() -> None:
    assert Base.metadata.naming_convention == naming_convention
    assert naming_convention["pk"] == "pk_%(table_name)s"
    assert naming_convention["fk"] == "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"


@pytest.mark.unit
def test_core_entity_mixin_defines_shared_columns() -> None:
    columns = TechnicalTestEntity.__table__.columns

    assert "id" in columns
    assert "tenant_id" in columns
    assert "created_at" in columns
    assert "updated_at" in columns
    assert "deleted_at" in columns
    assert "created_by" in columns
    assert "updated_by" in columns
    assert "deleted_by" in columns


@pytest.mark.unit
def test_core_entity_mixin_generates_uuid_and_tracks_soft_delete() -> None:
    entity = TechnicalTestEntity(name="technical", tenant_id=uuid4())
    uuid_default = TechnicalTestEntity.__table__.columns["id"].default

    assert uuid_default is not None
    assert isinstance(uuid_default.arg(None), UUID)
    assert entity.deleted_at is None
    assert entity.is_deleted is False

    entity.mark_as_deleted()

    assert entity.deleted_at is not None
    assert entity.deleted_at.tzinfo == UTC
    assert entity.is_deleted is True

    entity.restore()

    assert entity.deleted_at is None
    assert entity.is_deleted is False


@pytest.mark.unit
def test_timestamp_defaults_are_timezone_aware() -> None:
    created_default = TechnicalTestEntity.__table__.columns["created_at"].default
    updated_default = TechnicalTestEntity.__table__.columns["updated_at"].default

    assert created_default is not None
    assert updated_default is not None

    created_at = created_default.arg(None)
    updated_at = updated_default.arg(None)

    assert isinstance(created_at, datetime)
    assert isinstance(updated_at, datetime)
    assert created_at.tzinfo == UTC
    assert updated_at.tzinfo == UTC


@pytest.mark.unit
def test_tenant_context_lifecycle() -> None:
    tenant_id = uuid4()

    set_tenant_id(tenant_id)

    assert get_tenant_id() == tenant_id

    clear_tenant_id()

    assert get_tenant_id() is None


@pytest.mark.unit
def test_required_tenant_fails_when_context_is_empty() -> None:
    clear_tenant_id()

    with pytest.raises(TenantNotSetError):
        require_tenant_id()
