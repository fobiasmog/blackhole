import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from blackhole_io.store.models import FileRecord, FileRecordInput
from blackhole_io.store.sql_store import SQLStore


@pytest_asyncio.fixture
async def store():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    s = SQLStore(engine=engine)
    await s.create_tables()
    yield s
    await engine.dispose()


@pytest.mark.asyncio
async def test_save_and_get(store):
    record = await store.save(FileRecordInput(filename="test.txt", content_type="text/plain", size=42))
    assert isinstance(record, FileRecord)
    assert record.id is not None
    assert record.filename == "test.txt"
    assert record.content_type == "text/plain"
    assert record.size == 42

    fetched = await store.get("test.txt")
    assert fetched is not None
    assert fetched.id == record.id


@pytest.mark.asyncio
async def test_get_missing(store):
    result = await store.get("nonexistent.txt")
    assert result is None


@pytest.mark.asyncio
async def test_delete(store):
    await store.save(FileRecordInput(filename="to_delete.txt"))
    await store.delete("to_delete.txt")
    assert await store.get("to_delete.txt") is None


@pytest.mark.asyncio
async def test_delete_nonexistent_is_noop(store):
    await store.delete("does_not_exist.txt")


@pytest.mark.asyncio
async def test_save_with_metadata(store):
    meta = {"user_id": 7, "tag": "invoice"}
    await store.save(FileRecordInput(filename="meta.pdf", extra_metadata=meta))
    fetched = await store.get("meta.pdf")
    assert fetched is not None
    assert fetched.extra_metadata == meta


@pytest.mark.asyncio
async def test_create_tables_idempotent(store):
    await store.create_tables()


@pytest.mark.asyncio
async def test_sql_store_requires_engine_or_dsn():
    with pytest.raises(ValueError, match="engine.*dsn"):
        SQLStore()


@pytest.mark.asyncio
async def test_sql_store_from_dsn():
    s = SQLStore(dsn="sqlite+aiosqlite:///:memory:")
    await s.create_tables()
    record = await s.save(FileRecordInput(filename="dsn_test.bin"))
    assert record.filename == "dsn_test.bin"
    await s.engine.dispose()
