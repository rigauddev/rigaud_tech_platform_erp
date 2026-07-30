from abc import ABC
from typing import TypeVar

EntityT = TypeVar("EntityT")
IdentifierT = TypeVar("IdentifierT")


class Repository[EntityT, IdentifierT](ABC):
    """Contrato base para repositories de módulos independentes."""
