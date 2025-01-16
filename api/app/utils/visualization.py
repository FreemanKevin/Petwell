import plotly.graph_objects as go
import plotly.express as px
from typing import List
import pandas as pd
from app.models.records import WeightRecord, MedicalVisit

def create_weight_chart(weight_records: List[WeightRecord]) -> dict:
    """创建体重变化图表"""
    df = pd.DataFrame([
        {
            "date": record.date,
            "weight": record.weight
        } for record in weight_records
    ])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['weight'],
        mode='lines+markers',
        name='Weight'
    ))
    
    # 添加移动平均线
    df['ma7'] = df['weight'].rolling(window=7).mean()
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['ma7'],
        mode='lines',
        name='7-day MA',
        line=dict(dash='dash')
    ))
    
    fig.update_layout(
        title="Weight Trend",
        xaxis_title="Date",
        yaxis_title="Weight (kg)"
    )
    
    return fig.to_dict()

def create_health_summary_chart(medical_records: List[MedicalVisit]) -> dict:
    """创建健康概况图表"""
    # 症状频率饼图
    symptom_counts = {}
    for record in medical_records:
        for symptom in record.symptoms.split(','):
            symptom = symptom.strip()
            symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1
    
    fig = px.pie(
        values=list(symptom_counts.values()),
        names=list(symptom_counts.keys()),
        title="Symptom Distribution"
    )
    
    return fig.to_dict() 