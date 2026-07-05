from typing import Optional

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from blackhole_io.configs.abstract import AbstractConfig


class AIStoreConfig(AbstractConfig):
    model_config = SettingsConfigDict(env_prefix="MINIO_", extra="ignore")

    endpoint: str = Field(..., description="The URL of the AIStore server")
    access_key: Optional[str] = Field(default=None, description="AIStore access key for authentication")
    secret_key: Optional[str] = Field(default=None, description="AIStore secret key for authentication")
    secure: bool = Field(default=False, description="Whether the server is secure")

    @classmethod
    def env_fields(cls) -> set[str]:
        return {"access_key", "secret_key", "endpoint", "secure"}
