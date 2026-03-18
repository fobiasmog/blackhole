import logging
import os
from pathlib import Path
from typing import Optional

import yaml

from blackhole_io.configs import ConfigType
from blackhole_io.configs.gcp import GCPConfig
from blackhole_io.configs.local import LocalConfig
from blackhole_io.configs.s3 import S3Config

logger = logging.getLogger(__name__)

ADAPTER_MAP: dict[str, type] = {
    "s3": S3Config,
    "gcp": GCPConfig,
    "local": LocalConfig,
}


def _load_from_yaml(path: Path) -> ConfigType:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    data = yaml.safe_load(path.read_text())

    adapter = data.get("adapter")
    if adapter is None:
        raise ValueError("YAML config must contain 'adapter' key (s3, gcp, local)")

    config_cls = ADAPTER_MAP.get(adapter)
    if config_cls is None:
        raise ValueError(
            f"Unknown adapter '{adapter}'. Must be one of: {', '.join(ADAPTER_MAP)}"
        )

    env_prefix = config_cls.model_config.get("env_prefix", "")
    for key in config_cls.env_fields():
        if key not in data:
            env_val = os.environ.get(f"{env_prefix}{key.upper()}")
            if env_val is not None:
                data[key] = env_val

    logger.debug("Loaded '%s' config from YAML: %s", adapter, path)
    return config_cls(**data)


def _discover_yaml() -> Optional[Path]:
    path = Path.cwd() / "config" / "blackhole.yaml"
    return path if path.exists() else None


SUPPORTED_EXTENSIONS = {".yaml", ".yml"}


def _load_from_file(path: Path) -> ConfigType:
    if path.suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported config file format: '{path.suffix}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
    return _load_from_yaml(path)


def load_config(config: Optional[ConfigType | str | Path] = None) -> ConfigType:
    if isinstance(config, ConfigType):
        return config

    if isinstance(config, (str, Path)):
        return _load_from_file(Path(config))

    # config is None — try auto-discovery
    yaml_path = _discover_yaml()
    if yaml_path is not None:
        logger.debug("Auto-discovered config at %s", yaml_path)
        return _load_from_yaml(yaml_path)

    # Fall back to env vars
    adapter = os.environ.get("BLACKHOLE_ADAPTER")
    if adapter is not None:
        logger.debug("Using env var fallback: BLACKHOLE_ADAPTER=%s", adapter)
        config_cls = ADAPTER_MAP.get(adapter)
        if config_cls is None:
            raise ValueError(
                f"Unknown adapter '{adapter}'. Must be one of: {', '.join(ADAPTER_MAP)}"
            )
        return config_cls()

    raise ValueError(
        "No configuration found. Provide a config object, a YAML file path, "
        "place config/blackhole.yaml in the working directory, "
        "or set BLACKHOLE_ADAPTER environment variable."
    )
