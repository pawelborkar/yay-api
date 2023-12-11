from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env_name: str = 'Local'
    base_url: str = 'http://localhost:8000'
    db_url: str = 'sqlite:///./shortener.db'
    origins: List[str] = ["http://localhost:1420", "http://localhost:3000", "https://yay.pawel.in", "https://https://yay-nhv8.onrender.com"]

    class Config:
        env = '.env'


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    print(f"Loading settings for: {settings.env_name}")
    return settings
