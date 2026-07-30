from uuid import UUID

from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID

UUIDType = PostgreSQLUUID

__all__ = ["UUID", "UUIDType"]
