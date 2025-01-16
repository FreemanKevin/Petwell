from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# 体重记录
class WeightRecordBase(BaseModel):
    """Base schema for weight records"""
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

# 疫苗记录
class VaccineRecordBase(BaseModel):
    """Base schema for vaccination records"""
    model_config = ConfigDict(from_attributes=True)
    vaccine_name: str
    date: datetime
    batch_number: str | None = None
    next_due_date: datetime | None = None
    notes: str | None = None

class VaccineRecordCreate(VaccineRecordBase):
    pet_id: int

class VaccineRecordResponse(VaccineRecordBase):
    id: int
    pet_id: int

# 驱虫记录
class DewormingBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    date: datetime
    medicine_name: str
    dosage: str
    weight: float
    next_due_date: datetime | None = None
    notes: str | None = None

class DewormingCreate(DewormingBase):
    pet_id: int

class DewormingResponse(DewormingBase):
    id: int
    pet_id: int

# 就医记录
class MedicalVisitBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    date: datetime
    symptoms: str
    diagnosis: str | None = None
    treatment: str | None = None
    follow_up_date: datetime | None = None
    notes: str | None = None

class MedicalVisitCreate(MedicalVisitBase):
    pet_id: int

class MedicalVisitResponse(MedicalVisitBase):
    id: int
    pet_id: int

# 日常观察
class DailyObservationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    date: datetime
    description: str
    action_taken: str | None = None
    notes: str | None = None

class DailyObservationCreate(DailyObservationBase):
    pet_id: int

class DailyObservationResponse(DailyObservationBase):
    id: int
    pet_id: int
