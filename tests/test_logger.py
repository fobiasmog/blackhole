import logging
from unittest.mock import patch

import pytest

from blackhole_io import Blackhole
from blackhole_io.configs.local import LocalConfig
from blackhole_io.configs.s3 import S3Config


def test_default_log_level_is_error():
    bl_logger = logging.getLogger("blackhole_io")
    assert bl_logger.level == logging.ERROR


def test_default_no_handler(tmp_path):
    """Without log_level, no handler is added to the blackhole_io logger."""
    bl_logger = logging.getLogger("blackhole_io")
    handlers_before = list(bl_logger.handlers)

    Blackhole(config=LocalConfig(directory=str(tmp_path)))

    assert bl_logger.handlers == handlers_before


def test_log_level_configures_logger(tmp_path):
    bl_logger = logging.getLogger("blackhole_io")

    Blackhole(config=LocalConfig(directory=str(tmp_path)), log_level=logging.DEBUG)

    assert bl_logger.level == logging.DEBUG
    assert any(isinstance(h, logging.StreamHandler) for h in bl_logger.handlers)

    # cleanup
    bl_logger.handlers = [
        h for h in bl_logger.handlers if not isinstance(h, logging.StreamHandler)
    ]
    bl_logger.setLevel(logging.ERROR)


@pytest.mark.asyncio
async def test_s3_adapter_logs_on_put(caplog):
    config = S3Config(bucket="b", region="r", access_key="a", secret_key="s")
    with patch("blackhole_io.adapters.s3_adapter.boto3"):
        from blackhole_io.adapters.s3_adapter import S3Adapter

        adapter = S3Adapter(config)

    with caplog.at_level(logging.INFO, logger="blackhole_io.adapters.s3_adapter"):
        with patch.object(adapter, "_sync_put", return_value="test-key"):
            await adapter.put(b"data", key="test-key")

    assert any("Uploading test-key" in r.message for r in caplog.records)
