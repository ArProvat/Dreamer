
from pydantic_settings import BaseSettings
from typing import Any

class Settings(BaseSettings):
    GOOGLE_API_KEY: Any
    DATABASE_URL: str
    DATABASE_NAME: str
    COLLECTION_NAME: str
    COLLECTION_SESSION : str
    COLLECTION_NAME: str

    

    class Config:
        env_file = ".env"

settings = Settings()