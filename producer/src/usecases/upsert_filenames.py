from abc import ABC, abstractmethod
from typing import Iterator, overload

class UpsertFilenamesClient(ABC):
    
    @overload    
    def upsert(self, filename: str) -> bool:
        ...
    
    @overload
    def upsert(self, filename: list[str]) -> list[bool]:
        ...
    
    @abstractmethod
    def upsert(self, filename: str | list[str]) -> bool | list[bool]:
        ...
    
    @abstractmethod
    def upsert_stream(self, filename_iterator: Iterator[str]) -> dict[str, bool]:
        ...
    
    @abstractmethod
    def close(self) -> bool:
        ...
    