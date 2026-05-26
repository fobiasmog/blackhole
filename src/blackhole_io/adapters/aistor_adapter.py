import asyncio
import concurrent.futures
import functools
import logging
from typing import Any

import boto3
from botocore.config import Config
from starlette.datastructures import UploadFile

from blackhole_io.adapters.abstract import AbstractAdapter, PutResult
from blackhole_io.blackhole_file import BlackholeFile
from blackhole_io.configs.aistore import AIStoreConfig
from blackhole_io.types import UploadFileType
from minio import Minio

logger = logging.getLogger(__name__)

class AIStoreAdapter(AbstractAdapter):
    def __init__(self, config: Any) -> None:
        self.config = config

    async def put(self, file: BlackholeFile) -> PutResult:
        pass

    async def put_all(self, files: list[BlackholeFile]) -> list[PutResult]:
        pass

    async def get(self, **kwargs) -> BlackholeFile:
        pass

    async def exists(self, **kwargs) -> bool:
        pass

    async def delete(self, **kwargs) -> None:
        pass
