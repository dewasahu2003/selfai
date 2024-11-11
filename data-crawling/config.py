from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    MONGO_DB_HOST: str | None = None

    #  (
    #     "mongodb://mongo1:30001,mongo2:30002,mongo3:30003/?replicaSet=my-replica-set"
    # )

    MONGO_DB_NAME: str | None = None

    LINKEDIN_USERNAME: str | None = None
    LINKEDIN_PASSWORD: str | None = None


settings = Settings()
