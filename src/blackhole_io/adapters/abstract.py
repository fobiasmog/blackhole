from abc import ABC, abstractmethod
from typing import Any

from blackhole_io.blackhole_file import BlackholeFile


class AbstractAdapter(ABC):
    def __init__(self, config: Any) -> None:
        self.config = config

    # TODO: return BlackholeFile
    @abstractmethod
    async def put(self, **kwargs) -> str:
        pass

    # TODO: return list of BlackholeFile
    @abstractmethod
    async def put_all(self, **kwargs) -> list[str]:
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
