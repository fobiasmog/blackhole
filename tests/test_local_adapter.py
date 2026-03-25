import os
from io import BytesIO

import pytest
import pytest_asyncio
from starlette.datastructures import UploadFile

from blackhole_io.adapters.local_adapter import LocalAdapter
from blackhole_io.blackhole_file import BlackholeFile
from blackhole_io.configs.local import LocalConfig


@pytest_asyncio.fixture
async def adapter(tmp_path):
    config = LocalConfig(directory=str(tmp_path))
    return LocalAdapter(config)


@pytest.mark.asyncio
async def test_put_bytes(adapter, tmp_path):
    data = b"hello bytes"
    file = BlackholeFile(filename="test", data_to_upload=data)
    result = await adapter.put(file)
    assert os.path.exists(tmp_path / result.filename)
    with open(tmp_path / result.filename, "rb") as f:
        assert f.read() == data


@pytest.mark.asyncio
async def test_put_bytesio(adapter, tmp_path):
    data = b"hello bytesio"
    file = BlackholeFile(filename="test", data_to_upload=BytesIO(data))
    result = await adapter.put(file)
    assert os.path.exists(tmp_path / result.filename)
    with open(tmp_path / result.filename, "rb") as f:
        assert f.read() == data


@pytest.mark.asyncio
async def test_put_str_path(adapter, tmp_path):
    source = tmp_path / "source.txt"
    source.write_bytes(b"hello file path")
    file = BlackholeFile(filename="test", data_to_upload=str(source))
    result = await adapter.put(file)
    assert os.path.exists(tmp_path / result.filename)
    with open(tmp_path / result.filename, "rb") as f:
        assert f.read() == b"hello file path"


@pytest.mark.asyncio
async def test_put_upload_file(adapter, tmp_path):
    data = b"hello upload"
    upload = UploadFile(file=BytesIO(data), filename="test.txt")
    file = BlackholeFile(filename="test.txt", data_to_upload=upload)
    result = await adapter.put(file)
    assert os.path.exists(tmp_path / result.filename)
    with open(tmp_path / result.filename, "rb") as f:
        assert f.read() == data


@pytest.mark.asyncio
async def test_put_unsupported_type(adapter):
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        BlackholeFile(filename="test", data_to_upload=12345)


@pytest.mark.asyncio
async def test_put_all(adapter, tmp_path):
    raw_files = [b"file1", b"file2", b"file3"]
    files = [BlackholeFile(filename=f"f{i}", data_to_upload=d) for i, d in enumerate(raw_files)]
    results = await adapter.put_all(files)
    assert len(results) == 3
    for i, result in enumerate(results):
        with open(tmp_path / result.filename, "rb") as f:
            assert f.read() == raw_files[i]


@pytest.mark.asyncio
async def test_get(adapter, tmp_path):
    data = b"get me"
    file = BlackholeFile(filename="test", data_to_upload=data)
    put_result = await adapter.put(file)
    result = await adapter.get(put_result.filename)
    assert result.filename == put_result.filename
    assert result.blob == data
    assert result.size == len(data)


@pytest.mark.asyncio
async def test_get_not_found(adapter):
    with pytest.raises(FileNotFoundError):
        await adapter.get("nonexistent")


@pytest.mark.asyncio
async def test_exists_true(adapter, tmp_path):
    data = b"i exist"
    file = BlackholeFile(filename="test", data_to_upload=data)
    result = await adapter.put(file)
    assert await adapter.exists(result.filename) is True


@pytest.mark.asyncio
async def test_exists_false(adapter):
    assert await adapter.exists("nonexistent") is False


@pytest.mark.asyncio
async def test_delete(adapter, tmp_path):
    data = b"delete me"
    file = BlackholeFile(filename="test", data_to_upload=data)
    result = await adapter.put(file)
    full_path = tmp_path / result.filename
    assert os.path.exists(full_path)
    await adapter.delete(result.filename)
    assert not os.path.exists(full_path)


@pytest.mark.asyncio
async def test_delete_not_found(adapter):
    with pytest.raises(FileNotFoundError):
        await adapter.delete("nonexistent")
