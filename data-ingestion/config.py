from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    MONGO_DB_HOST: str | None = None
    MONGO_DB_NAME: str | None = None

    RABBITMQ_HOST: str | None = None
    RABBITMQ_PORT: int | None = None
    RABBITMQ_DEFAULT_USERNAME: str | None = None
    RABBITMQ_DEFAULT_PASSWORD: str | None = None
    RABBITMQ_QUEUE_NAME: str | None = None


settings = Settings()
