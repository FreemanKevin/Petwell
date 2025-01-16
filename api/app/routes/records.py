from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.pet import Pet
from app.models.record import WeightRecord, VaccineRecord
from app.schemas.record import (
    WeightRecordCreate,
    WeightRecordResponse,
    VaccineRecordCreate,
    VaccineRecordResponse
)

router = APIRouter(
    prefix="/records",
    tags=["records"],
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "Record not found"}
    }
)

@router.post("/weight", response_model=WeightRecordResponse)
async def create_weight_record(
    record_in: WeightRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new weight record for a pet.
    
    Parameters:
    * **pet_id**: ID of the pet
    * **weight**: Weight in kilograms
    * **date**: Record date (optional, defaults to current time)
    * **notes**: Additional notes (optional)
    
    Returns created weight record.
    """
    # Verify pet ownership
    pet = db.query(Pet).filter(
        Pet.id == record_in.pet_id,
        Pet.owner_id == current_user.id
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    record = WeightRecord(**record_in.dict())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.get("/weight/{pet_id}", response_model=List[WeightRecordResponse])
async def list_weight_records(
    pet_id: int,
    skip: int = Query(0, description="Skip N items"),
    limit: int = Query(100, description="Limit response size"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get weight history for a specific pet.
    
    Parameters:
    * **pet_id**: ID of the pet
    * **skip**: Number of records to skip (pagination)
    * **limit**: Maximum number of records to return
    
    Returns list of weight records ordered by date (newest first).
    
    Raises:
    * **404**: Pet not found
    * **401**: Not authorized to access this pet
    """
    # Verify pet ownership
    pet = db.query(Pet).filter(
        Pet.id == pet_id,
        Pet.owner_id == current_user.id
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    records = db.query(WeightRecord).filter(
        WeightRecord.pet_id == pet_id
    ).order_by(WeightRecord.date.desc()).offset(skip).limit(limit).all()
    
    return records

@router.post("/vaccine", response_model=VaccineRecordResponse)
async def create_vaccine_record(
    record_in: VaccineRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new vaccination record.
    
    Parameters:
    * **pet_id**: ID of the pet
    * **vaccine_name**: Name of the vaccine
    * **date**: Vaccination date
    * **next_due_date**: Next vaccination due date (optional)
    * **notes**: Additional notes (optional)
    
    Returns created vaccination record.
    
    Raises:
    * **404**: Pet not found
    * **401**: Not authorized to add records for this pet
    """
    # Verify pet ownership
    pet = db.query(Pet).filter(
        Pet.id == record_in.pet_id,
        Pet.owner_id == current_user.id
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    record = VaccineRecord(**record_in.dict())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.get("/vaccine/{pet_id}", response_model=List[VaccineRecordResponse])
async def list_vaccine_records(
    pet_id: int,
    skip: int = Query(0, description="Skip N items"),
    limit: int = Query(100, description="Limit response size"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get vaccination history for a specific pet.
    
    Parameters:
    * **pet_id**: ID of the pet
    * **skip**: Number of records to skip (pagination)
    * **limit**: Maximum number of records to return
    
    Returns list of vaccination records ordered by date (newest first).
    
    Raises:
    * **404**: Pet not found
    * **401**: Not authorized to access this pet
    """
    # Verify pet ownership
    pet = db.query(Pet).filter(
        Pet.id == pet_id,
        Pet.owner_id == current_user.id
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    records = db.query(VaccineRecord).filter(
        VaccineRecord.pet_id == pet_id
    ).order_by(VaccineRecord.date.desc()).offset(skip).limit(limit).all()
    
    return records
