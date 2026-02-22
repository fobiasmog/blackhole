from unittest.mock import patch

import pytest

from blackhole_io.adapters.factory import AdapterFactory
from blackhole_io.adapters.gcp_adapter import GCPAdapter
from blackhole_io.adapters.local_adapter import LocalAdapter
from blackhole_io.adapters.s3_adapter import S3Adapter
from blackhole_io.configs.gcp import GCPConfig
from blackhole_io.configs.local import LocalConfig
from blackhole_io.configs.s3 import S3Config


def test_create_local_adapter(tmp_path):
    config = LocalConfig(directory=str(tmp_path))
    adapter = AdapterFactory.create(config)
    assert isinstance(adapter, LocalAdapter)


def test_create_s3_adapter():
    with patch("blackhole_io.adapters.s3_adapter.boto3"):
        config = S3Config(
            bucket="b",
            region="us-east-1",
            access_key="k",
            secret_key="s",
        )
        adapter = AdapterFactory.create(config)
        assert isinstance(adapter, S3Adapter)


def test_create_gcp_adapter():
    config = GCPConfig(
        bucket="b",
        project_id="p",
        credentials={"key": "val"},
    )
    adapter = AdapterFactory.create(config)
    assert isinstance(adapter, GCPAdapter)


def test_create_unsupported():
    with pytest.raises(ValueError, match="Unsupported configuration type"):
        AdapterFactory.create("not a config")
