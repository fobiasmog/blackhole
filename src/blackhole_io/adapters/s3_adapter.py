import asyncio
import functools
from blackhole_io.adapters.abstract import AbstractAdapter

from typing import Union, Any, Coroutine, Awaitable, Optional
from io import BytesIO
from blackhole_io.adapters import UploadFileType
import boto3
from botocore.config import Config
from blackhole_io.configs.s3 import S3Config
from starlette.datastructures import UploadFile
from uuid import uuid4
import concurrent.futures


class S3Adapter(AbstractAdapter):
    def __init__(self, config: S3Config, **kwargs) -> None:
        self.config = config
        self.client = boto3.client(
            "s3",
            config=Config(
                signature_version="v4",
                region_name=config.region,
            ),
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
        )


    async def put(self, file: UploadFileType, key: Optional[str] = None,  **kwargs) -> str:
        key = kwargs.get("Key") or key or uuid4().hex
        print(f"[S3Adapter] Uploading {key} to bucket")
        # return self._sync_put(file, key, **kwargs)
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, functools.partial(self._sync_put, file, key, **kwargs))


    async def put_all(self, files: list[UploadFileType], **kwargs) -> list[Any]:
        return await asyncio.gather(
            *[self.put(file=file,**kwargs) for file in files],
        )


    async def get(self, file_name: str) -> UploadFileType:
        print("[S3Adapter] GET")
        return ""


    async def delete(self, file_name: str) -> None:
        print("[S3Adapter] DELETE")
        pass


    def _sync_put(self, file: UploadFileType, key: str,  **kwargs) -> str:
        bucket = kwargs.pop("Bucket", self.config.bucket)
        kwargs.pop("Key", None)

        if isinstance(file, str):
            self.client.upload_file(
                Filename=file,
                Bucket=bucket,
                Key=key,
                **kwargs
            )
            return key

        fileobj = file
        if isinstance(file, UploadFile):
            fileobj = file.file

        self.client.upload_fileobj(
            Fileobj=fileobj,
            Bucket=bucket,
            Key=key,
            **kwargs
        )
        print(f"[S3Adapter] Uploaded {key} to bucket")
        return key
