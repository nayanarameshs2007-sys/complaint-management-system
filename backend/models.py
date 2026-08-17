import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    complaint_id = Column(String(20), unique=True, index=True)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=False)
    image_path = Column(String(255), nullable=True)
    category = Column(String(100), nullable=False)
    priority = Column(String(20), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    department = Column(String(100), nullable=False)
    status = Column(String(50), default="Submitted")  # Submitted, Assigned, In Progress, Resolved
    duplicate_of = Column(String(20), nullable=True)  # References complaint_id if duplicate
    similarity_score = Column(Integer, nullable=True) # Percentage integer e.g. 85
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
