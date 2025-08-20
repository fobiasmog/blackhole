from blackhole_io.adapters.factory import AdapterFactory
from blackhole_io.configs import ConfigType
from blackhole_io.adapters import UploadFileType
from blackhole_io.adapters.abstract import AbstractAdapter

from typing import Any

class Blackhole(AbstractAdapter):
    def __init__(self, config: ConfigType) -> None:
        self.config = config
        self.adapter = AdapterFactory.create(config)

    # TODO: injecting methods from adapter during init
    async def put(self, file: UploadFileType) -> Any:
        return await self.adapter.put(file)

    async def put_all(self, files: list[UploadFileType]) -> list[str]:
        return await self.adapter.put_all(files)

    async def get(self, file_name: str) -> UploadFileType:
        return await self.adapter.get(file_name)

    async def delete(self, file_name: str) -> None:
        await self.adapter.delete(file_name)
