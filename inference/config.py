from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    COMET_API_KEY: str | None = None
    COMET_WORKSPACE: str | None = None
    COMET_PROJECT: str | None = None

    # Embeddings config
    EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"

    # OpenAI
    OPENAI_MODEL_ID: str = "gpt-4-1106-preview"
    OPENAI_API_KEY: str | None = None

    # QdrantDB config
    QDRANT_DATABASE_HOST: str = "qdrant"  # or localhost if running outside Docker
    QDRANT_DATABASE_PORT: int = 6333
    USE_QDRANT_CLOUD: bool = (
        False  # if True, fill in QDRANT_CLOUD_URL and QDRANT_APIKEY
    )
    QDRANT_CLOUD_URL: str | None = None
    QDRANT_APIKEY: str | None = None

    MODEL_NAME: str | None = "mistralai/Mistral-7B-Instruct-v0.1"
    QWAK_DEPLOYMENT_MODEL_ID: str | None = "selfai"
    # RAG config
    TOP_K: int = 3
    KEEP_TOP_K: int = 3
    EXPAND_N_QUERY: int = 3


settings = Settings()
