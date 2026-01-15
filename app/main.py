from datetime import date, datetime
from fastapi import FastAPI, Depends, HTTPException, Query, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from . import crud, models, schemas
from .database import engine, SessionLocal, Base
# from .crud import create_task, get_tasks
# from .models import Task
# from .schemas import TaskCreate, Task, TaskUpdate


templates = Jinja2Templates(directory="app/templates")

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ToDoApp API", description="App to structure everyday tasks")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    tasks = db.query(models.Task).order_by(models.Task.priority.desc(), models.Task.due_date).all()

    for task in tasks:
        task.is_overdue = task.due_date and task.due_date.date() < date.today() if task.due_date else False
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks, "today": date.today()})


# CRUD ENDPOINTS
@app.post("/tasks/", response_model=schemas.Task)
async def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task)


@app.get("/tasks/", response_model=list[schemas.Task])
async def get_tasks(db: Session = Depends(get_db),
                    skip: int = 0,
                    limit: int = 100,
                    completed: Optional[bool] = Query(None),
                    search: Optional[str] = Query(None),
                    min_priority: Optional[int] = Query(None)):
    query = db.query(models.Task)

    if completed is not None:
        query = query.filter(models.Task.completed == completed)
    if search:
        like = f"%{search}%"
        query = query.filter(
            models.Task.title.ilike(like) | models.Task.description.ilike(like)
        )
    if min_priority is not None:
        query = query.filter(models.Task.priority >= min_priority)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@app.get("/tasks/{task_id}", response_model=schemas.Task)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=schemas.Task)
async def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted"}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})

@app.post("/tasks/new")
async def add_task(title: str = Form(...),
                   priority: Optional[int] = Form(1),
                   description: Optional[str] = Form(None),
                   due_date: Optional[str] = Form(None),
                   db: Session = Depends(get_db)
                   ):
    
    task_data = schemas.TaskCreate(
        title=title,
        priority=priority,
        description=description,
        due_date=datetime.fromisoformat(due_date) if due_date else None
    )
    crud.create_task(db, task_data)
    return RedirectResponse(url="/", status_code=303)

@app.post("/tasks/{task_id}/delete")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/tasks/{task_id}/edit", response_class=HTMLResponse)
async def edit_form(task_id: int, request: Request, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("edit.html", {"request": request, "task": task})


@app.post("/tasks/{task_id}/update")
async def update_task_page(
    task_id: int,
    title: str = Form(...),
    priority: Optional[int] = Form(1),
    status: str = Form("pending"),
    description: Optional[str] = Form(None),
    due_date: Optional[str] = Form(None),
    completed: Optional[bool] = Form(False),
    db: Session = Depends(get_db)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        status_map = {"pending": False, "in-progress": None, "completed": True}
        task.title = title
        task.priority = priority
        task.description = description
        if due_date:
            task.due_date = datetime.fromisoformat(due_date + ":00") if due_date else None
        task.completed = status_map[status]
        db.commit()
    return RedirectResponse("/", status_code=303)


@app.post("/tasks/{task_id}/toggle")
async def toggle_task_status(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        task.completed = not task.completed
        db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.patch("/tasks/{task_id}/status")
async def update_status(task_id: int, status_data: dict, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    status_map = {
        "pending": False,
        "in-progress": None, 
        "completed": True
    }
    task.completed = status_map[status_data["status"]]
    db.commit()
    db.refresh(task)
    return {"message": "Status updated"}
