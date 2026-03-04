from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Move EMOTION_STRESS_MAP outside the Settings class (already done)
EMOTION_STRESS_MAP = {
    "happy": {"level": "Low", "min_confidence": 20},  # Temporarily lowered for testing
    "neutral": {"level": "Low", "min_confidence": 25},
    "sad": {"level": "Medium", "min_confidence": 30},
    "angry": {"level": "Medium", "min_confidence": 30},
    "fear": {"level": "High", "min_confidence": 35},
    "disgust": {"level": "High", "min_confidence": 35},
    "surprise": {"level": "Medium", "min_confidence": 30}
}

class Settings:
    # API Settings
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
    # MongoDB Settings
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
    DB_NAME: str = os.getenv("DB_NAME", "stress_sense_db")
    # JWT Settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "insecure_jwt_secret_change_this_in_production")
    JWT_EXPIRES_MINUTES: int = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))
    # Security Settings
    PASSWORD_HASH_SCHEME: str = os.getenv("PASSWORD_HASH_SCHEME", "bcrypt")
    DEVICE_KEY_PEPPER: str = os.getenv("DEVICE_KEY_PEPPER", "insecure_pepper_change_this_in_production")
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = []
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Stress level suggestions
    STRESS_SUGGESTIONS: dict = {
        "Low": [
            "Keep up the good mood! 😊",
            "Consider sharing your positive energy with others",
            "Take a moment to appreciate your current state"
        ],
        "Medium": [
            "Try a 3-minute breathing exercise",
            "Listen to calming music",
            "Take a short walk",
            "Practice mindfulness meditation"
        ],
        "High": [
            "Stop and take deep breaths",
            "Try progressive muscle relaxation",
            "Listen to guided meditation",
            "Consider talking to someone about your feelings",
            "Take a break and do something you enjoy"
        ]
    }
    
    # Redis Settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_USERNAME: Optional[str] = os.getenv("REDIS_USERNAME")
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_DECODE_RESPONSES: bool = os.getenv("REDIS_DECODE_RESPONSES", "False").lower() == "true"
    REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", "30"))  # seconds
    
    # Privacy Banner
    PRIVACY_BANNER: str = (
        "StressSense only stores processed stress data, not raw images or video. "
        "Data is kept for 12 months and anonymized thereafter."
    )
    
    def __init__(self):
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
        if allowed_origins:
            self.ALLOWED_ORIGINS = allowed_origins.split(",")

settings = Settings()
