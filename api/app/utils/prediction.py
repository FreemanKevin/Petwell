import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from typing import List, Tuple
from datetime import datetime, timedelta
from app.models.records import WeightRecord

def predict_weight_trend(
    weight_records: List[WeightRecord],
    days_ahead: int = 30
) -> List[Tuple[datetime, float]]:
    """预测未来体重趋势"""
    if len(weight_records) < 5:  # 需要足够的数据点
        return []
    
    # 准备数据
    dates = np.array([(r.date - weight_records[0].date).days for r in weight_records])
    weights = np.array([r.weight for r in weight_records])
    
    # 使用多项式回归
    poly = PolynomialFeatures(degree=2)
    X_poly = poly.fit_transform(dates.reshape(-1, 1))
    
    model = LinearRegression()
    model.fit(X_poly, weights)
    
    # 预测未来数据点
    future_dates = np.array(range(
        dates[-1] + 1,
        dates[-1] + days_ahead + 1
    ))
    future_X_poly = poly.transform(future_dates.reshape(-1, 1))
    predictions = model.predict(future_X_poly)
    
    # 转换回日期格式
    base_date = weight_records[0].date
    return [
        (base_date + timedelta(days=int(d)), float(p))
        for d, p in zip(future_dates, predictions)
    ] 