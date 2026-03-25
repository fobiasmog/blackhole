from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from blackhole_io.store.abstract import AbstractStore
from blackhole_io.store.models import FileRecord, FileRecordInput


class SQLStore(AbstractStore):
    def __init__(
        self,
        engine: Optional[AsyncEngine] = None,
        dsn: Optional[str] = None,
    ) -> None:
        if engine is None and dsn is None:
            raise ValueError("SQLStore requires either 'engine' or 'dsn'")
        self._engine = engine or create_async_engine(dsn, echo=False)

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    async def save(self, record: FileRecordInput) -> FileRecord:
        async with AsyncSession(self._engine) as session:
            result = await session.exec(
                select(FileRecord).where(FileRecord.hashsum == record.hashsum)
            )
            existing = result.first()

            if existing is not None:
                existing.filename = record.filename
                existing.content_type = record.content_type
                existing.size = record.size
                existing.extra_metadata = record.extra_metadata
                existing.updated_at = datetime.now(timezone.utc)
                session.add(existing)
                await session.commit()
                await session.refresh(existing)
                return existing

            db_record = FileRecord(
                filename=record.filename,
                hashsum=record.hashsum,
                content_type=record.content_type,
                size=record.size,
                extra_metadata=record.extra_metadata,
            )
            session.add(db_record)
            await session.commit()
            await session.refresh(db_record)
            return db_record

    async def get(self, filename: str) -> Optional[FileRecord]:
        async with AsyncSession(self._engine) as session:
            result = await session.exec(
                select(FileRecord).where(FileRecord.filename == filename)
            )
            return result.first()

    async def delete(self, filename: str) -> None:
        async with AsyncSession(self._engine) as session:
            result = await session.exec(
                select(FileRecord).where(FileRecord.filename == filename)
            )
            record = result.first()
            if record is not None:
                await session.delete(record)
                await session.commit()

    async def create_tables(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
