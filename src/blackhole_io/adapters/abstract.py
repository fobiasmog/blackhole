from abc import ABC, abstractmethod
from typing import Any

from blackhole_io.adapters import UploadFileType
from blackhole_io.blackhole_file import BlackholeFile


class AbstractAdapter(ABC):
    def __init__(self, config: Any) -> None:
        self.config = config

    @abstractmethod
    async def put(self, file: UploadFileType) -> str:
        pass

    @abstractmethod
    async def put_all(self, files: list[UploadFileType]) -> list[str]:
        pass

    @abstractmethod
    async def get(self, file_name: str) -> BlackholeFile:
        pass

    @abstractmethod
    async def exists(self, file_name: str) -> bool:
        pass

    @abstractmethod
    async def delete(self, file_name: str) -> None:
        pass
