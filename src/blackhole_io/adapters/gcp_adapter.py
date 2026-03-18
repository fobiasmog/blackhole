import logging

from blackhole_io.adapters import UploadFileType
from blackhole_io.adapters.abstract import AbstractAdapter
from blackhole_io.blackhole_file import BlackholeFile

logger = logging.getLogger(__name__)


class GCPAdapter(AbstractAdapter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def put(self, file: UploadFileType) -> str:
        logger.info("PUT")
        return ""

    async def put_all(self, files: list[UploadFileType]) -> list[str]:
        logger.info("PUT ALL")
        return [""] * len(files)

    async def get(self, file_name: str) -> BlackholeFile:
        logger.info("GET")
        return BlackholeFile(filename=file_name)

    async def exists(self, file_name: str) -> bool:
        logger.info("EXISTS")
        return False

    async def delete(self, file_name: str) -> None:
        logger.info("DELETE")
