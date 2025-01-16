from .user import User
from .pet import Pet
from .record import WeightRecord, VaccineRecord

# 确保所有模型都被导入，这样 SQLAlchemy 可以正确设置关系
