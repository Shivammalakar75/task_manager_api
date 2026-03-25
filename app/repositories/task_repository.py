from math import ceil
from typing import Optional

from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session

from app.models.task_model import Task
from app.schemas.task_schema import TaskStatus, TaskPriority, TaskCreate, TaskUpdate, TaskListResponse


class TaskRepository:

    def _apply_filters(self, stmt, owner_id: int, status: Optional[TaskStatus], priority: Optional[TaskPriority]):
        stmt = stmt.where(Task.owner_id == owner_id)
        if status:
            stmt = stmt.where(Task.status == status.value)
        if priority:
            stmt = stmt.where(Task.priority == priority.value)
        return stmt

    def create(self, db: Session, data: TaskCreate, owner_id: int) -> Task:
        task = Task(
            title=data.title,
            description=data.description,
            status=data.status.value,
            priority=data.priority.value,
            due_date=data.due_date,
            owner_id=owner_id,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def get_all(
        self,
        db: Session,
        owner_id: int,
        page: int = 1,
        per_page: int = 10,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        search: Optional[str] = None,
    ) -> TaskListResponse:
        # Count query
        count_stmt = select(func.count()).select_from(Task)
        count_stmt = self._apply_filters(count_stmt, owner_id, status, priority)

        # Data query
        data_stmt = select(Task)
        data_stmt = self._apply_filters(data_stmt, owner_id, status, priority)

        if search:
            data_stmt = data_stmt.where(
                Task.title.ilike(f"%{search}%") | Task.description.ilike(f"%{search}%")
            )
            count_stmt = count_stmt.where(
                Task.title.ilike(f"%{search}%") | Task.description.ilike(f"%{search}%")
            )

        total = db.execute(count_stmt).scalar_one()

        tasks = (
            db.execute(
                data_stmt.order_by(Task.created_at.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            .scalars()
            .all()
        )

        return TaskListResponse(
            tasks=tasks,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=ceil(total / per_page) if total > 0 else 1,
        )

    def get_by_id(self, db: Session, task_id: int, owner_id: int) -> Optional[Task]:
        stmt = select(Task).where(Task.id == task_id, Task.owner_id == owner_id)
        return db.execute(stmt).scalar_one_or_none()

    def update(self, db: Session, task: Task, data: TaskUpdate) -> Task:
        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.status is not None:
            task.status = data.status.value
        if data.priority is not None:
            task.priority = data.priority.value
        if data.due_date is not None:
            task.due_date = data.due_date
        db.commit()
        db.refresh(task)
        return task

    def delete(self, db: Session, task: Task) -> None:
        db.delete(task)
        db.commit()

    def delete_all(
        self,
        db: Session,
        owner_id: int,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
    ) -> int:
        stmt = delete(Task).where(Task.owner_id == owner_id)
        if status:
            stmt = stmt.where(Task.status == status.value)
        if priority:
            stmt = stmt.where(Task.priority == priority.value)

        result = db.execute(stmt)
        db.commit()
        return result.rowcount


task_repo = TaskRepository()
