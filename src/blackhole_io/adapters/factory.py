from typing import TYPE_CHECKING, Union
from blackhole.configs import S3Config, GCPConfig, LocalConfig
from blackhole.adapters.abstract import AbstractAdapter
from typing import overload


if TYPE_CHECKING:
    from blackhole.adapters.s3_adapter import S3Adapter
    from blackhole.adapters.gcp_adapter import GCPAdapter
    from blackhole.adapters.local_adapter import LocalAdapter


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
            from blackhole.adapters.s3_adapter import S3Adapter
            return S3Adapter()
        elif isinstance(config, GCPConfig):
            from blackhole.adapters.gcp_adapter import GCPAdapter
            return GCPAdapter()
        elif isinstance(config, LocalConfig):
            from blackhole.adapters.local_adapter import LocalAdapter
            return LocalAdapter(config)
        else:
            raise ValueError("Unsupported configuration type")
