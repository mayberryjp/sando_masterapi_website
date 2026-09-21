from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SERVICE_", extra="ignore")

    database_url: str = Field(
        "sqlite:////database/errors.db", validation_alias="DATABASE_URL"
    )
    api_listen_address: str = Field(
        "0.0.0.0",  # nosec B104
        validation_alias="API_LISTEN_ADDRESS",
    )
    api_port: int = Field(5000, validation_alias="API_PORT")

    log_level: str = "INFO"


settings = Settings()
