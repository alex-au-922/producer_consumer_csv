from abc import ABC, abstractmethod
from typing import overload, Sequence


class PublishFilenamesClient(ABC):
    @overload
    def publish(self, filename: str) -> bool:  # type: ignore[overload-overlap]
        ...

    @overload
    def publish(self, filename: Sequence[str]) -> list[bool]:
        ...

    @abstractmethod
    def publish(self, filename: str | Sequence[str]) -> bool | list[bool]:
        ...

    @abstractmethod
    def close(self) -> bool:
        ...
