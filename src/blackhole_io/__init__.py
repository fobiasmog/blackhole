import asyncio
import logging
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

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
        upload_filename = filename or uuid4().hex
        content_type = None

        if hasattr(file, "filename") and not filename:
            upload_filename = file.filename or upload_filename
            content_type = file.content_type

        bh_file = BlackholeFile(
            filename=upload_filename,
            content_type=content_type,
            data_to_upload=file,
        )

        result = await self.adapter.put(bh_file)

        logger.info(
            f"Uploading filename: {upload_filename} with content_type: {content_type}"
        )

        if self.store is not None:
            await self.store.save(
                FileRecordInput(
                    filename=result.filename,
                    hashsum=result.hashsum,
                    content_type=content_type,
                    extra_metadata=extra_metadata,
                )
            )
        return result.filename

    async def put_all(
        self,
        files: list[UploadFileType],
        extra_metadata: Optional[list[Optional[dict[str, Any]]]] = None,
    ) -> list[str]:
        files_to_upload = [
            BlackholeFile(filename=uuid4().hex, data_to_upload=f)
            for f in files
        ]
        results = await self.adapter.put_all(files_to_upload)
        if self.store is not None:
            meta_list = extra_metadata or [None] * len(results)
            await asyncio.gather(
                *[
                    self.store.save(
                        FileRecordInput(
                            filename=r.filename,
                            hashsum=r.hashsum,
                            extra_metadata=m,
                        )
                    )
                    for r, m in zip(results, meta_list)
                ]
            )
        return [r.filename for r in results]

    async def get(self, file_name: str) -> BlackholeFile:
        return await self.adapter.get(file_name)

    async def exists(self, file_name: str) -> bool:
        return await self.adapter.exists(file_name)

    async def delete(self, file_name: str) -> None:
        await self.adapter.delete(file_name)
