from io import BytesIO
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
async def test_put_all(adapter):
    files = [BytesIO(b"f1"), BytesIO(b"f2"), BytesIO(b"f3")]
    keys = await adapter.put_all(files)
    assert len(keys) == 3
    assert adapter.client.upload_fileobj.call_count == 3


@pytest.mark.asyncio
async def test_put_all_empty(adapter):
    keys = await adapter.put_all([])
    assert keys == []


@pytest.mark.asyncio
async def test_put_all_custom_bucket(adapter):
    files = [BytesIO(b"a"), BytesIO(b"b")]
    await adapter.put_all(files, Bucket="custom")
    for call in adapter.client.upload_fileobj.call_args_list:
        assert call.kwargs["Bucket"] == "custom"
