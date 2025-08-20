import asyncio
from blackhole_io.adapters.abstract import AbstractAdapter

from typing import Union, Any
from io import BytesIO
from blackhole_io.adapters import UploadFileType
import boto3
from botocore.config import Config
from blackhole_io.configs.s3 import S3Config
from starlette.datastructures import UploadFile
from uuid import uuid4

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


    async def put(self, file: UploadFileType, key: str = uuid4().hex,  **kwargs) -> str:
        filename = kwargs.get("Key", key)
        if isinstance(file, str):
            self.client.upload_file(
                Filename=file,
                Bucket=kwargs.get("Bucket", self.config.bucket),
                Key=filename,
                **kwargs
            )
            return filename

        fileobj = file
        if isinstance(file, UploadFile):
            fileobj = file.file

        self.client.upload_fileobj(
            Fileobj=fileobj,
            Bucket=kwargs.get("Bucket", self.config.bucket),
            Key=filename,
            **kwargs
        )
        return filename


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