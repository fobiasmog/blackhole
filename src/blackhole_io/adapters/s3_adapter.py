import asyncio
from blackhole_io.adapters.abstract import AbstractAdapter

from typing import Union, Any, Coroutine, Awaitable, Optional
from io import BytesIO
from blackhole_io.adapters import UploadFileType
import boto3
from botocore.config import Config
from blackhole_io.configs.s3 import S3Config
from starlette.datastructures import UploadFile
from uuid import uuid4
from contextlib import asynccontextmanager, contextmanager
import boto3.session
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


    @contextmanager
    def session(self):
        s = boto3.session.Session()
        client = s.client(
            "s3",
            config=Config(
                signature_version="v4",
                region_name=self.config.region,
            ),
            aws_access_key_id=self.config.access_key,
            aws_secret_access_key=self.config.secret_key,
        )
        try:
            yield client
        except Exception as e:
            print(f"[S3Adapter] Error: {e}")
            # await s.close()
        # finally:
        #     await s.close()


    async def put(self, file: UploadFileType, key: Optional[str] = None,  **kwargs) -> str:
        key = kwargs.get("Key") or key or uuid4().hex
        print(f"[S3Adapter] Uploading {key} to bucket")
        # return self._sync_put(file, key, **kwargs)
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, self._sync_put, file, key, **kwargs)


    async def put_all(self, files: list[UploadFileType], **kwargs) -> list[Any]:
        # for file in files:
        #     key = kwargs.get("Key") or key or uuid4().hex
        #     await self.put(file=file, key=key, **kwargs)
        # return [
        #     await self.put(file=file, **kwargs) for file in files
        # ]

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
        with self.session() as s3_session:
            # bucket = s3.Bucket(self.config.bucket)
            # obj = s3.Object(self.config.bucket, key)
            if isinstance(file, str):
                s3_session.upload_file(
                    Filename=file,
                    Bucket=kwargs.get("Bucket", self.config.bucket),
                    Key=key,
                    **kwargs
                )
                return key

            fileobj = file
            if isinstance(file, UploadFile):
                fileobj = file.file

            s3_session.upload_fileobj(
                Fileobj=fileobj,
                Bucket=kwargs.get("Bucket", self.config.bucket),
                Key=key,
                **kwargs
            )
            # obj.upload_fileobj(fileobj, **kwargs)
            print(f"[S3Adapter] Uploaded {key} to bucket")
            return key
