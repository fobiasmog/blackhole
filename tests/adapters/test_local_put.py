import os
from io import BytesIO
from pathlib import Path

import pytest
from starlette.datastructures import UploadFile


@pytest.mark.asyncio
async def test_put_bytes(adapter):
    data = b"hello bytes"
    filename = await adapter.put(data)
    assert os.path.exists(filename)
    with open(filename, "rb") as f:
        assert f.read() == data


@pytest.mark.asyncio
async def test_put_bytes_no_extension(adapter):
    filename = await adapter.put(b"raw")
    assert Path(filename).suffix == ""


@pytest.mark.asyncio
async def test_put_bytesio(adapter):
    data = b"hello bytesio"
    filename = await adapter.put(BytesIO(data))
    assert os.path.exists(filename)
    with open(filename, "rb") as f:
        assert f.read() == data


@pytest.mark.asyncio
async def test_put_bytesio_preserves_extension(adapter):
    buf = BytesIO(b"data")
    buf.name = "report.csv"
    filename = await adapter.put(buf)
    assert Path(filename).suffix == ".csv"


@pytest.mark.asyncio
async def test_put_bytesio_no_name(adapter):
    filename = await adapter.put(BytesIO(b"no name"))
    assert Path(filename).suffix == ""


@pytest.mark.asyncio
async def test_put_str_path(adapter, tmp_path):
    source = tmp_path / "source.txt"
    source.write_bytes(b"hello file path")
    filename = await adapter.put(str(source))
    assert os.path.exists(filename)
    with open(filename, "rb") as f:
        assert f.read() == b"hello file path"


@pytest.mark.asyncio
async def test_put_str_path_preserves_extension(adapter, tmp_path):
    source = tmp_path / "image.png"
    source.write_bytes(b"png data")
    filename = await adapter.put(str(source))
    assert Path(filename).suffix == ".png"


@pytest.mark.asyncio
async def test_put_str_path_no_extension(adapter, tmp_path):
    source = tmp_path / "noext"
    source.write_bytes(b"data")
    filename = await adapter.put(str(source))
    assert Path(filename).suffix == ""


@pytest.mark.asyncio
async def test_put_upload_file(adapter):
    data = b"hello upload"
    upload = UploadFile(file=BytesIO(data), filename="test.txt")
    filename = await adapter.put(upload)
    assert os.path.exists(filename)
    with open(filename, "rb") as f:
        assert f.read() == data


@pytest.mark.asyncio
async def test_put_upload_file_preserves_extension(adapter):
    upload = UploadFile(file=BytesIO(b"img"), filename="photo.jpg")
    filename = await adapter.put(upload)
    assert Path(filename).suffix == ".jpg"


@pytest.mark.asyncio
async def test_put_upload_file_no_filename(adapter):
    upload = UploadFile(file=BytesIO(b"anon"))
    filename = await adapter.put(upload)
    assert Path(filename).suffix == ""


@pytest.mark.asyncio
async def test_put_unsupported_type(adapter):
    with pytest.raises(TypeError):
        await adapter.put(12345)
