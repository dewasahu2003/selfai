from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings for the application.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    TOKENIZER_PARALLELISM: str = "false"
    HUGGINGFACE_ACCESS_TOKEN: str | None = None

    COMET_API_KEY: str | None = None
    COMET_WORKSPACE: str | None = None
    COMET_PROJECT_NAME: str | None = None


settings = Settings()
