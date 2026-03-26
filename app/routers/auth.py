from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user_schema import (
    UserRegister, UserLogin, TokenResponse, RefreshTokenRequest,
    AccessTokenResponse, ForgotPasswordRequest, ResetPasswordRequest,
    UpdateProfileRequest, UserOut, ChangePasswordRequest
)
from app.schemas.common import MessageResponse
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=MessageResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    return auth_service.register(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    return auth_service.login(db, data)


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return auth_service.refresh(db, data.refresh_token)


@router.get("/me", response_model=UserOut)
def get_profile(current_user=Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_profile(
    data: UpdateProfileRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return auth_service.update_profile(db, current_user, data)


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return auth_service.forgot_password(db, data.email)


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    return auth_service.reset_password(db, data.token, data.new_password)


@router.put("/change-password", response_model=MessageResponse)
def change_password(
    data: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return auth_service.change_password(db, current_user, data)


@router.delete("/me", response_model=MessageResponse)
def deactivate_account(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return auth_service.deactivate(db, current_user)
