from pathlib import Path

from dotenv import dotenv_values

from blackhole_io.configs.gcp import GCPConfig
from blackhole_io.configs.local import LocalConfig
from blackhole_io.configs.s3 import S3Config

ADAPTER_MAP = {
    "s3": S3Config,
    "gcp": GCPConfig,
    "local": LocalConfig,
}


def load_config(path: str | Path) -> S3Config | GCPConfig | LocalConfig:
    env = dotenv_values(path)

    adapter = env.get("BLACKHOLE_ADAPTER")
    if adapter is None:
        raise ValueError(".env file must contain BLACKHOLE_ADAPTER (s3, gcp, local)")

    config_cls = ADAPTER_MAP.get(adapter)
    if config_cls is None:
        raise ValueError(f"Unknown adapter '{adapter}'. Must be one of: {', '.join(ADAPTER_MAP)}")

    return config_cls(_env_file=path)
