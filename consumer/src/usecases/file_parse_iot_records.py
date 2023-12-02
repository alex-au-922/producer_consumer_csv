from abc import ABC, abstractmethod
from typing import Iterator, overload, Sequence
from ..entities import IOTRecord


class FileParseIOTRecordsClient(ABC):
    @overload
    def parse(self, filename: str) -> list[IOTRecord]:
        ...

    @overload
    def parse(self, filename: Sequence[str]) -> list[list[IOTRecord]]:
        ...

    @abstractmethod
    def parse(
        self, filename: str | Sequence[str]
    ) -> list[IOTRecord] | list[list[IOTRecord]]:
        ...

    @abstractmethod
    def parse_stream(self, filename: str) -> Iterator[IOTRecord]:
        ...

    @abstractmethod
    def close(self) -> bool:
        ...
