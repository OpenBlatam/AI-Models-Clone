"""Real settings"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Real application settings"""
    
    APP_NAME: str = "Real API"
    DEBUG: bool = True
    ENV: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings()
