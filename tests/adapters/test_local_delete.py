import os

import pytest


@pytest.mark.asyncio
async def test_delete(adapter):
    data = b"delete me"
    filename = await adapter.put(data)
    basename = os.path.basename(filename)
    assert os.path.exists(filename)
    await adapter.delete(basename)
    assert not os.path.exists(filename)


@pytest.mark.asyncio
async def test_delete_not_found(adapter):
    with pytest.raises(FileNotFoundError):
        await adapter.delete("nonexistent")


@pytest.mark.asyncio
async def test_delete_directory(adapter, tmp_path):
    subdir = tmp_path / "adir"
    subdir.mkdir()
    with pytest.raises(IsADirectoryError):
        await adapter.delete("adir")


@pytest.mark.asyncio
async def test_delete_not_writable(adapter, tmp_path):
    target = tmp_path / "readonly"
    target.write_bytes(b"locked")
    target.chmod(0o444)
    try:
        with pytest.raises(PermissionError):
            await adapter.delete("readonly")
    finally:
        target.chmod(0o644)
