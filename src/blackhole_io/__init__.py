import asyncio
import logging
from uuid import uuid4
from pathlib import Path
from typing import Any, Optional

from blackhole_io.adapters import UploadFileType
from blackhole_io.adapters.factory import AdapterFactory
from blackhole_io.blackhole_file import BlackholeFile
from blackhole_io.configs import ConfigType
from blackhole_io.configs.loader import load_config_with_store
from blackhole_io.store.abstract import AbstractStore
from blackhole_io.store.models import FileRecordInput

logger = logging.getLogger("blackhole_io")
logger.setLevel(logging.ERROR)


class Blackhole:
    def __init__(
        self,
        config: Optional[ConfigType | str | Path] = None,
        log_level: Optional[int] = None,
        store: Optional[AbstractStore] = None,
    ) -> None:
        if log_level is not None:
            logger.setLevel(log_level)
            if not logger.handlers:
                logger.addHandler(logging.StreamHandler())

        file_config, yaml_store = load_config_with_store(config)
        self.config = file_config
        self.adapter = AdapterFactory.create(self.config)
        self.store = store if store is not None else yaml_store

    # TODO: return BlackholeFile
    async def put(
        self,
        file: UploadFileType,
        filename: Optional[str] = None,
        extra_metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        upload_filename = None
        content_type = None

        if file.__class__.__name__ == "UploadFile":
            upload_filename = file.filename
            content_type = file.content_type

        upload_filename = upload_filename or filename or uuid4().hex
        content_type = content_type or None

        bh_file = BlackholeFile(
            filename=upload_filename,
            content_type=content_type,
            data_to_upload=file,
        )

        filename = await self.adapter.put(bh_file)

        logger.info(
            f"Uploading filename: {upload_filename} ",
            f"with content_type: {content_type}" if content_type else "",
        )

        if self.store is not None:
            await self.store.save(
                FileRecordInput(filename=filename, content_type=content_type, extra_metadata=extra_metadata)
            )
        return filename

    async def put_all(
        self,
        files: list[UploadFileType],
        extra_metadata: Optional[list[Optional[dict[str, Any]]]] = None,
    ) -> list[str]:
        files_to_upload = [
            BlackholeFile(filename=uuid4().hex, data_to_upload=f)
            for f in files
        ]
        filenames = await self.adapter.put_all(files_to_upload)
        if self.store is not None:
            meta_list = extra_metadata or [None] * len(filenames)
            await asyncio.gather(
                *[
                    self.store.save(
                        FileRecordInput(filename=fn, extra_metadata=m)
                    )
                    for fn, m in zip(filenames, meta_list)
                ]
            )
        return filenames

    async def get(self, file_name: str) -> BlackholeFile:
        return await self.adapter.get(file_name)

    async def exists(self, file_name: str) -> bool:
        return await self.adapter.exists(file_name)

    async def delete(self, file_name: str) -> None:
        await self.adapter.delete(file_name)
