import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "mock_key")
    TIKTOK_API_KEY: str = os.getenv("TIKTOK_API_KEY", "mock_key")
    FACEBOOK_ACCESS_TOKEN: str = os.getenv("FACEBOOK_ACCESS_TOKEN", "mock_key")
    YOUTUBE_CLIENT_SECRET: str = os.getenv("YOUTUBE_CLIENT_SECRET", "mock_key")
    TRUTHGPT_URL: str = os.getenv("TRUTHGPT_URL", "http://localhost:8000")

    # Bass Diffusion Model Defaults
    BASS_P: float = 0.03
    BASS_Q: float = 0.38
    
    # CLV Defaults
    CLV_MARGIN: float = 50.0
    CLV_RETENTION_RATE: float = 0.8
    CLV_DISCOUNT_RATE: float = 0.1

    # MMM Defaults
    MMM_DECAY_LAMBDA: float = 0.5
    MMM_SATURATION_ALPHA: float = 0.0001
    MMM_MAX_SALES_BETA: float = 50000

    # Vidale-Wolfe Defaults
    VW_RESPONSE_CONSTANT: float = 0.1
    VW_MARKET_POTENTIAL: float = 100000
    VW_DECAY_LAMBDA: float = 0.2

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
