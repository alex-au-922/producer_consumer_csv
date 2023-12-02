from abc import ABC, abstractmethod
from typing import Generator


class FetchFilenameClient(ABC):
    @abstractmethod
    def fetch(self) -> Generator[str, None, None]:
        ...

    @abstractmethod
    def close(self) -> bool:
        ...
