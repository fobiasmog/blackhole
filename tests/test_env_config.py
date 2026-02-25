from unittest.mock import patch

import pytest

from blackhole_io.configs.loader import load_config
from blackhole_io.configs.local import LocalConfig
from blackhole_io.configs.s3 import S3Config

@pytest.skip("TODO", allow_module_level=True)
def test_load_local_config(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "BLACKHOLE_ADAPTER=local\n"
        "BLACKHOLE_LOCAL_DIRECTORY=/tmp/storage\n"
    )
    config = load_config(env_file)
    assert isinstance(config, LocalConfig)
    assert config.directory == "/tmp/storage"


def test_load_s3_config(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "BLACKHOLE_ADAPTER=s3\n"
        "BLACKHOLE_S3_BUCKET=my-bucket\n"
        "BLACKHOLE_S3_REGION=us-east-1\n"
        "BLACKHOLE_S3_ACCESS_KEY=key123\n"
        "BLACKHOLE_S3_SECRET_KEY=secret456\n"
    )
    with patch("blackhole_io.adapters.s3_adapter.boto3"):
        config = load_config(env_file)
    assert isinstance(config, S3Config)
    assert config.bucket == "my-bucket"
    assert config.region == "us-east-1"
    assert config.access_key == "key123"
    assert config.secret_key == "secret456"


def test_missing_adapter_key(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("BLACKHOLE_LOCAL_DIRECTORY=/tmp\n")
    with pytest.raises(ValueError, match="must contain BLACKHOLE_ADAPTER"):
        load_config(env_file)

def test_unknown_adapter(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("BLACKHOLE_ADAPTER=azure\n")
    with pytest.raises(ValueError, match="Unknown adapter 'azure'"):
        load_config(env_file)

def test_blackhole_from_env(tmp_path):
    from blackhole_io import Blackhole
    from blackhole_io.adapters.local_adapter import LocalAdapter

    env_file = tmp_path / ".env"
    env_file.write_text(
        "BLACKHOLE_ADAPTER=local\n"
        f"BLACKHOLE_LOCAL_DIRECTORY={tmp_path}\n"
    )
    bh = Blackhole(config=str(env_file))
    assert isinstance(bh.adapter, LocalAdapter)
    assert bh.config.directory == str(tmp_path)
