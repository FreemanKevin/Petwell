from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReportTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    template_type: str
    content: str
    is_default: bool = False

class ReportTemplateCreate(ReportTemplateBase):
    pass

class ReportTemplateUpdate(ReportTemplateBase):
    pass

class ReportTemplateResponse(ReportTemplateBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 

class TemplateVersionCreate(BaseModel):
    version: str
    content: str
    changelog: Optional[str] = None

class TemplateVersionResponse(TemplateVersionCreate):
    id: int
    template_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ShareTemplateRequest(BaseModel):
    user_id: int
    can_edit: bool = False

class SharedTemplateResponse(BaseModel):
    id: int
    template_id: int
    shared_with_id: int
    can_edit: bool
    created_at: datetime

    class Config:
        from_attributes = True 