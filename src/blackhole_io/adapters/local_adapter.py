import asyncio
from pathlib import Path
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
        directory = Path(self.config.directory)
        file_id = str(uuid4())

        if isinstance(file, str):
            ext = Path(file).suffix
            filename = directory / (file_id + ext)
            async with aiofiles.open(file, "rb") as f:
                data = await f.read()
            async with aiofiles.open(filename, "wb") as out:
                await out.write(data)
        elif isinstance(file, bytes):
            filename = directory / file_id
            async with aiofiles.open(filename, "wb") as out:
                await out.write(file)
        elif isinstance(file, BytesIO):
            ext = Path(file.name).suffix if getattr(file, "name", None) else ""
            filename = directory / (file_id + ext)
            async with aiofiles.open(filename, "wb") as out:
                await out.write(file.getvalue())
        elif isinstance(file, UploadFile):
            ext = Path(file.filename).suffix if file.filename else ""
            filename = directory / (file_id + ext)
            filebytes = await file.read()
            async with aiofiles.open(filename, "wb") as out:
                await out.write(filebytes)
        else:
            raise TypeError("Unsupported file type. Must be str, bytes, or BytesIO.")

        return str(filename)

    async def put_all(self, files: list[UploadFileType]) -> list[str]:
        return await asyncio.gather(*[self.put(file) for file in files])

    async def get(self, file_name: str) -> BlackholeFile:
        file_path = Path(self.config.directory) / file_name

        if not await aiofiles.os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")
        if not await aiofiles.os.path.isfile(file_path):
            raise IsADirectoryError(f"{file_path} is a directory, not a file.")
        if not file_path.stat().st_mode & 0o444:
            raise PermissionError(f"File {file_path} is not readable.")

        async with aiofiles.open(file_path, "rb") as f:
            data = await f.read()

        return BlackholeFile(
            filename=file_name,
            size=len(data),
            data=data,
        )

    async def exists(self, file_name: str) -> bool:
        file_path = Path(self.config.directory) / file_name
        return await aiofiles.os.path.isfile(file_path)

    async def delete(self, file_name: str) -> None:
        file_path = Path(self.config.directory) / file_name

        if not await aiofiles.os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")
        if not await aiofiles.os.path.isfile(file_path):
            raise IsADirectoryError(f"{file_path} is a directory, not a file.")
        if not file_path.stat().st_mode & 0o222:
            raise PermissionError(f"File {file_path} is not writable.")

        await aiofiles.os.remove(file_path)
