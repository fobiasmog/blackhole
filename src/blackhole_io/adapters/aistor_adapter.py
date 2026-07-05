import asyncio
import concurrent.futures
import functools
import logging

from minio import Minio
from starlette.datastructures import UploadFile

from blackhole_io.adapters.abstract import AbstractAdapter, PutResult
from blackhole_io.blackhole_file import BlackholeFile
from blackhole_io.configs.aistore import AIStoreConfig

logger = logging.getLogger(__name__)

class AIStoreAdapter(AbstractAdapter):
    def __init__(self, config: AIStoreConfig) -> None:
        super().__init__(config)
        self.client = Minio(
            endpoint=self.config.endpoint,
            access_key=self.config.access_key,
            secret_key=self.config.secret_key,
            secure=self.config.secure,
        )

    async def put(self, file: BlackholeFile) -> PutResult:
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool,
                functools.partial(self._sync_put, file=file),
            )

    async def put_all(self, files: list[BlackholeFile]) -> list[PutResult]:
        return await asyncio.gather(
            *[self.put(file=file) for file in files],
        )

    async def get(self, key: str) -> BlackholeFile:
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool,
                functools.partial(self._sync_get, key),
            )

    async def exists(self, key: str) -> bool:
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool,
                functools.partial(self._sync_exists, key),
            )

    async def delete(self, key: str) -> None:
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool,
                functools.partial(self._sync_delete, key),
            )

    def _sync_get(self, key: str) -> BlackholeFile:
        try:
            response = self.client.get_object(
                bucket_name=self.config.bucket,
                object_name=key,
            )
        finally:
            response.close()
            response.release_conn()

        return BlackholeFile(
            filename=key,
            content_type=response.get("ContentType", "application/octet-stream"),
            size=response.get("ContentLength", 0),
            data=response.data,
        )

    def _sync_put(self, file: BlackholeFile, bucket:str = "default") -> PutResult:
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)

        if isinstance(file.data_to_upload, str):
            result = self.client.fput_object(
                bucket_name=bucket,
                object_name=file.filename,
                file_path=file.data_to_upload,
                content_type=file.content_type,
                metadata=file.extra,
            )
        else:
            fileobj = file.data_to_upload
            if isinstance(fileobj, UploadFile):
                fileobj = fileobj.file

            result = self.client.put_object(
                bucket_name=bucket,
                object_name=file.filename,
                data=fileobj,
                length=file.size,
                content_type=file.content_type,
                metadata=file.extra,
            )

        logger.info("Uploaded %s to bucket", file.filename)

        return PutResult(
            filename=file.filename,
            hashsum=result.etag,
        )

    def _sync_exists(self, key: str) -> bool:
        try:
            self.client.stat_object(
                bucket_name=self.config.bucket,
                object_name=key,
            )
            return True
        except Exception:
            return False

    def _sync_delete(self, key: str) -> None:
        self.client.remove_object(
            bucket_name=self.config.bucket,
            object_name=key,
        )

