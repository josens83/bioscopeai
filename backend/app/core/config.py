from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 기본 설정
    APP_NAME: str = "BioscopeAI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development, production
    DEBUG: bool = True
    SECRET_KEY: str

    # 데이터베이스
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 5

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OpenAI
    OPENAI_API_KEY: str

    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:19006"]

    # 파일 업로드
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "/tmp/uploads"

    # RAG 설정
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_DB_PATH: str = "/tmp/faiss_index"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # PubMed
    PUBMED_EMAIL: str
    PUBMED_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
