from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base

class WeightRecord(Base):
    """Weight record table"""
    __tablename__ = "weight_records"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"))
    weight = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(String)

    pet = relationship("Pet", back_populates="weight_records")

class VaccineRecord(Base):
    """Vaccination record table"""
    __tablename__ = "vaccine_records"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"))
    vaccine_name = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    batch_number = Column(String)
    next_due_date = Column(DateTime)
    notes = Column(String)

    pet = relationship("Pet", back_populates="vaccine_records")

class Deworming(Base):
    """Deworming record table"""
    __tablename__ = "dewormings"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"))
    date = Column(DateTime, nullable=False)
    medicine_name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    next_due_date = Column(DateTime)
    notes = Column(Text)
    
    pet = relationship("Pet", back_populates="deworming_records")

class MedicalVisit(Base):
    """Medical visit record table"""
    __tablename__ = "medical_visits"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"))
    date = Column(DateTime, nullable=False)
    symptoms = Column(Text, nullable=False)
    diagnosis = Column(Text)
    treatment = Column(Text)
    follow_up_date = Column(DateTime)
    notes = Column(Text)
    
    pet = relationship("Pet", back_populates="medical_records")

class DailyObservation(Base):
    """Daily observation table"""
    __tablename__ = "daily_observations"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"))
    date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=False)
    action_taken = Column(Text)
    notes = Column(Text)
    
    pet = relationship("Pet", back_populates="observations") 