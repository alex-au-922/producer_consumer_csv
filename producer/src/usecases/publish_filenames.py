from abc import ABC, abstractmethod
from typing import overload, Sequence


class PublishFilenamesClient(ABC):
    @overload
    def publish(self, filename: str) -> bool:
        pass

    @overload
    def publish(self, filename: Sequence[str]) -> list[bool]:
        pass

    @abstractmethod
    def publish(self, filename: str | Sequence[str]) -> bool | list[bool]:
        pass

    @abstractmethod
    def close(self) -> bool:
        pass
