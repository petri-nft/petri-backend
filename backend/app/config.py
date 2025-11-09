from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/petri_db"
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External service URLs
    CARD_GENERATION_SERVICE_URL: str = "http://localhost:8001"
    HEALTH_SCORING_SERVICE_URL: str = "http://localhost:8002"
    
    # AI Service Keys (optional)
    GEMINI_API_KEY: str = ""
    GEMINI_API_SECRET: str = ""
    ELEVENLABS_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    
    # App settings
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields from .env


settings = Settings()
