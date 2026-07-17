from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "supersecretkey123"
    DATABASE_URL: str = "sqlite:///./cinebook.db"
    SEAT_LOCK_MINUTES: int = 5
    APP_NAME: str = "CineBook"

    class Config:
        env_file = ".env"

settings = Settings()
