# Todo App

Full-stack task management app built with FastAPI, SQLAlchemy, and Bootstrap. Professional table UI with priority badges, status toggle, overdue detection, and timeline tracking.

## Features
- Full CRUD - Create, Read, Update, Delete tasks
- Timeline view - Start date (created_at) + Due date columns
- Priority badges - P1 (blue) to P5 (red)
- Status toggle - Pending ↔ Completed with badges
- Overdue detection - Red badge when past due date
- Responsive design - Works on mobile/desktop
- JSON API - Auto-generated docs at `/docs`

## Tech Stack
- Backend: FastAPI + SQLAlchemy + SQLite
- Frontend: Jinja2 + Bootstrap 5
- Database: SQLite (todo.db)


## Quick Start

1. Clone & Install
```bash
git clone <your-repo> todo-app
cd todo-app
pip install -r requirements.txt
```

2. Run: uvicorn app.main:app --reload

3. Open
- UI: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```bash
todo-app/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI routes
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # Database operations
│   └── templates/       # Jinja2 HTML
        └── base.html
        └── edit.html
│       └── index.html
├── requirements.txt
└── todo.db             # SQLite database
```

## Usage

- Add tasks with title, priority (1-5), description, due date
- Edit and Delete tasks, prorities and statuses
