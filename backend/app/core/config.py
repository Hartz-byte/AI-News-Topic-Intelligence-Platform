from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    debug: bool = True

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    database_url: str = "sqlite:///./local.db"
    cache_dir: str = "./cache"
    qdrant_path: str = "./qdrant_db"
    qdrant_collection: str = "articles"

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    serper_api_key: str = ""

    pinecone_api_key: str = ""
    huggingface_token: str = ""

    trend_refresh_minutes: int = 30
    article_fetch_limit: int = 30
    log_level: str = "INFO"

@lru_cache
def get_settings() -> Settings:
    return Settings()
