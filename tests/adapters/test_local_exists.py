import os

import pytest


@pytest.mark.asyncio
async def test_exists_true(adapter):
    data = b"i exist"
    filename = await adapter.put(data)
    basename = os.path.basename(filename)
    assert await adapter.exists(basename) is True


@pytest.mark.asyncio
async def test_exists_false(adapter):
    assert await adapter.exists("nonexistent") is False


@pytest.mark.asyncio
async def test_exists_directory_returns_false(adapter, tmp_path):
    subdir = tmp_path / "adir"
    subdir.mkdir()
    assert await adapter.exists("adir") is False
