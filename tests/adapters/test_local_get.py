import os

import pytest


@pytest.mark.asyncio
async def test_get(adapter):
    data = b"get me"
    filename = await adapter.put(data)
    basename = os.path.basename(filename)
    result = await adapter.get(basename)
    assert result.filename == basename
    assert result.blob == data
    assert result.size == len(data)


@pytest.mark.asyncio
async def test_get_content_type_default(adapter):
    filename = await adapter.put(b"data")
    basename = os.path.basename(filename)
    result = await adapter.get(basename)
    assert result.content_type == "application/octet-stream"


@pytest.mark.asyncio
async def test_get_not_found(adapter):
    with pytest.raises(FileNotFoundError):
        await adapter.get("nonexistent")


@pytest.mark.asyncio
async def test_get_directory(adapter, tmp_path):
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    with pytest.raises(IsADirectoryError):
        await adapter.get("subdir")


@pytest.mark.asyncio
async def test_get_not_readable(adapter, tmp_path):
    target = tmp_path / "noperm"
    target.write_bytes(b"secret")
    target.chmod(0o000)
    try:
        with pytest.raises(PermissionError):
            await adapter.get("noperm")
    finally:
        target.chmod(0o644)
