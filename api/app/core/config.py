from typing import List
from pydantic_settings import BaseSettings
from datetime import timezone, timedelta

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PetWell API"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/petwell"
    
    # JWT
    JWT_SECRET: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # MinIO
    MINIO_HOST: str = "localhost"
    MINIO_PORT: int = 9000
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_USE_SSL: bool = False
    MINIO_BUCKET_NAME: str = "petwell"
    
    # Timezone
    TIMEZONE: timezone = timezone(timedelta(hours=8))  # 中国标准时间 UTC+8
    
    class Config:
        env_file = ".env"

settings = Settings()
