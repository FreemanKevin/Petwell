from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class WeightRecordBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    weight: float
    date: datetime
    notes: str | None = None

class WeightRecordCreate(WeightRecordBase):
    pet_id: int
    date: datetime | None = None

class WeightRecordResponse(WeightRecordBase):
    id: int
    pet_id: int
    date: datetime

class VaccineRecordBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    vaccine_name: str
    date: datetime
    next_due_date: datetime | None = None
    notes: str | None = None

class VaccineRecordCreate(VaccineRecordBase):
    pet_id: int

class VaccineRecordResponse(VaccineRecordBase):
    id: int
    pet_id: int
