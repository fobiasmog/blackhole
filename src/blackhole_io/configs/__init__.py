
from blackhole_io.configs.s3 import S3Config
from blackhole_io.configs.gcp import GCPConfig
from blackhole_io.configs.local import LocalConfig
from typing import Union

ConfigType = Union[S3Config, GCPConfig, LocalConfig]

__all__ = ["S3Config", "GCPConfig", "LocalConfig", "ConfigType"]
