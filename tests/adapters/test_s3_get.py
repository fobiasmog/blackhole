from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

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
async def test_get(adapter):
    mock_body = MagicMock()
    mock_body.read.return_value = b"file content"
    adapter.client.get_object.return_value = {
        "Body": mock_body,
        "ContentType": "text/plain",
        "ContentLength": 12,
    }
    result = await adapter.get("my-key")
    assert result.filename == "my-key"
    assert result.blob == b"file content"
    assert result.content_type == "text/plain"
    assert result.size == 12
    adapter.client.get_object.assert_called_once_with(
        Bucket="test-bucket", Key="my-key"
    )


@pytest.mark.asyncio
async def test_get_default_content_type(adapter):
    mock_body = MagicMock()
    mock_body.read.return_value = b"data"
    adapter.client.get_object.return_value = {
        "Body": mock_body,
        "ContentLength": 4,
    }
    result = await adapter.get("k")
    assert result.content_type == "application/octet-stream"


@pytest.mark.asyncio
async def test_get_missing_content_length(adapter):
    mock_body = MagicMock()
    mock_body.read.return_value = b"hello"
    adapter.client.get_object.return_value = {
        "Body": mock_body,
        "ContentType": "text/plain",
    }
    result = await adapter.get("k")
    assert result.size == 5  # falls back to len(data)


@pytest.mark.asyncio
async def test_get_propagates_error(adapter):
    adapter.client.get_object.side_effect = Exception("NoSuchKey")
    with pytest.raises(Exception, match="NoSuchKey"):
        await adapter.get("missing")
