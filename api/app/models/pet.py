from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    breed = Column(String)
    birth_date = Column(DateTime)
    status = Column(String, default="active")
    avatar_url = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="pets")
    weight_records = relationship("WeightRecord", back_populates="pet", cascade="all, delete-orphan")
    vaccine_records = relationship("VaccineRecord", back_populates="pet", cascade="all, delete-orphan")
    deworming_records = relationship("Deworming", back_populates="pet", cascade="all, delete")
    medical_records = relationship("MedicalVisit", back_populates="pet", cascade="all, delete")
    observations = relationship("DailyObservation", back_populates="pet", cascade="all, delete")
    reminder_settings = relationship("ReminderSettings", back_populates="pet", cascade="all, delete")
