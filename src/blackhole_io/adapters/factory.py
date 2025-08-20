from typing import TYPE_CHECKING, Union
from blackhole_io.configs import S3Config, GCPConfig, LocalConfig
from blackhole_io.adapters.abstract import AbstractAdapter
from typing import overload


if TYPE_CHECKING:
    from blackhole_io.adapters.s3_adapter import S3Adapter
    from blackhole_io.adapters.gcp_adapter import GCPAdapter
    from blackhole_io.adapters.local_adapter import LocalAdapter


class AdapterFactory:
    @overload
    @classmethod
    def create(cls, config: S3Config) -> "S3Adapter":
        ...

    @overload
    @classmethod
    def create(cls, config: GCPConfig) -> "GCPAdapter":
        ...

    @overload
    @classmethod
    def create(cls, config: LocalConfig) -> "LocalAdapter":
        ...

    @classmethod
    def create(cls, config: Union[S3Config, GCPConfig, LocalConfig]) -> AbstractAdapter:
        if isinstance(config, S3Config):
            from blackhole_io.adapters.s3_adapter import S3Adapter
            return S3Adapter(config)
        elif isinstance(config, GCPConfig):
            from blackhole_io.adapters.gcp_adapter import GCPAdapter
            return GCPAdapter(config)
        elif isinstance(config, LocalConfig):
            from blackhole_io.adapters.local_adapter import LocalAdapter
            return LocalAdapter(config)
        else:
            raise ValueError("Unsupported configuration type")
