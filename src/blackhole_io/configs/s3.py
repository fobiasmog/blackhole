from typing import Optional

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from blackhole_io.configs.abstract import AbstractConfig


class S3Config(AbstractConfig):
    model_config = SettingsConfigDict(env_prefix="BLACKHOLE_S3_", extra="ignore")

    bucket: str = Field(..., description="The name of the S3 bucket")
    region: str = Field(
        ..., description="The AWS region where the S3 bucket is located"
    )
    access_key: Optional[str] = Field(default=None, description="AWS access key for authentication")
    secret_key: Optional[str] = Field(default=None, description="AWS secret key for authentication")

    @classmethod
    def env_fields(cls) -> set[str]:
        return {"access_key", "secret_key"}
