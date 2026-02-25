from pathlib import Path
from typing import Any, Optional

from blackhole_io.adapters import UploadFileType
from blackhole_io.adapters.factory import AdapterFactory
from blackhole_io.blackhole_file import BlackholeFile
from blackhole_io.configs import ConfigType
from blackhole_io.configs.loader import load_config


class Blackhole:
    def __init__(self, config: Optional[ConfigType | str | Path] = None) -> None:
        self.config = load_config(config)
        self.adapter = AdapterFactory.create(self.config)

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
