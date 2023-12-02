from abc import ABC, abstractmethod
from typing import overload, Sequence
from entities import IOTRecord


class UpsertIOTRecordsClient(ABC):
    @overload
    def upsert(self, iot_record: IOTRecord) -> bool:
        ...

    @overload
    def upsert(self, iot_record: Sequence[IOTRecord]) -> list[bool]:
        ...

    @abstractmethod
    def upsert(self, iot_record: IOTRecord | Sequence[IOTRecord]) -> bool | list[bool]:
        ...

    @abstractmethod
    def close(self) -> bool:
        ...
