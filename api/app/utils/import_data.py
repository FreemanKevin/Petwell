import pandas as pd
from typing import List, Dict
from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models.records import WeightRecord, MedicalVisit

async def import_records_from_excel(
    file: UploadFile,
    record_type: str,
    pet_id: int,
    db: Session
) -> Dict[str, int]:
    """从Excel文件导入记录"""
    try:
        contents = await file.read()
        df = pd.read_excel(contents)
        
        records_created = 0
        records_updated = 0
        
        if record_type == "weight":
            for _, row in df.iterrows():
                try:
                    record = WeightRecord(
                        pet_id=pet_id,
                        date=pd.to_datetime(row['Date']),
                        weight=float(row['Weight']),
                        notes=str(row.get('Notes', ''))
                    )
                    db.add(record)
                    records_created += 1
                except Exception as e:
                    continue
                    
        elif record_type == "medical":
            for _, row in df.iterrows():
                try:
                    record = MedicalVisit(
                        pet_id=pet_id,
                        date=pd.to_datetime(row['Date']),
                        symptoms=str(row['Symptoms']),
                        diagnosis=str(row.get('Diagnosis', '')),
                        treatment=str(row.get('Treatment', '')),
                        follow_up_date=pd.to_datetime(row['Follow-up Date'])
                        if not pd.isna(row.get('Follow-up Date')) else None,
                        notes=str(row.get('Notes', ''))
                    )
                    db.add(record)
                    records_created += 1
                except Exception as e:
                    continue
        
        db.commit()
        return {
            "records_created": records_created,
            "records_updated": records_updated
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to import data: {str(e)}"
        ) 