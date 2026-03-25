from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.task_schema import (
    TaskCreate, TaskUpdate, TaskOut, TaskListResponse,
    TaskStatus, TaskPriority,
)
from app.schemas.common import MessageResponse
from app.services.task_service import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskOut, status_code=201)
def create_task(
    data: TaskCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return task_service.create(db, data, current_user)


@router.get("/", response_model=TaskListResponse)
def get_tasks(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    search: Optional[str] = Query(None, max_length=100),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return task_service.get_all(db, current_user, page, per_page, status, priority, search)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return task_service.get_by_id(db, task_id, current_user)


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return task_service.update(db, task_id, data, current_user)


@router.delete("/{task_id}", response_model=MessageResponse)
def delete_task(
    task_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return task_service.delete(db, task_id, current_user)


@router.delete("/", response_model=MessageResponse)
def delete_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return task_service.delete_all(db, current_user, status, priority)
