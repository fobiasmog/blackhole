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
async def test_exists_true(adapter):
    result = await adapter.exists("my-key")
    assert result is True
    adapter.client.head_object.assert_called_once_with(
        Bucket="test-bucket", Key="my-key"
    )


@pytest.mark.asyncio
async def test_exists_false(adapter):
    adapter.client.head_object.side_effect = Exception("not found")
    result = await adapter.exists("missing-key")
    assert result is False
