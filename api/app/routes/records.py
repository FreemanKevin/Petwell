from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.pet import Pet
from app.models.records import (
    WeightRecord,
    VaccineRecord,
    Deworming,
    MedicalVisit,
    DailyObservation
)
from app.schemas.record import (
    WeightRecordCreate,
    WeightRecordResponse,
    VaccineRecordCreate,
    VaccineRecordResponse,
    DewormingCreate,
    DewormingResponse,
    MedicalVisitCreate,
    MedicalVisitResponse,
    DailyObservationCreate,
    DailyObservationResponse
)
from app.utils.health_analysis import analyze_weight_trend, analyze_health_patterns
from app.utils.visualization import create_weight_chart, create_health_summary_chart
from app.utils.export import export_to_excel
from app.utils.import_data import import_records_from_excel
from app.utils.prediction import predict_weight_trend

router = APIRouter(
    prefix="/records",
    tags=["records"],
)

# Basic Record Management APIs
@router.post("/weight", response_model=WeightRecordResponse)
async def create_weight_record(
    record: WeightRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new weight record"""
    pet = db.query(Pet).filter(
        Pet.id == record.pet_id,
        Pet.owner_id == current_user.id
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    db_record = WeightRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.post("/vaccine", response_model=VaccineRecordResponse)
async def create_vaccine_record(
    record: VaccineRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new vaccination record"""
    pet = db.query(Pet).filter(
        Pet.id == record.pet_id,
        Pet.owner_id == current_user.id
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    db_record = VaccineRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

# Advanced Analysis APIs
@router.get("/{pet_id}/analysis/weight")
async def analyze_pet_weight(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze pet weight trends"""
    pet = db.query(Pet).filter(
        Pet.id == pet_id,
        Pet.owner_id == current_user.id
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    weight_records = db.query(WeightRecord).filter(
        WeightRecord.pet_id == pet_id
    ).order_by(WeightRecord.date).all()
    
    return {
        "trend_analysis": analyze_weight_trend(weight_records),
        "chart_data": create_weight_chart(weight_records),
        "predictions": predict_weight_trend(weight_records)
    }

@router.get("/{pet_id}/analysis/health")
async def analyze_pet_health(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze overall pet health status"""
    pet = db.query(Pet).filter(
        Pet.id == pet_id,
        Pet.owner_id == current_user.id
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    medical_records = db.query(MedicalVisit).filter(
        MedicalVisit.pet_id == pet_id
    ).order_by(MedicalVisit.date).all()
    
    return {
        "health_patterns": analyze_health_patterns(medical_records),
        "summary_chart": create_health_summary_chart(medical_records)
    }

# Data Import/Export APIs
@router.post("/{pet_id}/import")
async def import_pet_records(
    pet_id: int,
    file: UploadFile = File(...),
    record_type: str = Query(..., description="Type of records to import (weight/medical)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import records from Excel file"""
    pet = db.query(Pet).filter(
        Pet.id == pet_id,
        Pet.owner_id == current_user.id
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    result = await import_records_from_excel(file, record_type, pet_id, db)
    return result

@router.get("/{pet_id}/export")
async def export_pet_records(
    pet_id: int,
    record_type: str = Query(..., description="Type of records to export (weight/medical/all)"),
    format: str = Query("excel", description="Export format (excel/csv)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export records"""
    pet = db.query(Pet).filter(
        Pet.id == pet_id,
        Pet.owner_id == current_user.id
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    if record_type == "weight":
        records = db.query(WeightRecord).filter(
            WeightRecord.pet_id == pet_id
        ).order_by(WeightRecord.date).all()
    elif record_type == "medical":
        records = db.query(MedicalVisit).filter(
            MedicalVisit.pet_id == pet_id
        ).order_by(MedicalVisit.date).all()
    else:
        raise HTTPException(status_code=400, detail="Invalid record type")
    
    return export_to_excel(records, record_type)

# Reminder APIs
@router.get("/{pet_id}/reminders")
async def get_pet_reminders(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reminders for a pet"""
    pet = db.query(Pet).filter(
        Pet.id == pet_id,
        Pet.owner_id == current_user.id
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    # Get various reminders
    vaccine_reminders = db.query(VaccineRecord).filter(
        VaccineRecord.pet_id == pet_id,
        VaccineRecord.next_due_date > datetime.utcnow()
    ).all()
    
    deworming_reminders = db.query(Deworming).filter(
        Deworming.pet_id == pet_id,
        Deworming.next_due_date > datetime.utcnow()
    ).all()
    
    medical_reminders = db.query(MedicalVisit).filter(
        MedicalVisit.pet_id == pet_id,
        MedicalVisit.follow_up_date > datetime.utcnow()
    ).all()
    
    return {
        "vaccine_reminders": vaccine_reminders,
        "deworming_reminders": deworming_reminders,
        "medical_reminders": medical_reminders
    }

# Batch Operation APIs
@router.post("/batch/import")
async def batch_import_records(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Batch import multiple record files"""
    results = []
    for file in files:
        try:
            result = await import_records_from_excel(
                file,
                record_type="auto",  # Auto-detect record type
                pet_id=None,  # Read pet_id from file
                db=db
            )
            results.append({"filename": file.filename, "status": "success", **result})
        except Exception as e:
            results.append({"filename": file.filename, "status": "error", "error": str(e)})
    
    return results

@router.get("/statistics/summary")
async def get_records_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary statistics for all pets' records"""
    pets = db.query(Pet).filter(Pet.owner_id == current_user.id).all()
    
    summary = []
    for pet in pets:
        weight_count = db.query(WeightRecord).filter(
            WeightRecord.pet_id == pet.id
        ).count()
        
        vaccine_count = db.query(VaccineRecord).filter(
            VaccineRecord.pet_id == pet.id
        ).count()
        
        medical_count = db.query(MedicalVisit).filter(
            MedicalVisit.pet_id == pet.id
        ).count()
        
        summary.append({
            "pet_id": pet.id,
            "pet_name": pet.name,
            "weight_records": weight_count,
            "vaccine_records": vaccine_count,
            "medical_records": medical_count
        })
    
    return summary 