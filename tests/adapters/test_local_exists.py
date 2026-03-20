import os

import pytest

from blackhole_io.blackhole_file import BlackholeFile


@pytest.mark.asyncio
async def test_exists_true(adapter):
    data = b"i exist"
    filename = await adapter.put(BlackholeFile(filename="test", data_to_upload=data))
    assert await adapter.exists(filename) is True


@pytest.mark.asyncio
async def test_exists_false(adapter):
    assert await adapter.exists("nonexistent") is False


@pytest.mark.asyncio
async def test_exists_directory_returns_false(adapter, tmp_path):
    subdir = tmp_path / "adir"
    subdir.mkdir()
    assert await adapter.exists("adir") is False
