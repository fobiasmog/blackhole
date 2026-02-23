import asyncio
import os
from io import BytesIO
from uuid import uuid4

import aiofiles
import aiofiles.os
from starlette.datastructures import UploadFile

from blackhole_io.adapters import UploadFileType
from blackhole_io.adapters.abstract import AbstractAdapter
from blackhole_io.blackhole_file import BlackholeFile


class LocalAdapter(AbstractAdapter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def put(self, file: UploadFileType) -> str:
        dir = self.config.directory
        file_id = str(uuid4())
        filename = os.path.join(dir, file_id)

        if isinstance(file, str):
            async with aiofiles.open(file, "rb") as f:
                data = await f.read()
            async with aiofiles.open(filename, "wb") as out:
                await out.write(data)
        elif isinstance(file, bytes):
            async with aiofiles.open(filename, "wb") as out:
                await out.write(file)
        elif isinstance(file, BytesIO):
            async with aiofiles.open(filename, "wb") as out:
                await out.write(file.getvalue())
        elif isinstance(file, UploadFile):
            filebytes = await file.read()
            async with aiofiles.open(filename, "wb") as out:
                await out.write(filebytes)
        else:
            raise TypeError("Unsupported file type. Must be str, bytes, or BytesIO.")

        return filename

    async def put_all(self, files: list[UploadFileType]) -> list[str]:
        return await asyncio.gather(*[self.put(file) for file in files])

    async def get(self, file_name: str) -> BlackholeFile:
        dir = self.config.directory
        file_path = os.path.join(dir, file_name)

        if not await aiofiles.os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")
        if not await aiofiles.os.path.isfile(file_path):
            raise IsADirectoryError(f"{file_path} is a directory, not a file.")
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"File {file_path} is not readable.")

        async with aiofiles.open(file_path, "rb") as f:
            data = await f.read()

        return BlackholeFile(
            filename=file_name,
            size=len(data),
            data=data,
        )

    async def exists(self, file_name: str) -> bool:
        file_path = os.path.join(self.config.directory, file_name)
        return await aiofiles.os.path.isfile(file_path)

    async def delete(self, file_name: str) -> None:
        dir = self.config.directory
        file_name = os.path.join(dir, file_name)

        if not await aiofiles.os.path.exists(file_name):
            raise FileNotFoundError(f"File {file_name} does not exist.")
        if not await aiofiles.os.path.isfile(file_name):
            raise IsADirectoryError(f"{file_name} is a directory, not a file.")
        if not os.access(file_name, os.W_OK):
            raise PermissionError(f"File {file_name} is not writable.")

        await aiofiles.os.remove(file_name)
