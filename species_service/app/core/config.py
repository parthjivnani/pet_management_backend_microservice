import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(dotenv_path=find_dotenv(), override=True)


class Config:
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "pet_management")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    AUTH_SERVICE_VALIDATE_URL: str = os.getenv("AUTH_SERVICE_VALIDATE_URL", "http://localhost:8080/api/auth/validate-token")
    


configs = Config()
