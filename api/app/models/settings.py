from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class ReminderSettings(Base):
    """用户自定义提醒设置"""
    __tablename__ = "reminder_settings"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"))
    reminder_type = Column(String, nullable=False)  # vaccine, deworming, medical, weight
    days_before = Column(Integer, default=30)  # 提前多少天提醒
    notification_method = Column(String, default="app")  # app, email, both
    enabled = Column(Boolean, default=True)
    
    pet = relationship("Pet", back_populates="reminder_settings")

class ReportTemplate(Base):
    """报告模板"""
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    template_type = Column(String, nullable=False)  # html/markdown
    content = Column(Text, nullable=False)
    is_default = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="report_templates") 

    versions = relationship("ReportTemplateVersion", back_populates="template", cascade="all, delete")
    shared_with = relationship("SharedTemplate", cascade="all, delete")

class ReportTemplateVersion(Base):
    """报告模板版本"""
    __tablename__ = "report_template_versions"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("report_templates.id", ondelete="CASCADE"))
    version = Column(String, nullable=False)  # 语义化版本号
    content = Column(Text, nullable=False)
    changelog = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    template = relationship("ReportTemplate", back_populates="versions")

class SharedTemplate(Base):
    """共享的报告模板"""
    __tablename__ = "shared_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("report_templates.id", ondelete="CASCADE"))
    shared_with_id = Column(Integer, ForeignKey("users.id"))
    can_edit = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    template = relationship("ReportTemplate")
    shared_with = relationship("User") 