from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:kipkemoi@localhost:5432/course_db"
    SECRET_KEY: str = "PRODUCTION_SUPER_SECRET_ALGORITHM_KEY_DO_NOT_SHARE_TOKEN_HASH"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REDIS_URL: str = "redis://localhost:6379/0"


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
