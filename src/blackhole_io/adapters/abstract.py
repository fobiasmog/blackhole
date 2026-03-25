from abc import ABC, abstractmethod
from typing import Any, NamedTuple

from blackhole_io.blackhole_file import BlackholeFile


class PutResult(NamedTuple):
    filename: str
    hashsum: str


class AbstractAdapter(ABC):
    def __init__(self, config: Any) -> None:
        self.config = config

    @abstractmethod
    async def put(self, file: BlackholeFile) -> PutResult:
        pass

    @abstractmethod
    async def put_all(self, files: list[BlackholeFile]) -> list[PutResult]:
        pass

    @abstractmethod
    async def get(self, **kwargs) -> BlackholeFile:
        pass

    @abstractmethod
    async def exists(self, **kwargs) -> bool:
        pass

    @abstractmethod
    async def delete(self, **kwargs) -> None:
        pass
