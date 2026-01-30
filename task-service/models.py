from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from database import Base

class Task(Base):
    """Task model for task management"""
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default="TODO", nullable=False)
    priority = Column(String(20), default="MEDIUM", nullable=False)

    created_by = Column(UUID(as_uuid=True), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), nullable=False)
    
    due_date = Column(DateTime(timezone=True))