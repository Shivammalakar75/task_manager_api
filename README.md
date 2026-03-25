# Task Manager REST API

FastAPI + SQLAlchemy 2.0 + MySQL (PyMySQL driver) + JWT

---

## Project Structure

```
task_manager_api/
├── main.py                          # FastAPI app entry point
├── requirements.txt
├── .env.example
└── app/
    ├── core/
    │   ├── config.py                # Settings (.env se load)
    │   ├── database.py              # SQLAlchemy engine, session, Base
    │   └── security.py             # JWT utils, password hashing, auth dependency
    │
    ├── models/                      # SQLAlchemy ORM models (DB tables)
    │   ├── user_model.py            # User table
    │   └── task_model.py            # Task table
    │
    ├── schemas/                     # Pydantic schemas (request/response validation)
    │   ├── user_schema.py
    │   ├── task_schema.py
    │   └── common.py
    │
    ├── repositories/                # DB operations (SQLAlchemy queries)
    │   ├── user_repository.py       # All user DB queries
    │   └── task_repository.py       # All task DB queries
    │
    ├── services/                    # Business logic
    │   ├── auth_service.py          # Auth logic (register, login, etc.)
    │   └── task_service.py          # Task logic (CRUD, filters)
    │
    └── routers/                     # HTTP endpoints (thin layer)
        ├── auth.py
        └── tasks.py
```

---

## Layer Responsibilities

| Layer        | Responsibility                                      |
|--------------|-----------------------------------------------------|
| `models`     | SQLAlchemy ORM — DB table structure define karna    |
| `schemas`    | Pydantic — HTTP request/response validate karna     |
| `repository` | SQLAlchemy queries — sirf DB se baat karna          |
| `service`    | Business logic — repository call karna              |
| `router`     | HTTP endpoints — service call karna, response dena  |

---

## Setup

```bash
# 1. Dependencies install karo
pip install -r requirements.txt

# 2. .env banao
cp .env.example .env
# DB_PASSWORD aur SECRET_KEY fill karo

# 3. Server chalao
uvicorn main:app --reload
```

Swagger: http://localhost:8000/docs

---

## API Endpoints

### Auth  `/api/v1/auth`

| Method | Endpoint           | Auth | Description                    |
|--------|--------------------|------|--------------------------------|
| POST   | `/register`        | No   | Register new user              |
| POST   | `/login`           | No   | Login → access + refresh token |
| POST   | `/refresh`         | No   | Get new access token           |
| GET    | `/me`              | Yes  | Get profile                    |
| PUT    | `/me`              | Yes  | Update name/email              |
| POST   | `/forgot-password` | No   | Get reset token                |
| POST   | `/reset-password`  | No   | Reset password with token      |
| DELETE | `/me`              | Yes  | Deactivate account             |

### Tasks  `/api/v1/tasks`

| Method | Endpoint      | Auth | Description                           |
|--------|---------------|------|---------------------------------------|
| POST   | `/`           | Yes  | Create task                           |
| GET    | `/`           | Yes  | List tasks (filter, search, paginate) |
| GET    | `/{task_id}`  | Yes  | Get single task                       |
| PUT    | `/{task_id}`  | Yes  | Update task                           |
| DELETE | `/{task_id}`  | Yes  | Delete single task                    |
| DELETE | `/`           | Yes  | Delete tasks (with filters)           |

### GET/DELETE /tasks Query Params

| Param      | Type   | Description                         |
|------------|--------|-------------------------------------|
| `status`   | string | pending / in_progress / completed   |
| `priority` | string | low / medium / high                 |
| `search`   | string | Title/description search (GET only) |
| `page`     | int    | Page number (GET only, default: 1)  |
| `per_page` | int    | Per page (GET only, default: 10)    |
