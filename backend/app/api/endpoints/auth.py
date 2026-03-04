from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any
from datetime import timedelta
from app.core.config import settings
from app.schemas.schemas import Token, User, UserCreate
from app.core.security.auth import verify_password, create_access_token
from app.core.security.deps import get_current_manager
from app.models.models import get_user_by_username, create_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = get_user_by_username(form_data.username)
    
    if not user:
        logger.warning(f"Login attempt with invalid username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user["password_hash"]):
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get("active", True):
        logger.warning(f"Login attempt for inactive user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRES_MINUTES)
    
    token_data = {
        "sub": user["user_id"],
        "role": user["role"]
    }
    
    if user.get("employee_id"):
        token_data["employee_id"] = user["employee_id"]
    
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    
    logger.info(f"Successful login for user: {form_data.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user["user_id"],
        "role": user["role"],
        "employee_id": user.get("employee_id"),
        "full_name": user.get("full_name"),
        "email": user.get("email")
    }

@router.post("/register", response_model=User)
async def register_user(user_data: UserCreate):
    """
    Create a new user account (self-registration for employees, manager required for other roles)
    """
    # Check if trying to register a non-employee role without manager auth
    if user_data.role != "employee":
        # For non-employee roles, we would need manager authentication
        # For now, we'll allow employee self-registration only
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employees can self-register. Contact administrator for other roles."
        )

    existing_user = get_user_by_username(user_data.username)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    return create_user(user_data)
