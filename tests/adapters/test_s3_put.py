from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from starlette.datastructures import UploadFile

from blackhole_io.adapters.s3_adapter import S3Adapter
from blackhole_io.blackhole_file import BlackholeFile
from blackhole_io.configs.s3 import S3Config


FAKE_ETAG = '"abc123def456"'


@pytest_asyncio.fixture
async def adapter():
    with patch("blackhole_io.adapters.s3_adapter.boto3") as mock_boto3:
        mock_client = MagicMock()
        mock_client.head_object.return_value = {"ETag": FAKE_ETAG}
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
    file = BlackholeFile(filename="test-key", data_to_upload=b"hello bytes")
    result = await adapter.put(file)
    assert result.filename == "test-key"
    assert result.hashsum == "abc123def456"
    adapter.client.upload_fileobj.assert_called_once()
    adapter.client.head_object.assert_called_once()


@pytest.mark.asyncio
async def test_put_bytesio(adapter):
    data = b"hello bytesio"
    file = BlackholeFile(filename="test-key", data_to_upload=BytesIO(data))
    result = await adapter.put(file)
    assert result.filename == "test-key"
    assert result.hashsum == "abc123def456"
    call_kwargs = adapter.client.upload_fileobj.call_args
    assert call_kwargs.kwargs["Bucket"] == "test-bucket"
    assert call_kwargs.kwargs["Key"] == "test-key"


@pytest.mark.asyncio
async def test_put_str_path(adapter, tmp_path):
    source = tmp_path / "source.txt"
    source.write_bytes(b"hello file")
    file = BlackholeFile(filename="file-key", data_to_upload=str(source))
    result = await adapter.put(file)
    assert result.filename == "file-key"
    assert result.hashsum == "abc123def456"
    adapter.client.upload_file.assert_called_once()
    call_kwargs = adapter.client.upload_file.call_args
    assert call_kwargs.kwargs["Filename"] == str(source)
    assert call_kwargs.kwargs["Bucket"] == "test-bucket"
    assert call_kwargs.kwargs["Key"] == "file-key"


@pytest.mark.asyncio
async def test_put_upload_file(adapter):
    data = b"hello upload"
    upload = UploadFile(file=BytesIO(data), filename="test.txt")
    file = BlackholeFile(filename="upload-key", data_to_upload=upload)
    result = await adapter.put(file)
    assert result.filename == "upload-key"
    assert result.hashsum == "abc123def456"
    adapter.client.upload_fileobj.assert_called_once()


@pytest.mark.asyncio
async def test_put_upload_file_passes_inner_file(adapter):
    inner = BytesIO(b"inner")
    upload = UploadFile(file=inner, filename="doc.pdf")
    file = BlackholeFile(filename="k", data_to_upload=upload)
    await adapter.put(file)
    call_kwargs = adapter.client.upload_fileobj.call_args
    assert call_kwargs.kwargs["Fileobj"] is inner


@pytest.mark.asyncio
async def test_put_uses_filename_as_key(adapter):
    file = BlackholeFile(filename="my-key", data_to_upload=b"data")
    result = await adapter.put(file)
    assert result.filename == "my-key"


@pytest.mark.asyncio
async def test_put_custom_bucket(adapter):
    file = BlackholeFile(filename="k", data_to_upload=BytesIO(b"data"), extra={"Bucket": "other-bucket"})
    result = await adapter.put(file)
    assert result.filename == "k"
    call_kwargs = adapter.client.upload_fileobj.call_args
    assert call_kwargs.kwargs["Bucket"] == "other-bucket"
    # head_object should use the custom bucket too
    head_kwargs = adapter.client.head_object.call_args
    assert head_kwargs.kwargs["Bucket"] == "other-bucket"


@pytest.mark.asyncio
async def test_put_unsupported_type(adapter):
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        BlackholeFile(filename="k", data_to_upload=12345)
