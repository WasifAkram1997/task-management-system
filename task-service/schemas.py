"""
Pydantic schemas for request/response validation
Defines the API contract
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Literal
import uuid


# ============================================
# Task Schemas
# ============================================

class TaskBase(BaseModel):
    """Base task schema with common fields"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: Literal["TODO", "IN_PROGRESS", "DONE"] = "TODO"
    priority: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "MEDIUM"
    assigned_to: Optional[uuid.UUID] = None
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    """Schema for creating a task"""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[Literal["TODO", "IN_PROGRESS", "DONE"]] = None
    priority: Optional[Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]] = None
    assigned_to: Optional[uuid.UUID] = None
    due_date: Optional[datetime] = None


class TaskResponse(TaskBase):
    """Schema for task response"""
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Comment Schemas
# ============================================

class CommentCreate(BaseModel):
    """Schema for creating a comment"""
    content: str = Field(..., min_length=1)


class CommentResponse(BaseModel):
    """Schema for comment response"""
    id: uuid.UUID
    task_id: uuid.UUID
    user_id: uuid.UUID
    content: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Standard Response Schemas
# ============================================

class MessageResponse(BaseModel):
    """Standard message response"""
    message: str