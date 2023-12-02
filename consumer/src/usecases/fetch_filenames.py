from abc import ABC, abstractmethod
from typing import Iterator


class FetchFilenameClient(ABC):
    @abstractmethod
    def fetch(self) -> Iterator[str]:
        ...

    @abstractmethod
    def close(self) -> bool:
        ...
