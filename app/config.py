from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "StudyBlossom API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str
    DATABASE_ECHO: bool = False

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 horas

    # API Keys
    GEMINI_API_KEY: str
    D_ID_API_KEY: str

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001"
    ]

    # Storage
    STORAGE_TYPE: str = "local"
    STORAGE_PATH: str = "./storage"

    # Limits
    MAX_FLASHCARDS_PER_TOPIC: int = 10
    MAX_QUIZ_QUESTIONS: int = 5
    MAX_CONVERSATION_HISTORY: int = 20

    # XP Map
    XP_MAP: dict = {
        "text": 5,
        "visual": 10,
        "audio": 5,
        "map": 15,
        "pomodoro": 20,
        "inspiration": 2,
        "research": 8,
        "explanation": 10,
        "elaboration": 15,
        "evaluation": 20,
        "voice-tutor": 25,
        "video": 15,
    }

    # Levels
    LEVELS: List[dict] = [
        {"level": 1, "xp_threshold": 0, "name": "Semilla", "stage": 1},
        {"level": 2, "xp_threshold": 50, "name": "Brote", "stage": 2},
        {"level": 3, "xp_threshold": 120, "name": "Tallo Joven", "stage": 3},
        {"level": 4, "xp_threshold": 250, "name": "Planta Fuerte", "stage": 4},
        {"level": 5, "xp_threshold": 500, "name": "Floración", "stage": 5},
        {"level": 6, "xp_threshold": 1000, "name": "Árbol Sabio", "stage": 6},
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()