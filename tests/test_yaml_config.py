from pathlib import Path

import pytest

from blackhole_io.configs.loader import load_config
from blackhole_io.configs.local import LocalConfig
from blackhole_io.configs.s3 import S3Config


def test_load_s3_config_from_yaml(tmp_path, monkeypatch):
    monkeypatch.setenv("BLACKHOLE_S3_ACCESS_KEY", "envkey")
    monkeypatch.setenv("BLACKHOLE_S3_SECRET_KEY", "envsecret")
    yaml_file = tmp_path / "blackhole.yaml"
    yaml_file.write_text(
        "adapter: s3\n"
        "bucket: my-bucket\n"
        "region: us-east-1\n"
    )
    config = load_config(str(yaml_file))
    assert isinstance(config, S3Config)
    assert config.bucket == "my-bucket"
    assert config.region == "us-east-1"
    assert config.access_key == "envkey"
    assert config.secret_key == "envsecret"


def test_load_local_config_from_yaml(tmp_path):
    yaml_file = tmp_path / "blackhole.yaml"
    yaml_file.write_text("adapter: local\ndirectory: /tmp/storage\n")
    config = load_config(str(yaml_file))
    assert isinstance(config, LocalConfig)
    assert config.directory == "/tmp/storage"


def test_missing_adapter_key(tmp_path):
    yaml_file = tmp_path / "blackhole.yaml"
    yaml_file.write_text("bucket: my-bucket\n")
    with pytest.raises(ValueError, match="must contain.*adapter"):
        load_config(str(yaml_file))


def test_unknown_adapter(tmp_path):
    yaml_file = tmp_path / "blackhole.yaml"
    yaml_file.write_text("adapter: azure\n")
    with pytest.raises(ValueError, match="Unknown adapter 'azure'"):
        load_config(str(yaml_file))


def test_yaml_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/blackhole.yaml")


def test_auto_discovery(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    yaml_file = config_dir / "blackhole.yaml"
    yaml_file.write_text("adapter: local\ndirectory: /tmp/storage\n")
    monkeypatch.chdir(tmp_path)
    config = load_config(None)
    assert isinstance(config, LocalConfig)
    assert config.directory == "/tmp/storage"


def test_auto_discovery_falls_back_to_env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("BLACKHOLE_ADAPTER", "local")
    monkeypatch.setenv("BLACKHOLE_LOCAL_DIRECTORY", "/tmp/envdir")
    config = load_config(None)
    assert isinstance(config, LocalConfig)
    assert config.directory == "/tmp/envdir"


def test_env_fallback_s3(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("BLACKHOLE_ADAPTER", "s3")
    monkeypatch.setenv("BLACKHOLE_S3_BUCKET", "env-bucket")
    monkeypatch.setenv("BLACKHOLE_S3_REGION", "eu-west-1")
    monkeypatch.setenv("BLACKHOLE_S3_ACCESS_KEY", "envkey")
    monkeypatch.setenv("BLACKHOLE_S3_SECRET_KEY", "envsecret")
    config = load_config(None)
    assert isinstance(config, S3Config)
    assert config.bucket == "env-bucket"
    assert config.region == "eu-west-1"
    assert config.access_key == "envkey"
    assert config.secret_key == "envsecret"


def test_env_fallback_unknown_adapter(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("BLACKHOLE_ADAPTER", "azure")
    with pytest.raises(ValueError, match="Unknown adapter 'azure'"):
        load_config(None)


def test_yaml_takes_precedence_over_env(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    yaml_file = config_dir / "blackhole.yaml"
    yaml_file.write_text("adapter: local\ndirectory: /tmp/from-yaml\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("BLACKHOLE_ADAPTER", "s3")
    monkeypatch.setenv("BLACKHOLE_S3_BUCKET", "b")
    monkeypatch.setenv("BLACKHOLE_S3_REGION", "r")
    monkeypatch.setenv("BLACKHOLE_S3_ACCESS_KEY", "a")
    monkeypatch.setenv("BLACKHOLE_S3_SECRET_KEY", "s")
    config = load_config(None)
    assert isinstance(config, LocalConfig)
    assert config.directory == "/tmp/from-yaml"


def test_auto_discovery_no_yaml_no_env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("BLACKHOLE_ADAPTER", raising=False)
    with pytest.raises(ValueError, match="No configuration found"):
        load_config(None)


def test_direct_config_passthrough():
    config = S3Config(bucket="b", region="r", access_key="a", secret_key="s")
    result = load_config(config)
    assert result is config


def test_direct_local_config_passthrough(tmp_path):
    config = LocalConfig(directory=str(tmp_path))
    result = load_config(config)
    assert result is config


def test_extra_yaml_keys_ignored(tmp_path):
    yaml_file = tmp_path / "blackhole.yaml"
    yaml_file.write_text(
        "adapter: local\n"
        "directory: /tmp/storage\n"
        "unknown_key: whatever\n"
        "another_extra: 123\n"
    )
    config = load_config(str(yaml_file))
    assert isinstance(config, LocalConfig)
    assert config.directory == "/tmp/storage"


def test_path_object(tmp_path):
    yaml_file = tmp_path / "blackhole.yaml"
    yaml_file.write_text("adapter: local\ndirectory: /tmp/storage\n")
    config = load_config(Path(yaml_file))
    assert isinstance(config, LocalConfig)


def test_env_fields_yaml_takes_precedence(tmp_path, monkeypatch):
    """env_fields present in YAML are kept; env vars don't override them."""
    monkeypatch.setenv("BLACKHOLE_S3_ACCESS_KEY", "from-env")
    monkeypatch.setenv("BLACKHOLE_S3_SECRET_KEY", "from-env")
    yaml_file = tmp_path / "blackhole.yaml"
    yaml_file.write_text(
        "adapter: s3\n"
        "bucket: b\n"
        "region: r\n"
        "access_key: from-yaml\n"
        "secret_key: from-yaml\n"
    )
    config = load_config(str(yaml_file))
    assert config.access_key == "from-yaml"
    assert config.secret_key == "from-yaml"


def test_env_fields_loaded_from_env_when_missing_in_yaml(tmp_path, monkeypatch):
    """env_fields absent from YAML are loaded from env vars."""
    monkeypatch.setenv("BLACKHOLE_S3_ACCESS_KEY", "from-env")
    monkeypatch.setenv("BLACKHOLE_S3_SECRET_KEY", "from-env")
    yaml_file = tmp_path / "blackhole.yaml"
    yaml_file.write_text(
        "adapter: s3\n"
        "bucket: b\n"
        "region: r\n"
    )
    config = load_config(str(yaml_file))
    assert config.access_key == "from-env"
    assert config.secret_key == "from-env"


def test_env_fields_default_to_none(tmp_path, monkeypatch):
    """env_fields not set in env → default to None."""
    monkeypatch.delenv("BLACKHOLE_S3_ACCESS_KEY", raising=False)
    monkeypatch.delenv("BLACKHOLE_S3_SECRET_KEY", raising=False)
    yaml_file = tmp_path / "blackhole.yaml"
    yaml_file.write_text(
        "adapter: s3\n"
        "bucket: b\n"
        "region: r\n"
    )
    config = load_config(str(yaml_file))
    assert isinstance(config, S3Config)
    assert config.access_key is None
    assert config.secret_key is None


def test_env_fields_returns_empty_for_local():
    from blackhole_io.configs.local import LocalConfig

    assert LocalConfig.env_fields() == set()


def test_env_fields_returns_secrets_for_s3():
    assert S3Config.env_fields() == {"access_key", "secret_key"}


def test_unsupported_file_extension(tmp_path):
    toml_file = tmp_path / "blackhole.toml"
    toml_file.write_text("")
    with pytest.raises(ValueError, match="Unsupported config file format"):
        load_config(str(toml_file))


def test_yml_extension(tmp_path):
    yml_file = tmp_path / "blackhole.yml"
    yml_file.write_text("adapter: local\ndirectory: /tmp/storage\n")
    config = load_config(str(yml_file))
    assert isinstance(config, LocalConfig)
    assert config.directory == "/tmp/storage"


def test_blackhole_from_yaml(tmp_path):
    from blackhole_io import Blackhole
    from blackhole_io.adapters.local_adapter import LocalAdapter

    yaml_file = tmp_path / "blackhole.yaml"
    yaml_file.write_text(f"adapter: local\ndirectory: {tmp_path}\n")
    bh = Blackhole(config=str(yaml_file))
    assert isinstance(bh.adapter, LocalAdapter)
    assert bh.config.directory == str(tmp_path)
