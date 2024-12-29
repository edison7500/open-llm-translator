from functools import lru_cache

from typing import Optional, Any
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Translator API"
    items_per_user: int = 50

    ollama_url: Optional[str] = None
    ollama_model: Optional[str] = None

    deepl_api_key: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_config() -> Settings:
    return Settings()


settings = get_config()
