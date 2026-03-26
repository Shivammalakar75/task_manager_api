from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_token, generate_reset_token,
)
from app.repositories.user_repository import user_repo
from app.schemas.user_schema import (
    UserRegister, UserLogin, UpdateProfileRequest,
    TokenResponse, AccessTokenResponse, UserOut,ChangePasswordRequest
)


class AuthService:

    def register(self, db: Session, data: UserRegister) -> dict:
        if user_repo.get_by_email(db, data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        user_repo.create(db, data.name, data.email, hash_password(data.password))
        return {"message": "User registered successfully"}

    def login(self, db: Session, data: UserLogin) -> TokenResponse:
        user = user_repo.get_by_email(db, data.email)

        if not user or not verify_password(data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        token_data = {"sub": str(user.id)}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
            user=UserOut.model_validate(user),
        )

    def refresh(self, db: Session, refresh_token: str) -> AccessTokenResponse:
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Provide a refresh token.",
            )

        user = user_repo.get_by_id(db, int(payload.get("sub")))

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or deactivated",
            )

        return AccessTokenResponse(
            access_token=create_access_token({"sub": str(user.id)})
        )

    def update_profile(self, db: Session, current_user, data: UpdateProfileRequest):
        updates = {}
        if data.name is not None:
            updates["name"] = data.name
        if data.email is not None:
            if user_repo.email_exists_for_other(db, data.email, current_user.id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already in use",
                )
            updates["email"] = data.email

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        return user_repo.update(db, current_user, **updates)

    def forgot_password(self, db: Session, email: str) -> dict:
        user = user_repo.get_by_email(db, email)

        if not user:
            return {"message": "If this email is registered, a reset link has been sent"}

        reset_token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
        user_repo.set_reset_token(db, user, reset_token, expires_at)

        return {"message": f"Password reset token (dev mode): {reset_token}"}

    def reset_password(self, db: Session, token: str, new_password: str) -> dict:
        user = user_repo.get_by_reset_token(db, token)

        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")

        parts = user.password.split("::")
        if len(parts) < 4:
            raise HTTPException(status_code=400, detail="Invalid reset token format")

        expires_at = datetime.strptime(parts[2], "%Y-%m-%d %H:%M:%S")

        if datetime.utcnow() > expires_at:
            user_repo.clear_reset_token_and_set_password(db, user, "::".join(parts[3:]))
            raise HTTPException(status_code=400, detail="Reset token has expired")

        user_repo.clear_reset_token_and_set_password(db, user, hash_password(new_password))
        return {"message": "Password reset successfully. You can now login."}
    

    def change_password(self, db: Session, current_user, data: ChangePasswordRequest) -> dict:
        user = user_repo.get_by_id(db, current_user.id)
        if not verify_password(data.old_password, user.password):
            raise HTTPException(status_code=400, detail="Old password is incorrect")
        user_repo.update_password(db, user, hash_password(data.new_password))
        return {"message": "Password changed successfully"}

    def deactivate(self, db: Session, current_user) -> dict:
        user_repo.deactivate(db, current_user)
        return {"message": "Account deactivated successfully"}


auth_service = AuthService()
