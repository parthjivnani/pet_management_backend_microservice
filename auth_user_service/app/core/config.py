import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(dotenv_path=find_dotenv(), override=True)


class Config:
    """Application configuration from environment."""
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "pet_management")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_DAYS: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "7"))
    SITE_URL: str = os.getenv("SITE_URL", "http://localhost:5173")


configs = Config()
