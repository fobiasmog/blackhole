import asyncio
import concurrent.futures
import functools
from typing import Any, Optional
from uuid import uuid4

import boto3
from botocore.config import Config
from starlette.datastructures import UploadFile

from blackhole_io.adapters import UploadFileType
from blackhole_io.adapters.abstract import AbstractAdapter
from blackhole_io.blackhole_file import BlackholeFile
from blackhole_io.configs.s3 import S3Config


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

    async def put(
        self, file: UploadFileType, key: Optional[str] = None, **kwargs
    ) -> str:
        key = kwargs.get("Key") or key or uuid4().hex
        print(f"[S3Adapter] Uploading {key} to bucket")
        # return self._sync_put(file, key, **kwargs)
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, functools.partial(self._sync_put, file, key, **kwargs)
            )

    async def put_all(self, files: list[UploadFileType], **kwargs) -> list[Any]:
        return await asyncio.gather(
            *[self.put(file=file, **kwargs) for file in files],
        )

    async def get(self, file_name: str) -> BlackholeFile:
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, functools.partial(self._sync_get, file_name)
            )

    async def exists(self, file_name: str) -> bool:
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, functools.partial(self._sync_exists, file_name)
            )

    async def delete(self, file_name: str) -> None:
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool, functools.partial(self._sync_delete, file_name)
            )

    def _sync_get(self, file_name: str) -> BlackholeFile:
        response = self.client.get_object(
            Bucket=self.config.bucket,
            Key=file_name,
        )
        data = response["Body"].read()
        content_type = response.get("ContentType", "application/octet-stream")
        size = response.get("ContentLength", len(data))

        return BlackholeFile(
            filename=file_name,
            content_type=content_type,
            size=size,
            data=data,
        )

    def _sync_exists(self, file_name: str) -> bool:
        try:
            self.client.head_object(
                Bucket=self.config.bucket,
                Key=file_name,
            )
            return True
        except Exception:
            return False

    def _sync_delete(self, file_name: str) -> None:
        self.client.delete_object(
            Bucket=self.config.bucket,
            Key=file_name,
        )

    def _sync_put(self, file: UploadFileType, key: str, **kwargs) -> str:
        bucket = kwargs.pop("Bucket", self.config.bucket)
        kwargs.pop("Key", None)

        if isinstance(file, str):
            self.client.upload_file(Filename=file, Bucket=bucket, Key=key, **kwargs)
            return key

        fileobj = file
        if isinstance(file, UploadFile):
            fileobj = file.file

        self.client.upload_fileobj(Fileobj=fileobj, Bucket=bucket, Key=key, **kwargs)
        print(f"[S3Adapter] Uploaded {key} to bucket")
        return key
