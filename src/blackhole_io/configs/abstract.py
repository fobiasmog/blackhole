from pydantic_settings import BaseSettings, SettingsConfigDict


class AbstractConfig(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")
