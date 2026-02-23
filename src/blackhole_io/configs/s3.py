from pydantic import Field
from pydantic_settings import SettingsConfigDict

from blackhole_io.configs.abstract import AbstractConfig


class S3Config(AbstractConfig):
    model_config = SettingsConfigDict(env_prefix="BLACKHOLE_S3_", extra="ignore")

    bucket: str = Field(..., description="The name of the S3 bucket")
    region: str = Field(
        ..., description="The AWS region where the S3 bucket is located"
    )
    access_key: str = Field(..., description="AWS access key for authentication")
    secret_key: str = Field(..., description="AWS secret key for authentication")
