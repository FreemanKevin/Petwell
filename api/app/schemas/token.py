from typing import Optional
from pydantic import BaseModel, ConfigDict

class Token(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None

class TokenData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: Optional[str] = None

class RefreshToken(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    refresh_token: str 