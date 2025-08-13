from typing import Union, Any, overload
from io import BytesIO
from abc import ABC, abstractmethod
from starlette.datastructures import UploadFile
from blackhole.adapters import UploadFileType


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
    async def get(self, file_name: str) -> UploadFileType:
        pass

    @abstractmethod
    async def delete(self, file_name: str) -> None:
        pass
