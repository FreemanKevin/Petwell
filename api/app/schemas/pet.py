from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class PetBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    species: str
    gender: str
    breed: str | None = None

class PetCreate(PetBase):
    birth_date: datetime | None = None

class PetUpdate(PetBase):
    name: str | None = None
    status: str | None = None
    breed: str | None = None
    avatar_url: str | None = None

class PetResponse(PetBase):
    id: int
    status: str
    birth_date: datetime | None = None
    avatar_url: str | None = None
    created_at: datetime
    updated_at: datetime
    owner_id: int
