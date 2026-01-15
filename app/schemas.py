from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 1
    completed: bool = False
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    title: str
    priority: int = 1
    status: str = "pending"
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None

class Task(TaskBase):
    id: int
    completed: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Replaces orm_mode
