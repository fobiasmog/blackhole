import os
from io import BytesIO
from pathlib import Path

import pytest
from starlette.datastructures import UploadFile

from blackhole_io.blackhole_file import BlackholeFile


@pytest.mark.asyncio
async def test_put_bytes(adapter, tmp_path):
    data = b"hello bytes"
    file = BlackholeFile(filename="test", data_to_upload=data)
    filename = await adapter.put(file)
    assert os.path.exists(tmp_path / filename)
    with open(tmp_path / filename, "rb") as f:
        assert f.read() == data


@pytest.mark.asyncio
async def test_put_bytes_no_extension(adapter):
    file = BlackholeFile(filename="test", data_to_upload=b"raw")
    filename = await adapter.put(file)
    assert Path(filename).suffix == ""


@pytest.mark.asyncio
async def test_put_bytesio(adapter, tmp_path):
    data = b"hello bytesio"
    file = BlackholeFile(filename="test", data_to_upload=BytesIO(data))
    filename = await adapter.put(file)
    assert os.path.exists(tmp_path / filename)
    with open(tmp_path / filename, "rb") as f:
        assert f.read() == data


@pytest.mark.asyncio
async def test_put_bytesio_preserves_extension(adapter, tmp_path):
    buf = BytesIO(b"data")
    buf.name = "report.csv"
    file = BlackholeFile(filename="report.csv", data_to_upload=buf)
    filename = await adapter.put(file)
    assert Path(filename).suffix == ".csv"


@pytest.mark.asyncio
async def test_put_bytesio_no_name(adapter):
    file = BlackholeFile(filename="test", data_to_upload=BytesIO(b"no name"))
    filename = await adapter.put(file)
    assert Path(filename).suffix == ""


@pytest.mark.asyncio
async def test_put_str_path(adapter, tmp_path):
    source = tmp_path / "source.txt"
    source.write_bytes(b"hello file path")
    file = BlackholeFile(filename="test", data_to_upload=str(source))
    filename = await adapter.put(file)
    assert os.path.exists(tmp_path / filename)
    with open(tmp_path / filename, "rb") as f:
        assert f.read() == b"hello file path"


@pytest.mark.asyncio
async def test_put_str_path_preserves_extension(adapter, tmp_path):
    source = tmp_path / "image.png"
    source.write_bytes(b"png data")
    file = BlackholeFile(filename="test", data_to_upload=str(source))
    filename = await adapter.put(file)
    # str data_to_upload appends source extension when filename has none
    assert Path(filename).suffix == ".png"


@pytest.mark.asyncio
async def test_put_str_path_no_extension(adapter, tmp_path):
    source = tmp_path / "noext"
    source.write_bytes(b"data")
    file = BlackholeFile(filename="test", data_to_upload=str(source))
    filename = await adapter.put(file)
    assert Path(filename).suffix == ""


@pytest.mark.asyncio
async def test_put_upload_file(adapter, tmp_path):
    data = b"hello upload"
    upload = UploadFile(file=BytesIO(data), filename="test.txt")
    file = BlackholeFile(filename="test.txt", data_to_upload=upload)
    filename = await adapter.put(file)
    assert os.path.exists(tmp_path / filename)
    with open(tmp_path / filename, "rb") as f:
        assert f.read() == data


@pytest.mark.asyncio
async def test_put_upload_file_preserves_extension(adapter):
    upload = UploadFile(file=BytesIO(b"img"), filename="photo.jpg")
    file = BlackholeFile(filename="photo.jpg", data_to_upload=upload)
    filename = await adapter.put(file)
    assert Path(filename).suffix == ".jpg"


@pytest.mark.asyncio
async def test_put_upload_file_no_filename(adapter):
    upload = UploadFile(file=BytesIO(b"anon"))
    file = BlackholeFile(filename="test", data_to_upload=upload)
    filename = await adapter.put(file)
    assert Path(filename).suffix == ""


@pytest.mark.asyncio
async def test_put_unsupported_type(adapter):
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        BlackholeFile(filename="test", data_to_upload=12345)
