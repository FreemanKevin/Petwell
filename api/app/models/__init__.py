from app.models.user import User
from app.models.pet import Pet
from app.models.records import (
    WeightRecord,
    VaccineRecord,
    Deworming,
    MedicalVisit,
    DailyObservation
)
from app.models.settings import (
    ReminderSettings,
    ReportTemplate,
    ReportTemplateVersion,
    SharedTemplate
)

# 确保所有模型都被导入，这样 SQLAlchemy 可以正确设置关系
