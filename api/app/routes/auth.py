from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError
from app.core.security import (
    verify_password,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_refresh_token
)
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token, RefreshToken
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"description": "Unauthorized"}}
)

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def authenticate_user(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Parameters:
    * **email**: Valid email address
    * **password**: Strong password
    * **full_name**: User's full name
    
    Returns registered user information.
    """
    # Check if email exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login to get access token.
    
    Parameters:
    * **username**: Email address
    * **password**: Account password
    
    Returns:
    * **access_token**: JWT token for API authentication
    * **token_type**: Token type (bearer)
    * **refresh_token**: Token for refreshing access token
    """
    # Validate user
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    # Create refresh token (longer expiration)
    refresh_token_expires = timedelta(days=30)  # 30天有效期
    refresh_token = create_access_token(
        data={"sub": str(user.id), "refresh": True},
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    token: RefreshToken,
    db: Session = Depends(get_db)
):
    """
    Refresh an expired access token.
    
    Parameters:
    * **refresh_token**: Valid refresh token from previous login
    
    Returns:
    * **access_token**: New JWT token for API authentication
    * **token_type**: Token type (bearer)
    * **refresh_token**: New refresh token
    """
    try:
        user_id = verify_refresh_token(token.refresh_token)
        user = get_user(db, int(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create new access token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Create new refresh token
        refresh_token_expires = timedelta(days=30)
        new_refresh_token = create_access_token(
            data={"sub": str(user.id), "refresh": True},
            expires_delta=refresh_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": new_refresh_token
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
