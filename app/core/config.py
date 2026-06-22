from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # These hardcoded strings act as safe fallbacks for local machine testing ONLY
    DATABASE_URL: str = "postgresql://postgres:kipkemoi@localhost:5432/course_db"
    SECRET_KEY: str = "local_development_insecure_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REDIS_URL: str = "redis://localhost:6379/0"

    # Automatically loads local .env files if present, ignores extra cloud variables
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
