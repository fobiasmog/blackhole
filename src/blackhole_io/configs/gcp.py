from pydantic import Field
from pydantic_settings import SettingsConfigDict

from blackhole_io.configs.abstract import AbstractConfig


class GCPConfig(AbstractConfig):
    model_config = SettingsConfigDict(env_prefix="BLACKHOLE_GCP_", extra="ignore")

    bucket: str = Field(..., description="The name of the GCP bucket")
    project_id: str = Field(..., description="The GCP project ID")
    credentials: dict = Field(..., description="GCP credentials for authentication")
