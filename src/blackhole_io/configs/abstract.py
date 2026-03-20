from pydantic_settings import BaseSettings, SettingsConfigDict


class AbstractConfig(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    @classmethod
    def env_fields(cls) -> set[str]:
        """Return field names that should be loaded from env vars, not YAML."""
        return set()
