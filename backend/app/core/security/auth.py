from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
import secrets
import string
import logging
import hashlib

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=[settings.PASSWORD_HASH_SCHEME], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password for storing"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_EXPIRES_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
    return encoded_jwt

def generate_api_key(length: int = 32) -> str:
    """Generate a secure API key for devices"""
    alphabet = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return api_key

def hash_api_key(api_key: str) -> str:
    """Create a hash of an API key with server-side pepper"""
    peppered = api_key + settings.DEVICE_KEY_PEPPER
    return hashlib.sha256(peppered.encode()).hexdigest()

def verify_api_key(api_key: str, hashed_api_key: str) -> bool:
    """Verify an API key against its hash"""
    calculated_hash = hash_api_key(api_key)
    return secrets.compare_digest(calculated_hash, hashed_api_key)
