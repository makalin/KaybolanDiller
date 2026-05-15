from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "KaybolanDiller API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api"
    debug: bool = False

    # When true, skip Hugging Face model downloads (tests / local dev)
    use_mock_translation: bool = True
    preload_models: bool = False
    default_model_cache: str = "./models/cache"

    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
    ]

    max_text_length: int = 5000
    max_batch_size: int = 32
    rate_limit_per_hour: int = 100

    # Optional API key (empty = auth disabled)
    api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
