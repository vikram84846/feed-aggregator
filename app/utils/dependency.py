from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db import get_async_session
from app.db.repos.user_repo import UserRepository
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import verify_access_token

oauth2_schema = OAuth2PasswordBearer("/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_schema),
    session: AsyncSession = Depends(get_async_session),
):
    """
    returns the current user object from the jwt token if valid
    Args: token -: jwt access token for user
    """
    user_repo = UserRepository(session)
    payload = verify_access_token(token=token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )
    return user
