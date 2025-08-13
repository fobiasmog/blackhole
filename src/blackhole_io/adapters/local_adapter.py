from typing import Union
from io import BytesIO
from blackhole.adapters.abstract import AbstractAdapter
from blackhole.configs.local import LocalConfig
from pathlib import Path
import os
from uuid import uuid4
from starlette.datastructures import UploadFile
from blackhole.adapters import UploadFileType
import asyncio

class LocalAdapter(AbstractAdapter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


    async def put(self, file: UploadFileType) -> str:
        dir = self.config.directory
        file_id = str(uuid4())
        filename = os.path.join(dir, file_id)

        if isinstance(file, str):
            with open(file, "rb") as f:
                data = f.read()
                with open(filename, "wb") as out:
                    out.write(data)
        elif isinstance(file, bytes):
            with open(filename, "wb") as out:
                out.write(file)
        elif isinstance(file, BytesIO):
            with open(filename, "wb") as out:
                out.write(file.getvalue())
        elif isinstance(file, UploadFile):
            filebytes = await file.read()
            with open(filename, "wb") as out:
                out.write(filebytes)
        else:
            raise TypeError("Unsupported file type. Must be str, bytes, or BytesIO.")

        return filename


    async def put_all(self, files: list[UploadFileType]) -> list[str]:
        return await asyncio.gather(
            *[self.put(file) for file in files]
        )


    async def get(self, file_name: str) -> bytes:
        dir = self.config.directory
        file_name = os.path.join(dir, file_name)

        if not os.path.exists(file_name):
            raise FileNotFoundError(f"File {file_name} does not exist.")
        if not os.path.isfile(file_name):
            raise IsADirectoryError(f"{file_name} is a directory, not a file.")
        if not os.access(file_name, os.R_OK):
            raise PermissionError(f"File {file_name} is not readable.")

        with open(file_name, "rb") as f:
            data = f.read()
            return data


    async def delete(self, file_name: str) -> None:
        dir = self.config.directory
        file_name = os.path.join(dir, file_name)

        if not os.path.exists(file_name):
            raise FileNotFoundError(f"File {file_name} does not exist.")
        if not os.path.isfile(file_name):
            raise IsADirectoryError(f"{file_name} is a directory, not a file.")
        if not os.access(file_name, os.W_OK):
            raise PermissionError(f"File {file_name} is not writable.")

        os.remove(file_name)
