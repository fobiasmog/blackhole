from pathlib import Path
from typing import Optional


from blackhole_io.configs import ConfigType

# ADAPTER_MAP = {
#     "s3": S3Config,
#     "gcp": GCPConfig,
#     "local": LocalConfig,
# }


def load_config(config: Optional[ConfigType | str | Path]) -> ConfigType:
    if config is None:
        raise NotImplementedError
    elif isinstance(config, ConfigType):
        return config
    elif isinstance(config, Path) or isinstance(config, str):
        raise NotImplementedError
        # adapter = env.get("BLACKHOLE_ADAPTER")
        # if adapter is None:
        #     raise ValueError(".env file must contain BLACKHOLE_ADAPTER (s3, gcp, local)")

        # config_cls = ADAPTER_MAP.get(adapter)
        # if config_cls is None:
        #     raise ValueError(f"Unknown adapter '{adapter}'. Must be one of: {', '.join(ADAPTER_MAP)}")

        # return config_cls(_env_file=config)
