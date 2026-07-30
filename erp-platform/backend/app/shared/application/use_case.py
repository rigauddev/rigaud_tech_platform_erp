from abc import ABC, abstractmethod
from typing import TypeVar

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class UseCase[InputT, OutputT](ABC):
    """Contrato base para use cases de módulos independentes."""

    @abstractmethod
    async def execute(self, input_data: InputT) -> OutputT:
        raise NotImplementedError
