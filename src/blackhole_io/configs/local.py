from pydantic import Field
from pydantic_settings import SettingsConfigDict

from blackhole_io.configs.abstract import AbstractConfig


class LocalConfig(AbstractConfig):
    model_config = SettingsConfigDict(env_prefix="BLACKHOLE_LOCAL_", extra="ignore")

    directory: str = Field(..., description="The name of the local directory")
