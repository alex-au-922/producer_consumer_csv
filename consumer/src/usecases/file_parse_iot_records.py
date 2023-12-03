from abc import ABC, abstractmethod
from typing import Iterator, Optional, overload, Sequence
from ..entities import IOTRecord


class FileParseIOTRecordsClient(ABC):
    @overload
    def parse(self, filename: str) -> Optional[list[IOTRecord]]:
        ...

    @overload
    def parse(self, filename: Sequence[str]) -> list[Optional[list[IOTRecord]]]:
        ...

    @abstractmethod
    def parse(
        self, filename: str | Sequence[str]
    ) -> Optional[list[IOTRecord]] | list[Optional[list[IOTRecord]]]:
        ...

    @abstractmethod
    def parse_stream(self, filename: str) -> Iterator[IOTRecord]:
        ...

    @abstractmethod
    def close(self) -> bool:
        ...
