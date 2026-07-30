from dataclasses import dataclass


@dataclass(frozen=True)
class Permission:
    code: str


@dataclass(frozen=True)
class Role:
    code: str
    permissions: tuple[Permission, ...] = ()
