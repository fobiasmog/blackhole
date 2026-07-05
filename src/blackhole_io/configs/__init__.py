from typing import Union

from blackhole_io.configs.aistore import AIStoreConfig
from blackhole_io.configs.gcp import GCPConfig
from blackhole_io.configs.local import LocalConfig
from blackhole_io.configs.s3 import S3Config

ConfigType = Union[S3Config, GCPConfig, AIStoreConfig, LocalConfig]

__all__ = ["S3Config", "GCPConfig", "LocalConfig", "AIStoreConfig", "ConfigType"]
