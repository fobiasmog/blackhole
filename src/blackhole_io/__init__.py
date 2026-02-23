from typing import Any

from blackhole_io.adapters import UploadFileType
from blackhole_io.adapters.factory import AdapterFactory
from blackhole_io.blackhole_file import BlackholeFile
from blackhole_io.configs import ConfigType


class Blackhole:
    def __init__(self, config: ConfigType) -> None:
        self.config = config
        self.adapter = AdapterFactory.create(config)

    # TODO: injecting methods from adapter during init
    async def put(self, file: UploadFileType) -> Any:
        return await self.adapter.put(file)

    async def put_all(self, files: list[UploadFileType]) -> list[str]:
        return await self.adapter.put_all(files)

    async def get(self, file_name: str) -> BlackholeFile:
        return await self.adapter.get(file_name)

    async def exists(self, file_name: str) -> bool:
        return await self.adapter.exists(file_name)

    async def delete(self, file_name: str) -> None:
        await self.adapter.delete(file_name)
