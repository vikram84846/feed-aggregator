"""
This modules defines auth routes for the app include following routes
    register
    login via username
"""

from fastapi import APIRouter, Depends, status
from app.db.db import get_async_session
from app.services.auth import UserService
from app.schema.auth_schema import (
    RegisterUserSchema,
    UsernameLoginSchema,
    UserResponseSchema,
    TokenSchema,
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="register new user for app",
)
async def register(
    payload: RegisterUserSchema, session: AsyncSession = Depends(get_async_session)
):
    """
    register route to create new user for the app
    Agrs:
        - payload : user register payload expected by route
        - session : async db session object
    """
    user_service = UserService(session)
    # use create service
    user = await user_service.create(user_payload=payload)
    return user


@router.post(
    "/login",
    response_model=TokenSchema,
    status_code=status.HTTP_200_OK,
    summary="log user into system via access_token",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    """
    logs user into the system and return access token required for authrozation
    Args:
        - payload : user login payload
        - session : async db session object
    """
    user_service = UserService(session)
    # login user
    payload = UsernameLoginSchema(
        username=form_data.username, password=form_data.password
    )
    token = await user_service.login(payload)
    return token
