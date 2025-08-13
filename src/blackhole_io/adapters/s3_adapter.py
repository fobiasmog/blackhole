from blackhole.adapters.abstract import AbstractAdapter

from typing import Union
from io import BytesIO
from blackhole.adapters import UploadFileType


class S3Adapter(AbstractAdapter):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    async def put(self, file: UploadFileType) -> str:
        print("[S3Adapter] PUT")
        return ""

    async def put_all(self, files: list[UploadFileType]) -> list[str]:
        print("[S3Adapter] PUT ALL")
        return [""] * len(files)

    async def get(self, file_name: str) -> UploadFileType:
        print("[S3Adapter] GET")
        return ""

    async def delete(self, file_name: str) -> None:
        print("[S3Adapter] DELETE")
        pass