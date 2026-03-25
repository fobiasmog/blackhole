import os

import pytest

from blackhole_io.blackhole_file import BlackholeFile


@pytest.mark.asyncio
async def test_delete(adapter, tmp_path):
    data = b"delete me"
    result = await adapter.put(BlackholeFile(filename="test", data_to_upload=data))
    full_path = tmp_path / result.filename
    assert os.path.exists(full_path)
    await adapter.delete(result.filename)
    assert not os.path.exists(full_path)


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
