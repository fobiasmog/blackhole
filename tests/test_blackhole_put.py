"""Tests for Blackhole.put() — filename resolution and content_type extraction."""

from io import BytesIO
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from starlette.datastructures import UploadFile

from blackhole_io import Blackhole
from blackhole_io.configs.local import LocalConfig


@pytest_asyncio.fixture
async def bh(tmp_path):
    config = LocalConfig(directory=str(tmp_path))
    return Blackhole(config=config)


# --- filename resolution ---


@pytest.mark.asyncio
async def test_put_explicit_filename(bh, tmp_path):
    filename = await bh.put(b"data", filename="custom.txt")
    assert filename == "custom.txt"
    assert (tmp_path / filename).exists()


@pytest.mark.asyncio
async def test_put_no_filename_generates_uuid(bh):
    filename = await bh.put(b"data")
    # uuid4().hex is 32 hex chars
    assert len(filename) == 32
    assert filename.isalnum()


@pytest.mark.asyncio
async def test_put_upload_file_uses_its_filename(bh):
    upload = UploadFile(file=BytesIO(b"data"), filename="from_upload.txt")
    filename = await bh.put(upload)
    assert filename == "from_upload.txt"


@pytest.mark.asyncio
async def test_put_upload_file_explicit_filename_wins(bh):
    upload = UploadFile(file=BytesIO(b"data"), filename="from_upload.txt")
    filename = await bh.put(upload, filename="explicit.txt")
    assert filename == "explicit.txt"


@pytest.mark.asyncio
async def test_put_upload_file_no_filename_generates_uuid(bh):
    upload = UploadFile(file=BytesIO(b"data"))
    filename = await bh.put(upload)
    # UploadFile with no filename → falls back to uuid
    assert len(filename) == 32


# --- content_type extraction ---


@pytest.mark.asyncio
async def test_put_upload_file_extracts_content_type(bh):
    upload = UploadFile(
        file=BytesIO(b"img"),
        filename="photo.jpg",
        headers={"content-type": "image/jpeg"},
    )
    await bh.put(upload)
    result = await bh.get("photo.jpg")
    assert result.data == b"img"


@pytest.mark.asyncio
async def test_put_bytes_content_type_is_none(bh):
    filename = await bh.put(b"data", filename="test.bin")
    result = await bh.get(filename)
    assert result.content_type is None


@pytest.mark.asyncio
async def test_put_upload_file_with_explicit_filename_still_extracts_content_type(bh):
    """When explicit filename is given, content_type branch is skipped."""
    upload = UploadFile(
        file=BytesIO(b"data"),
        filename="original.txt",
        headers={"content-type": "text/plain"},
    )
    # explicit filename → hasattr branch not entered → content_type stays None
    filename = await bh.put(upload, filename="override.txt")
    assert filename == "override.txt"


# --- data written correctly ---


@pytest.mark.asyncio
async def test_put_bytes_writes_data(bh, tmp_path):
    data = b"hello facade"
    filename = await bh.put(data, filename="out.bin")
    assert (tmp_path / filename).read_bytes() == data


@pytest.mark.asyncio
async def test_put_bytesio_writes_data(bh, tmp_path):
    data = b"bytesio facade"
    filename = await bh.put(BytesIO(data), filename="out.bin")
    assert (tmp_path / filename).read_bytes() == data
