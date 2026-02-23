import os
from io import BytesIO

import pytest
import pytest_asyncio
from starlette.datastructures import UploadFile

from blackhole_io.adapters.local_adapter import LocalAdapter
from blackhole_io.configs.local import LocalConfig


@pytest_asyncio.fixture
async def adapter(tmp_path):
    config = LocalConfig(directory=str(tmp_path))
    return LocalAdapter(config)


@pytest.mark.asyncio
async def test_put_bytes(adapter, tmp_path):
    data = b"hello bytes"
    filename = await adapter.put(data)
    assert os.path.exists(filename)
    with open(filename, "rb") as f:
        assert f.read() == data


@pytest.mark.asyncio
async def test_put_bytesio(adapter, tmp_path):
    data = b"hello bytesio"
    filename = await adapter.put(BytesIO(data))
    assert os.path.exists(filename)
    with open(filename, "rb") as f:
        assert f.read() == data


@pytest.mark.asyncio
async def test_put_str_path(adapter, tmp_path):
    source = tmp_path / "source.txt"
    source.write_bytes(b"hello file path")
    filename = await adapter.put(str(source))
    assert os.path.exists(filename)
    with open(filename, "rb") as f:
        assert f.read() == b"hello file path"


@pytest.mark.asyncio
async def test_put_upload_file(adapter, tmp_path):
    data = b"hello upload"
    upload = UploadFile(file=BytesIO(data), filename="test.txt")
    filename = await adapter.put(upload)
    assert os.path.exists(filename)
    with open(filename, "rb") as f:
        assert f.read() == data


@pytest.mark.asyncio
async def test_put_unsupported_type(adapter):
    with pytest.raises(TypeError):
        await adapter.put(12345)


@pytest.mark.asyncio
async def test_put_all(adapter, tmp_path):
    files = [b"file1", b"file2", b"file3"]
    filenames = await adapter.put_all(files)
    assert len(filenames) == 3
    for i, fname in enumerate(filenames):
        with open(fname, "rb") as f:
            assert f.read() == files[i]


@pytest.mark.asyncio
async def test_get(adapter, tmp_path):
    data = b"get me"
    filename = await adapter.put(data)
    basename = os.path.basename(filename)
    result = await adapter.get(basename)
    assert result.filename == basename
    assert result.blob == data
    assert result.size == len(data)


@pytest.mark.asyncio
async def test_get_not_found(adapter):
    with pytest.raises(FileNotFoundError):
        await adapter.get("nonexistent")


@pytest.mark.asyncio
async def test_exists_true(adapter, tmp_path):
    data = b"i exist"
    filename = await adapter.put(data)
    basename = os.path.basename(filename)
    assert await adapter.exists(basename) is True


@pytest.mark.asyncio
async def test_exists_false(adapter):
    assert await adapter.exists("nonexistent") is False


@pytest.mark.asyncio
async def test_delete(adapter, tmp_path):
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
