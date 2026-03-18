from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from starlette.datastructures import UploadFile

from blackhole_io.adapters.s3_adapter import S3Adapter
from blackhole_io.configs.s3 import S3Config


@pytest_asyncio.fixture
async def adapter():
    with patch("blackhole_io.adapters.s3_adapter.boto3") as mock_boto3:
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        config = S3Config(
            bucket="test-bucket",
            region="us-east-1",
            access_key="fake-key",
            secret_key="fake-secret",
        )
        yield S3Adapter(config)


@pytest.mark.asyncio
async def test_put_bytes(adapter):
    key = await adapter.put(b"hello bytes", key="test-key")
    assert key == "test-key"
    adapter.client.upload_fileobj.assert_called_once()


@pytest.mark.asyncio
async def test_put_bytesio(adapter):
    data = b"hello bytesio"
    key = await adapter.put(BytesIO(data), key="test-key")
    assert key == "test-key"
    call_kwargs = adapter.client.upload_fileobj.call_args
    assert call_kwargs.kwargs["Bucket"] == "test-bucket"
    assert call_kwargs.kwargs["Key"] == "test-key"


@pytest.mark.asyncio
async def test_put_str_path(adapter, tmp_path):
    source = tmp_path / "source.txt"
    source.write_bytes(b"hello file")
    key = await adapter.put(str(source), key="file-key")
    assert key == "file-key"
    adapter.client.upload_file.assert_called_once()
    call_kwargs = adapter.client.upload_file.call_args
    assert call_kwargs.kwargs["Filename"] == str(source)
    assert call_kwargs.kwargs["Bucket"] == "test-bucket"
    assert call_kwargs.kwargs["Key"] == "file-key"


@pytest.mark.asyncio
async def test_put_upload_file(adapter):
    data = b"hello upload"
    upload = UploadFile(file=BytesIO(data), filename="test.txt")
    key = await adapter.put(upload, key="upload-key")
    assert key == "upload-key"
    adapter.client.upload_fileobj.assert_called_once()


@pytest.mark.asyncio
async def test_put_upload_file_passes_inner_file(adapter):
    inner = BytesIO(b"inner")
    upload = UploadFile(file=inner, filename="doc.pdf")
    await adapter.put(upload, key="k")
    call_kwargs = adapter.client.upload_fileobj.call_args
    assert call_kwargs.kwargs["Fileobj"] is inner


@pytest.mark.asyncio
async def test_put_generates_key(adapter):
    key = await adapter.put(b"data")
    assert key is not None
    assert len(key) == 32  # uuid4().hex


@pytest.mark.asyncio
async def test_put_key_via_kwarg(adapter):
    key = await adapter.put(b"data", Key="kwarg-key")
    assert key == "kwarg-key"


@pytest.mark.asyncio
async def test_put_custom_bucket(adapter):
    key = await adapter.put(BytesIO(b"data"), key="k", Bucket="other-bucket")
    assert key == "k"
    call_kwargs = adapter.client.upload_fileobj.call_args
    assert call_kwargs.kwargs["Bucket"] == "other-bucket"


@pytest.mark.asyncio
async def test_put_unsupported_type(adapter):
    # ints get wrapped — boto3 would reject, but _sync_put doesn't guard types
    # just verify it doesn't crash at the adapter dispatch level
    await adapter.put(12345, key="k")
    adapter.client.upload_fileobj.assert_called_once()
