import pandas as pd
from typing import List
from io import BytesIO
from app.models.records import WeightRecord, MedicalVisit

def export_to_excel(records: List, record_type: str) -> BytesIO:
    """导出数据到Excel文件"""
    if record_type == "weight":
        df = pd.DataFrame([
            {
                "Date": r.date,
                "Weight": r.weight,
                "Notes": r.notes
            } for r in records
        ])
    elif record_type == "medical":
        df = pd.DataFrame([
            {
                "Date": r.date,
                "Symptoms": r.symptoms,
                "Diagnosis": r.diagnosis,
                "Treatment": r.treatment,
                "Follow-up Date": r.follow_up_date,
                "Notes": r.notes
            } for r in records
        ])
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=record_type.capitalize())
    
    return output 