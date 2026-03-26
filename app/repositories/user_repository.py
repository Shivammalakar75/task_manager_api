from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_model import User


class UserRepository:

    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.get(User, user_id)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        return db.execute(stmt).scalar_one_or_none()

    def email_exists_for_other(self, db: Session, email: str, exclude_id: int) -> bool:
        stmt = select(User).where(User.email == email, User.id != exclude_id)
        return db.execute(stmt).scalar_one_or_none() is not None

    def create(self, db: Session, name: str, email: str, hashed_password: str) -> User:
        user = User(name=name, email=email, password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(self, db: Session, user: User, **fields) -> User:
        for key, value in fields.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    def deactivate(self, db: Session, user: User) -> User:
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user

    def set_reset_token(
        self,
        db: Session,
        user: User,
        reset_token: str,
        expires_at: datetime,
    ) -> None:
        # Store token inside password field temporarily:
        # Format → RESET::<token>::<expires>::<original_hash>
        user.password = f"RESET::{reset_token}::{expires_at.strftime('%Y-%m-%d %H:%M:%S')}::{user.password}"
        db.commit()

    def get_by_reset_token(self, db: Session, token: str) -> Optional[User]:
        stmt = select(User).where(User.password.like(f"RESET::{token}::%"))
        return db.execute(stmt).scalar_one_or_none()

    def clear_reset_token_and_set_password(
        self, db: Session, user: User, new_hashed_password: str
    ) -> None:
        user.password = new_hashed_password
        db.commit()

    def update_password(self, db: Session, user: User, new_hashed_password: str) -> None:
        user.password = new_hashed_password
        db.commit()


user_repo = UserRepository()
