from __future__ import annotations

from typing import TYPE_CHECKING, overload

from blackhole_io.adapters.abstract import AbstractAdapter
from blackhole_io.configs import GCPConfig, LocalConfig, S3Config

if TYPE_CHECKING:
    from blackhole_io.adapters.gcp_adapter import GCPAdapter
    from blackhole_io.adapters.local_adapter import LocalAdapter
    from blackhole_io.adapters.s3_adapter import S3Adapter
    from blackhole_io.configs import ConfigType


class AdapterFactory:
    @overload
    @classmethod
    def create(cls, config: S3Config) -> "S3Adapter": ...

    @overload
    @classmethod
    def create(cls, config: GCPConfig) -> "GCPAdapter": ...

    @overload
    @classmethod
    def create(cls, config: LocalConfig) -> "LocalAdapter": ...

    @classmethod
    def create(cls, config: ConfigType) -> AbstractAdapter:
        if isinstance(config, S3Config):
            from blackhole_io.adapters.s3_adapter import S3Adapter
            return S3Adapter(config)

        if isinstance(config, GCPConfig):
            from blackhole_io.adapters.gcp_adapter import GCPAdapter
            return GCPAdapter(config)

        if isinstance(config, LocalConfig):
            from blackhole_io.adapters.local_adapter import LocalAdapter
            return LocalAdapter(config)

        raise ValueError("Unsupported configuration type")
