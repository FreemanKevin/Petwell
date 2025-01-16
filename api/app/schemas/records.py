from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# 驱虫记录
class DewormingBase(BaseModel):
    date: datetime
    medicine_name: str
    dosage: str
    weight: float
    next_due_date: Optional[datetime] = None
    notes: Optional[str] = None

class DewormingCreate(DewormingBase):
    pet_id: int

class DewormingResponse(DewormingBase):
    id: int
    pet_id: int

    class Config:
        from_attributes = True

# 就医记录
class MedicalVisitBase(BaseModel):
    date: datetime
    symptoms: str
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    notes: Optional[str] = None

class MedicalVisitCreate(MedicalVisitBase):
    pet_id: int

class MedicalVisitResponse(MedicalVisitBase):
    id: int
    pet_id: int

    class Config:
        from_attributes = True

# 日常观察
class DailyObservationBase(BaseModel):
    date: datetime
    description: str
    action_taken: Optional[str] = None
    notes: Optional[str] = None

class DailyObservationCreate(DailyObservationBase):
    pet_id: int

class DailyObservationResponse(DailyObservationBase):
    id: int
    pet_id: int

    class Config:
        from_attributes = True 