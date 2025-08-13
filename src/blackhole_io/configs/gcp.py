
from blackhole.configs.abstract import AbstractConfig
from pydantic import Field

class GCPConfig(AbstractConfig):
    bucket: str = Field(..., description="The name of the GCP bucket")
    project_id: str = Field(..., description="The GCP project ID")
    credentials: dict = Field(..., description="GCP credentials for authentication")
