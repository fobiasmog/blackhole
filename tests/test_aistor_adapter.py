from io import BytesIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

from blackhole_io.adapters.aistor_adapter import AIStoreAdapter
from blackhole_io.blackhole_file import BlackholeFile


@pytest_asyncio.fixture
async def adapter():
    with patch("blackhole_io.adapters.aistor_adapter.Minio") as mock_minio:
        mock_client = MagicMock()
        mock_minio.return_value = mock_client

        config = SimpleNamespace(
            endpoint="localhost:8080",
            access_key="access",
            secret_key="secret",
            secure=False,
            bucket="test-bucket",
        )
        yield AIStoreAdapter(config=config)


@pytest.mark.asyncio
async def test_put_str_path(adapter, tmp_path):
    source = tmp_path / "source.txt"
    source.write_bytes(b"hello file")

    adapter.client.bucket_exists.return_value = True
    adapter.client.fput_object.return_value = SimpleNamespace(etag="etag-path")

    file = BlackholeFile(filename="file-key", data_to_upload=str(source))
    result = await adapter.put(file)

    assert result.filename == "file-key"
    assert result.hashsum == "etag-path"
    adapter.client.bucket_exists.assert_called_once_with("default")
    adapter.client.make_bucket.assert_not_called()
    adapter.client.fput_object.assert_called_once_with(
        bucket_name="default",
        object_name="file-key",
        file_path=str(source),
        content_type=None,
        metadata={},
    )


@pytest.mark.asyncio
async def test_put_bytes_creates_bucket(adapter):
    adapter.client.bucket_exists.return_value = False
    adapter.client.put_object.return_value = SimpleNamespace(etag="etag-bytes")

    file = BlackholeFile(filename="bytes-key", data_to_upload=BytesIO(b"abc"), size=3)
    result = await adapter.put(file)

    assert result.filename == "bytes-key"
    assert result.hashsum == "etag-bytes"
    adapter.client.bucket_exists.assert_called_once_with("default")
    adapter.client.make_bucket.assert_called_once_with("default")
    adapter.client.put_object.assert_called_once()
    call_kwargs = adapter.client.put_object.call_args.kwargs
    assert call_kwargs["bucket_name"] == "default"
    assert call_kwargs["object_name"] == "bytes-key"
    assert call_kwargs["data"] == file.data_to_upload
    assert call_kwargs["length"] == 3


@pytest.mark.asyncio
async def test_put_all(adapter):
    adapter.client.bucket_exists.return_value = True
    adapter.client.put_object.side_effect = [
        SimpleNamespace(etag="etag-1"),
        SimpleNamespace(etag="etag-2"),
    ]

    files = [
        BlackholeFile(filename="one", data_to_upload=BytesIO(b"1"), size=1),
        BlackholeFile(filename="two", data_to_upload=BytesIO(b"2"), size=1),
    ]

    result = await adapter.put_all(files)

    assert [item.filename for item in result] == ["one", "two"]
    assert [item.hashsum for item in result] == ["etag-1", "etag-2"]
    assert adapter.client.put_object.call_count == 2


@pytest.mark.asyncio
async def test_get(adapter):
    response = MagicMock()
    response.data = b"file-data"
    response.get.side_effect = (
        lambda key, default=None: {
            "ContentType": "text/plain",
            "ContentLength": 9,
        }.get(key, default)
    )
    adapter.client.get_object.return_value = response

    result = await adapter.get("my-key")

    assert result.filename == "my-key"
    assert result.blob == b"file-data"
    assert result.content_type == "text/plain"
    assert result.size == 9
    adapter.client.get_object.assert_called_once_with(
        bucket_name="test-bucket",
        object_name="my-key",
    )
    response.close.assert_called_once()
    response.release_conn.assert_called_once()


@pytest.mark.asyncio
async def test_exists_true(adapter):
    result = await adapter.exists("my-key")

    assert result is True
    adapter.client.stat_object.assert_called_once_with(
        bucket_name="test-bucket",
        object_name="my-key",
    )


@pytest.mark.asyncio
async def test_exists_false(adapter):
    adapter.client.stat_object.side_effect = Exception("not found")

    result = await adapter.exists("missing-key")

    assert result is False


@pytest.mark.asyncio
async def test_delete(adapter):
    await adapter.delete("my-key")

    adapter.client.remove_object.assert_called_once_with(
        bucket_name="test-bucket",
        object_name="my-key",
    )
