# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # DATABASE URL (postgresql+psycopg2://user:pass@host:port/dbname)
    DATABASE_URL: str

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # llm / embedding
    SOLAR_API_KEY: str = "" 
    SOLAR_EMBEDDING_API_URL: str
    SOLAR_EMBEDDING_QUERY: str 
    SOLAR_EMBEDDING_PASSAGE: str
    EMBEDDING_DIMENSION: int

    # JWT Authentication Settings
    JWT_SECRET_KEY: str  
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24시간

    # Seoul Cultural Event API
    SEOUL_EVENT_BASE_URL: str
    SEOUL_EVENT_API_KEY: str   # 인증키
    SEOUL_EVENT_SERVICE: str = "culturalEventInfo"
    SEOUL_EVENT_TYPE: str = "json"
    SEOUL_EVENT_PAGE_SIZE: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
