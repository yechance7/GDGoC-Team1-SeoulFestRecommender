# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # DATABASE URL (postgresql+psycopg2://user:pass@host:port/dbname)
    DATABASE_URL: str

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Seoul Cultural Event API
    SEOUL_EVENT_BASE_URL: str 
    SEOUL_EVENT_API_KEY: str   # 인증키
    SEOUL_EVENT_SERVICE: str = "culturalEventInfo"
    SEOUL_EVENT_TYPE: str = "json"
    SEOUL_EVENT_PAGE_SIZE: int = 1000

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
