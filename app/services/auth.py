from app.db.repos.user_repo import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.schema.auth_schema import RegisterUserSchema, UsernameLoginSchema, TokenSchema
from fastapi import HTTPException, status
from app.core.security import hash_password, verify_password, create_access_token


class UserService:
    def __init__(self, session: AsyncSession):
        self._user_repo = UserRepository(session=session)

    async def create(self, user_payload: RegisterUserSchema):

        # check if user already exists
        existing = await self._user_repo.get_by_email_or_username(
            username=user_payload.username, email=user_payload.email
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="username alreadyin use"
            )

        pwd_hash = hash_password(user_payload.password)

        user = user_payload.model_dump()
        del user["password"]
        user["password_hash"] = pwd_hash

        return await self._user_repo.create(**user)

    async def login(self,payload: UsernameLoginSchema)->TokenSchema:
        #check if user exists
        existing = await self._user_repo.get_by_username(username=payload.username)
        if not existing:
            raise HTTPException(
                status_code= status.HTTP_401_UNAUTHORIZED,
                detail="invalid user credentials"
            )
        valid_password = verify_password(payload.password,existing.password_hash)

        if not valid_password:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail= "invalid user credentials"
            )
        # now create access token
        token = create_access_token({
            "sub":existing.id
        })
        return TokenSchema(
            token=token,
            token_type="bearer"
        )

