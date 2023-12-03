from abc import ABC, abstractmethod
from typing import Generator, Sequence, overload, TypeVar, Generic

T = TypeVar("T")


class FetchFilenameStreamClient(ABC, Generic[T]):
    @overload
    def ack(self, message_receipt: T) -> bool:
        ...

    @overload
    def ack(self, message_receipt: Sequence[T]) -> list[bool]:
        ...

    @abstractmethod
    def ack(self, message_receipt: T | Sequence[T]) -> bool | list[bool]:
        ...

    @overload
    def reject(self, message_receipt: T) -> bool:
        ...

    @overload
    def reject(self, message_receipt: Sequence[T]) -> list[bool]:
        ...

    @abstractmethod
    def reject(self, message_receipt: T | Sequence[T]) -> bool | list[bool]:
        ...

    @abstractmethod
    def fetch_stream(self) -> Generator[tuple[str, T], None, None]:
        ...

    @abstractmethod
    def close(self) -> bool:
        ...
