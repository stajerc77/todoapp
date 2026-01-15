from datetime import datetime
from sqlalchemy.orm import Session
from . import models, schemas

def create_task(db: Session, task: schemas.TaskCreate):
    task_data = task.dict(exclude_unset=True)
    status_map = {
        "pending": False,
        "in-progress": None,
        "completed": True
    }

    db_task = models.Task(
        title=task_data["title"],
        priority=task_data["priority"],
        description=task_data.get("description"),
        due_date=task.due_date,
        completed=status_map.get(task.status, False)
        )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Task).offset(skip).limit(limit).all()
