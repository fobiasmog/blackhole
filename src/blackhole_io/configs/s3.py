from pydantic import Field
from blackhole.configs.abstract import AbstractConfig

class S3Config(AbstractConfig):
    bucket: str = Field(..., description="The name of the S3 bucket")
    region: str = Field(..., description="The AWS region where the S3 bucket is located")
    access_key: str = Field(..., description="AWS access key for authentication")
    secret_key: str = Field(..., description="AWS secret key for authentication")
