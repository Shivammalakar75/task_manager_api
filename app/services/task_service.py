from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.task_repository import task_repo
from app.schemas.task_schema import (
    TaskCreate, TaskUpdate, TaskListResponse,
    TaskStatus, TaskPriority,
)


class TaskService:

    def create(self, db: Session, data: TaskCreate, current_user) -> dict:
        return task_repo.create(db, data, current_user.id)

    def get_all(
        self,
        db: Session,
        current_user,
        page: int = 1,
        per_page: int = 10,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        search: Optional[str] = None,
    ) -> TaskListResponse:
        return task_repo.get_all(db, current_user.id, page, per_page, status, priority, search)

    def get_by_id(self, db: Session, task_id: int, current_user) -> dict:
        task = task_repo.get_by_id(db, task_id, current_user.id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    def update(self, db: Session, task_id: int, data: TaskUpdate, current_user) -> dict:
        task = self.get_by_id(db, task_id, current_user)
        return task_repo.update(db, task, data)

    def delete(self, db: Session, task_id: int, current_user) -> dict:
        task = self.get_by_id(db, task_id, current_user)
        task_repo.delete(db, task)
        return {"message": "Task deleted successfully"}

    def delete_all(
        self,
        db: Session,
        current_user,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
    ) -> dict:
        deleted_count = task_repo.delete_all(db, current_user.id, status, priority)

        filter_info = []
        if status:
            filter_info.append(f"status={status.value}")
        if priority:
            filter_info.append(f"priority={priority.value}")

        filter_str = f" ({', '.join(filter_info)})" if filter_info else ""
        return {"message": f"{deleted_count} task(s) deleted{filter_str}"}


task_service = TaskService()
