from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth_schema import (
    AuthResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    UserProfileResponse,
)
from app.schemas.response import APIResponse
from app.services.auth_service import (
    authenticate_user,
    get_current_user,
    logout_user,
    refresh_user_tokens,
    register_user,
)


auth_router = APIRouter()


@auth_router.post(
    "/register/",
    response_model=APIResponse[AuthResponse],
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user, access_token, refresh_token = register_user(payload=payload, db=db)
    return APIResponse(
        success=True,
        message="Registration completed successfully",
        data=AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user,
        ),
        meta={},
    )


@auth_router.post("/login/", response_model=APIResponse[AuthResponse])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user, access_token, refresh_token = authenticate_user(payload=payload, db=db)
    return APIResponse(
        success=True,
        message="Login successful",
        data=AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user,
        ),
        meta={},
    )


@auth_router.post("/refresh-token/", response_model=APIResponse[AuthResponse])
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    user, access_token, refresh_token = refresh_user_tokens(payload=payload, db=db)
    return APIResponse(
        success=True,
        message="Token refreshed successfully",
        data=AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user,
        ),
        meta={},
    )


@auth_router.get("/me/", response_model=APIResponse[UserProfileResponse])
def me(user=Depends(get_current_user)):
    return APIResponse(
        success=True,
        message="Profile fetched successfully",
        data=user,
        meta={},
    )


@auth_router.post("/logout/", response_model=APIResponse[None])
def logout(_user=Depends(logout_user)):
    return APIResponse(
        success=True,
        message="Logout successful",
        data=None,
        meta={},
    )
