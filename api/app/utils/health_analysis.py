from typing import List, Dict, Any
from datetime import datetime, timedelta
import numpy as np
from scipy import stats
from app.models.records import WeightRecord, MedicalVisit

def analyze_weight_trend(weight_records: List[WeightRecord]) -> Dict[str, Any]:
    """Detailed weight trend analysis"""
    if not weight_records:
        return {"status": "no_data"}
    
    weights = [r.weight for r in weight_records]
    dates = [r.date for r in weight_records]
    
    # 计算基本统计数据
    stats_data = {
        "mean": np.mean(weights),
        "std": np.std(weights),
        "trend": "stable"
    }
    
    # 计算趋势
    if len(weights) > 2:
        slope, _, r_value, p_value, _ = stats.linregress(
            range(len(weights)), weights
        )
        if p_value < 0.05:  # 统计显著性
            stats_data["trend"] = "increasing" if slope > 0 else "decreasing"
            stats_data["change_rate"] = slope
    
    return stats_data

def analyze_health_patterns(medical_records: List[MedicalVisit]) -> Dict[str, Any]:
    """Analyze health patterns and periodic issues"""
    if not medical_records:
        return {"status": "no_data"}
    
    # 症状频率分析
    symptom_freq = {}
    for record in medical_records:
        symptoms = record.symptoms.split(',')
        for symptom in symptoms:
            symptom = symptom.strip()
            symptom_freq[symptom] = symptom_freq.get(symptom, 0) + 1
    
    # 季节性分析
    seasonal_patterns = {
        'spring': [],
        'summer': [],
        'autumn': [],
        'winter': []
    }
    
    for record in medical_records:
        month = record.date.month
        if 3 <= month <= 5:
            seasonal_patterns['spring'].append(record)
        elif 6 <= month <= 8:
            seasonal_patterns['summer'].append(record)
        elif 9 <= month <= 11:
            seasonal_patterns['autumn'].append(record)
        else:
            seasonal_patterns['winter'].append(record)
    
    return {
        "common_symptoms": sorted(
            symptom_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5],
        "seasonal_patterns": {
            season: len(records)
            for season, records in seasonal_patterns.items()
        }
    } 