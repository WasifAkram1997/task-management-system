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
    description = Column(Text, nullable=True)
    status = Column(String(20), default="TODO", nullable=False)
    priority = Column(String(20), default="MEDIUM", nullable=False)

    created_by = Column(UUID(as_uuid=True), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), nullable=True)

    due_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to comments
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")


class Comment(Base):
    """Comment model for task comments"""
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to task
    task = relationship("Task", back_populates="comments")