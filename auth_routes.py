from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from models.schemas import (
    UserSignup,
    UserLogin,
    Token,
    UserResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
)
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()
auth_service = AuthService()


# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Get current authenticated user"""
    token = credentials.credentials
    token_data = auth_service.verify_token(token, token_type="access")
    user = auth_service.get_user_by_id(token_data["user_id"])
    return user


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(user_data: UserSignup):
    """
    Register a new user

    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **full_name**: Optional full name
    """
    user = auth_service.create_user(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
    )

    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        is_active=user["is_active"],
        is_verified=user["is_verified"],
        created_at=user["created_at"],
    )


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """
    Login with email and password

    Returns JWT access token and refresh token
    """
    user = auth_service.authenticate_user(user_data.email, user_data.password)

    # Create tokens
    access_token = auth_service.create_access_token(
        data={"sub": user["email"], "user_id": user["id"]}
    )
    refresh_token = auth_service.create_refresh_token(
        data={"sub": user["email"], "user_id": user["id"]}
    )

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Refresh access token using refresh token
    """
    token = credentials.credentials
    token_data = auth_service.verify_token(token, token_type="refresh")

    # Create new access token
    access_token = auth_service.create_access_token(
        data={"sub": token_data["email"], "user_id": token_data["user_id"]}
    )

    # Create new refresh token
    refresh_token = auth_service.create_refresh_token(
        data={"sub": token_data["email"], "user_id": token_data["user_id"]}
    )

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


# @router.get("/me", response_model=UserResponse)
# async def get_current_user_info(
#     token_data: dict = Depends(get_current_user)
# ):
#     # Supabase client
#     result = supabase.table("users") \
#         .select("*") \
#         .eq("id", token_data["user_id"]) \
#         .single() \
#         .execute()

#     user = result.data

#     if not user:
#         raise HTTPException(status_code=401, detail="User not found")

#     return UserResponse(
#         id=user["id"],
#         email=user["email"],
#         full_name=user.get("full_name"),
#         is_active=user.get("is_active", True),
#         is_verified=user.get("is_verified", True),
#         created_at=user.get("created_at")
#     )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current logged-in user information
    """
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        is_active=current_user["is_active"],
        is_verified=current_user["is_verified"],
        created_at=current_user["created_at"],
    )


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """
    Request password reset

    Sends reset link to email if account exists
    """
    token = auth_service.create_password_reset_token(request.email)

    if token:
        # Send email
        auth_service.send_reset_email(request.email, token)

    # Always return success (don't reveal if email exists)
    return {
        "message": "If your email is registered, you will receive a password reset link"
    }


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """
    Reset password using reset token
    """
    auth_service.reset_password(request.token, request.new_password)

    return {"message": "Password reset successful"}


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest, current_user: dict = Depends(get_current_user)
):
    """
    Change password for logged-in user
    """
    auth_service.change_password(
        user_id=current_user["id"],
        old_password=request.old_password,
        new_password=request.new_password,
    )

    return {"message": "Password changed successfully"}
