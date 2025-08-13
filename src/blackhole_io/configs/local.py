from pydantic import Field
from blackhole.configs.abstract import AbstractConfig

class LocalConfig(AbstractConfig):
    directory: str = Field(..., description="The name of the local directory")
