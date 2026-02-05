"""
Task Service - FastAPI Application
Handles task and comment management
"""
from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import List, Optional
from database import get_db, init_db
from config import get_settings
from dependencies import get_current_user_id, get_current_user_email
from publisher import publish_notification
import models
import schemas
import uuid

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    init_db()
    yield
    # Shutdown (cleanup code would go here if needed)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Task management service with comments",
    lifespan=lifespan
)


# ============================================
# Health Check
# ============================================

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION
    }


# ============================================
# Task Endpoints
# ============================================

@app.post("/tasks", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: schemas.TaskCreate,
    request: Request,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new task"""
    new_task = models.Task(
        **task_data.model_dump(),
        created_by=current_user_id
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    user_email = get_current_user_email(request)

    #Now we publish the message
    publish_notification(
        notification_type="task_created",
        data={
            "task_id": str(new_task.id),
            "task_title": new_task.title,
            "user_email": user_email
        }
    )
    
    return new_task


@app.get("/tasks", response_model=List[schemas.TaskResponse])
def list_tasks(
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[uuid.UUID] = None,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """List tasks with optional filters"""
    query = db.query(models.Task)
    
    if status_filter:
        query = query.filter(models.Task.status == status_filter)
    if priority:
        query = query.filter(models.Task.priority == priority)
    if assigned_to:
        query = query.filter(models.Task.assigned_to == assigned_to)
    
    return query.all()


@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(
    task_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get a specific task by ID"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: uuid.UUID,
    task_data: schemas.TaskUpdate,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update a task"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update only provided fields
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    
    db.commit()
    db.refresh(task)
    
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a task"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db.delete(task)
    db.commit()


# ============================================
# Comment Endpoints
# ============================================

@app.post("/tasks/{task_id}/comments", response_model=schemas.CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(
    task_id: uuid.UUID,
    comment_data: schemas.CommentCreate,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Add a comment to a task"""
    # Verify task exists
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    new_comment = models.Comment(
        task_id=task_id,
        user_id=current_user_id,
        content=comment_data.content
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return new_comment


@app.get("/tasks/{task_id}/comments", response_model=List[schemas.CommentResponse])
def list_comments(
    task_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """List all comments for a task"""
    # Verify task exists
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task.comments