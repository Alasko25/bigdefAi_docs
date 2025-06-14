from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    LOGSTASH_HOST: str = "localhost:5045"  # Port TCP pour L
    DATABASE_URL: str = "postgresql+asyncpg://bdia_user:bdia_pass@localhost/bdia_db"
    SYNC_DATABASE_URL: str = "postgresql://bdia_user:bdia_pass@localhost/bdia_db"
    SECRET_KEY: str
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]


    # # ✅ MongoDB : URI complète avec base incluse (logs_db)
    # MONGODB_URI: str ="mongodb://localhost:27017/logs_db"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
