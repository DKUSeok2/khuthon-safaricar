from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "농산물 리뷰 분석 AI 서버"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "*",
    ]
    UPLOAD_DIRECTORY: str = "uploads"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB
    FIREBASE_DATABASE_URL: str = "https://khuton-default-rtdb.firebaseio.com"

settings = Settings() 