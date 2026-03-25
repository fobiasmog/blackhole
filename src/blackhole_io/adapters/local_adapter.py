import asyncio
import hashlib
from io import BytesIO
from pathlib import Path

import aiofiles
import aiofiles.os
from starlette.datastructures import UploadFile

from blackhole_io.adapters.abstract import AbstractAdapter, PutResult
from blackhole_io.blackhole_file import BlackholeFile

# TODO: add support for directory structure - now put supports only flat structure

class LocalAdapter(AbstractAdapter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def put(self, file: BlackholeFile) -> PutResult:
        directory = Path(self.config.directory)
        file_id = file.filename
        data_to_upload = file.data_to_upload

        if isinstance(data_to_upload, str):
            filename = directory / (file_id + Path(data_to_upload).suffix)
        else:
            # for UploadFile we probably have a correct content type even if its no extension at all
            # bytes and BytesIO just rely on file_id to determine the extension
            filename = directory / file_id

        if isinstance(data_to_upload, str):
            async with aiofiles.open(data_to_upload, "rb") as f:
                data = await f.read()
        elif isinstance(data_to_upload, bytes):
            data = data_to_upload
        elif isinstance(data_to_upload, BytesIO):
            data = data_to_upload.getvalue()
        elif isinstance(data_to_upload, UploadFile):
            data = await data_to_upload.read()
        else:
            raise TypeError("Unsupported file type. Must be str, bytes, BytesIO or UploadFile.")

        async with aiofiles.open(filename, "wb") as out:
            await out.write(data)

        hashsum = hashlib.sha256(data).hexdigest()
        return PutResult(filename=filename.name, hashsum=hashsum)

    async def put_all(self, files: list[BlackholeFile]) -> list[str]:
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
