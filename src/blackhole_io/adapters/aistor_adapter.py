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
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool,
                functools.partial(self._sync_put, file=file),
            )

    async def put_all(self, files: list[BlackholeFile]) -> list[PutResult]:
        pass

    async def get(self, **kwargs) -> BlackholeFile:
        pass

    async def exists(self, **kwargs) -> bool:
        pass

    async def delete(self, **kwargs) -> None:
        pass

    def _sync_put(self, file: BlackholeFile, bucket:str = "default") -> PutResult:
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)

        if isinstance(file.data_to_upload, str):
            result = self.client.fput_object(
                bucket_name=bucket,
                object_name=file.filename,
                file_path=file.data_to_upload,
            )
        else:
            fileobj = file
            if isinstance(file, UploadFile):
                fileobj = file.file
            result = self.client.put_object(
                bucket_name=bucket,
                object_name=file.filename,
                data=fileobj,
                length=file.size,
            )

        logger.info("Uploaded %s to bucket", file.filename)

        return PutResult(
            filename=file.filename,
            hashsum=result.etag,
        )
