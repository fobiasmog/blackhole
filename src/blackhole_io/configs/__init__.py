
from blackhole.configs.s3 import S3Config
from blackhole.configs.gcp import GCPConfig
from blackhole.configs.local import LocalConfig
from typing import Union

ConfigType = Union[S3Config, GCPConfig, LocalConfig]

__all__ = ["S3Config", "GCPConfig", "LocalConfig", "ConfigType"]
