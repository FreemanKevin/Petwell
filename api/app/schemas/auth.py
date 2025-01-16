from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    """Token schema"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data schema"""
    email: EmailStr | None = None

class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str 